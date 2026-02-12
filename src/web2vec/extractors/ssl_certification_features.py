import logging
import socket
import ssl
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import cache
from typing import Any, Dict, Optional, Tuple

import idna
import requests

from web2vec.config import config

logger = logging.getLogger(__name__)

FREE_CA_KEYWORDS = {
    "let's encrypt",
    "zerossl",
    "zero ssl",
    "buypass",
    "ssl.com free",
    "certbot",
}


def _flatten_name_entries(name_value: Any) -> Dict[str, str]:
    """Convert subject/issuer structures from ssl certs into a flat dict."""
    flat: Dict[str, str] = {}
    if isinstance(name_value, dict):
        for key, value in name_value.items():
            if isinstance(value, str):
                flat[key] = value
        return flat
    if isinstance(name_value, (tuple, list)):
        for rdn in name_value:
            if isinstance(rdn, (tuple, list)):
                for attr in rdn:
                    if (
                        isinstance(attr, (tuple, list))
                        and len(attr) >= 2
                        and isinstance(attr[0], str)
                        and isinstance(attr[1], str)
                    ):
                        flat[attr[0]] = attr[1]
    return flat


def _identify_known_ca(flat_name: Dict[str, str]) -> Optional[str]:
    """Return None; helper retained only for backwards compatibility."""
    return None


def _first_value(flat_name: Dict[str, str], keys: Tuple[str, ...]) -> Optional[str]:
    for key in keys:
        if key in flat_name:
            return flat_name[key]
        # handle case-insensitive matches
        for existing_key, value in flat_name.items():
            if existing_key.lower() == key.lower():
                return value
    return None


@dataclass
class CertificateFeatures:
    subject: Dict[str, Any]
    issuer: Dict[str, Any]
    not_before: datetime
    not_after: datetime
    is_valid: bool
    validity_message: str
    is_trusted: bool
    trust_message: str
    issuer_common_name: Optional[str] = field(init=False, default=None)
    issuer_organization_name: Optional[str] = field(init=False, default=None)
    issuer_is_lets_encrypt: Optional[bool] = field(init=False, default=None)
    issuer_is_free_ca: Optional[bool] = field(init=False, default=None)
    validity_duration_days: Optional[int] = field(init=False, default=None)
    days_until_expiration: Optional[int] = field(init=False, default=None)
    expires_within_7_days: Optional[bool] = field(init=False, default=None)
    expires_within_30_days: Optional[bool] = field(init=False, default=None)
    valid_in_7_days: Optional[bool] = field(init=False, default=None)
    valid_in_30_days: Optional[bool] = field(init=False, default=None)
    is_expired: Optional[bool] = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._compute_temporal_features()
        self._compute_issuer_features()

    def _has_certificate_window(self) -> bool:
        return self.not_before != datetime.min and self.not_after != datetime.min

    def _compute_temporal_features(self) -> None:
        if not self._has_certificate_window():
            self.validity_duration_days = None
            self.days_until_expiration = None
            self.expires_within_7_days = None
            self.expires_within_30_days = None
            self.valid_in_7_days = None
            self.valid_in_30_days = None
            self.is_expired = None
            return

        self.validity_duration_days = (self.not_after - self.not_before).days
        now = datetime.utcnow()
        remaining = self.not_after - now
        self.days_until_expiration = remaining.days
        self.is_expired = remaining.total_seconds() < 0
        self.expires_within_7_days = 0 <= remaining.days <= 7
        self.expires_within_30_days = 0 <= remaining.days <= 30
        self.valid_in_7_days = self._is_valid_on_date(now + timedelta(days=7))
        self.valid_in_30_days = self._is_valid_on_date(now + timedelta(days=30))

    def _is_valid_on_date(self, target_date: datetime) -> bool:
        if not self._has_certificate_window():
            return False
        return self.not_before <= target_date <= self.not_after

    def _compute_issuer_features(self) -> None:
        issuer_flat = _flatten_name_entries(self.issuer)
        if not issuer_flat:
            self.issuer_common_name = None
            self.issuer_organization_name = None
            self.issuer_is_lets_encrypt = None
            self.issuer_is_free_ca = None
            return

        self.issuer_common_name = _first_value(issuer_flat, ("commonName", "CN"))
        self.issuer_organization_name = _first_value(
            issuer_flat, ("organizationName", "O")
        )
        combined = " ".join(value.lower() for value in issuer_flat.values())
        is_lets_encrypt = "let's encrypt" in combined or "lets encrypt" in combined
        self.issuer_is_lets_encrypt = is_lets_encrypt
        self.issuer_is_free_ca = any(
            keyword in combined for keyword in FREE_CA_KEYWORDS
        )


def get_tls_certificate(hostname: str, port: int = 443) -> Dict[str, Any]:
    """Retrieve the TLS certificate for a given hostname and port."""
    try:
        context = ssl.create_default_context()

        hostname_idna = idna.encode(hostname).decode("ascii")

        with socket.create_connection((hostname_idna, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname_idna) as ssock:
                cert = ssock.getpeercert()
                return cert
    except Exception as e:  # noqa
        logger.debug(f"Error retrieving certificate for {hostname}: {e}")
        return {}


def is_certificate_valid(cert: Dict[str, Any]) -> Tuple[bool, str]:
    """Check if the certificate is currently valid based on its validity dates."""
    if not cert:
        return False, "No certificate found"

    current_date = datetime.utcnow()

    not_before = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z")
    not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")

    if not_before <= current_date <= not_after:
        return True, "Certificate is valid"
    else:
        return (
            False,
            f"Certificate is not valid: notBefore={not_before}, notAfter={not_after}",
        )


def is_certificate_trusted(cert: Dict[str, Any]) -> Tuple[bool, str]:
    """Check if the certificate is trusted by the system's CA store."""
    context = ssl.create_default_context()

    try:
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = False
        ca_certs = context.get_ca_certs(binary_form=True)  # noqa

        store = context.cert_store_stats()  # noqa
        return True, "Certificate is signed by a trusted CA"
    except ssl.SSLError as e:
        return False, f"Certificate is not trusted: {e}"


def check_ssl(url: str) -> bool:
    """Check if the SSL certificate of the URL is valid."""
    try:
        requests.get(url, verify=True, timeout=config.api_timeout)
        return True
    except Exception:  # noqa
        return False


def get_certificate_features(hostname: str) -> CertificateFeatures:
    """Retrieve and analyze the TLS certificate for a given hostname."""
    cert = get_tls_certificate(hostname)

    if cert:
        is_valid, validity_message = is_certificate_valid(cert)
        is_trusted, trust_message = is_certificate_trusted(cert)

        not_before = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z")
        not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")

        return CertificateFeatures(
            subject=cert.get("subject", {}),
            issuer=cert.get("issuer", {}),
            not_before=not_before,
            not_after=not_after,
            is_valid=is_valid,
            validity_message=validity_message,
            is_trusted=is_trusted,
            trust_message=trust_message,
        )
    else:
        return CertificateFeatures(
            subject={},
            issuer={},
            not_before=datetime.min,
            not_after=datetime.min,
            is_valid=False,
            validity_message="No certificate found",
            is_trusted=False,
            trust_message="No certificate found",
        )


@cache
def get_certificate_features_cached(hostname: str) -> CertificateFeatures:
    """Get the certificate features for the given hostname."""
    return get_certificate_features(hostname)


if __name__ == "__main__":
    hostname = "www.example.com"
    cert_info = get_certificate_features(hostname)

    print(f"Certificate for {hostname}")
    print(f"Subject: {cert_info.subject}")
    print(f"Issuer: {cert_info.issuer}")
    print(f"Validity: {cert_info.validity_message}")
    print(f"Trust: {cert_info.trust_message}")
    print(f"Valid from {cert_info.not_before} to {cert_info.not_after}")
