import socket
import ssl
from dataclasses import dataclass
from datetime import datetime
from functools import cache
from typing import Any, Dict, Tuple

import idna
import requests

from web2vec.config import config


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


def get_tls_certificate(hostname: str, port: int = 443) -> Dict[str, Any]:
    """Retrieve the TLS certificate for a given hostname and port."""
    context = ssl.create_default_context()

    hostname_idna = idna.encode(hostname).decode("ascii")

    with socket.create_connection((hostname_idna, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname_idna) as ssock:
            cert = ssock.getpeercert()
            return cert


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
