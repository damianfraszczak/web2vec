from datetime import datetime, timedelta

from web2vec.extractors import (
    ssl_certification_features as ssl_certification_features,
)
from web2vec.extractors.ssl_certification_features import CertificateFeatures


def test_certificate_temporal_and_issuer_indicators_active():
    """Confirm SSL features produce issuer flags and validity windows."""
    now = datetime.utcnow()
    not_before = now - timedelta(days=30)
    not_after = now + timedelta(days=10)
    features = CertificateFeatures(
        subject={"CN": "example.com"},
        issuer={"organizationName": "Let's Encrypt", "commonName": "R3"},
        not_before=not_before,
        not_after=not_after,
        is_valid=True,
        validity_message="Certificate is valid",
        is_trusted=True,
        trust_message="Certificate is signed by a trusted CA",
    )

    assert features.validity_duration_days == (not_after - not_before).days
    assert features.is_expired is False
    assert features.expires_within_7_days is False
    assert features.expires_within_30_days is True
    assert features.valid_in_7_days is True
    assert features.valid_in_30_days is False
    assert (
        features.days_until_expiration is not None
        and features.days_until_expiration >= 9
    )
    assert features.issuer_common_name == "R3"
    assert features.issuer_organization_name == "Let's Encrypt"
    assert features.issuer_is_lets_encrypt is True
    assert features.issuer_is_free_ca is True


def test_certificate_missing_window_sets_none():
    """Ensure sentinel certificates yield None for derived issuer flags."""
    features = CertificateFeatures(
        subject={},
        issuer={},
        not_before=datetime.min,
        not_after=datetime.min,
        is_valid=False,
        validity_message="No certificate found",
        is_trusted=False,
        trust_message="No certificate found",
    )

    assert features.validity_duration_days is None
    assert features.days_until_expiration is None
    assert features.expires_within_7_days is None
    assert features.valid_in_7_days is None
    assert features.is_expired is None
    assert features.issuer_common_name is None
    assert features.issuer_is_lets_encrypt is None
    assert features.issuer_is_free_ca is None


def test_is_certificate_valid_checks_window():
    """Validate the standalone validity helper for passing/failing windows."""
    now = datetime.utcnow()
    cert = {
        "notBefore": (now - timedelta(days=1)).strftime("%b %d %H:%M:%S %Y GMT"),
        "notAfter": (now + timedelta(days=1)).strftime("%b %d %H:%M:%S %Y GMT"),
    }
    assert ssl_certification_features.is_certificate_valid(cert)[0] is True

    expired_cert = {
        "notBefore": (now - timedelta(days=2)).strftime("%b %d %H:%M:%S %Y GMT"),
        "notAfter": (now - timedelta(days=1)).strftime("%b %d %H:%M:%S %Y GMT"),
    }
    assert ssl_certification_features.is_certificate_valid(expired_cert)[0] is False


def test_get_certificate_features_with_stub(monkeypatch):
    """Cover get_certificate_features by patching the TLS retrieval path."""
    now = datetime.utcnow()
    cert_payload = {
        "subject": {"commonName": "example.com"},
        "issuer": {"organizationName": "ZeroSSL", "commonName": "ZeroSSL RSA"},
        "notBefore": now.strftime("%b %d %H:%M:%S %Y GMT"),
        "notAfter": (now + timedelta(days=40)).strftime("%b %d %H:%M:%S %Y GMT"),
    }

    monkeypatch.setattr(
        ssl_certification_features, "get_tls_certificate", lambda host: cert_payload
    )
    monkeypatch.setattr(
        ssl_certification_features,
        "is_certificate_trusted",
        lambda cert: (True, "trusted"),
    )

    features = ssl_certification_features.get_certificate_features("example.com")
    assert features.issuer_is_free_ca is True
    assert features.validity_duration_days == 40
    assert features.valid_in_30_days is True


def test_check_ssl_handles_errors(monkeypatch):
    """Exercise the SSL check helper in both success and failure modes."""
    monkeypatch.setattr(
        ssl_certification_features.requests, "get", lambda *args, **kwargs: None
    )
    assert ssl_certification_features.check_ssl("https://example.com") is True

    def raising_get(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(ssl_certification_features.requests, "get", raising_get)
    assert ssl_certification_features.check_ssl("https://example.com") is False


def test_certificate_flatten_handles_tuple_issuer():
    """Ensure tuple-based issuer structures are flattened correctly."""
    now = datetime.utcnow()
    issuer_tuple = ((("organizationName", "CertOrg"), ("commonName", "CertCN")),)
    features = CertificateFeatures(
        subject={},
        issuer=issuer_tuple,
        not_before=now - timedelta(days=5),
        not_after=now + timedelta(days=5),
        is_valid=True,
        validity_message="",
        is_trusted=True,
        trust_message="",
    )
    assert features.issuer_common_name == "CertCN"
    assert features.issuer_organization_name == "CertOrg"
