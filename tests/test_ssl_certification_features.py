from datetime import datetime, timedelta

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
