from datetime import datetime, timedelta

from web2vec.extractors.whois_features import WhoisFeatures


def _make_whois(**overrides):
    defaults = dict(
        domain_name=["example.com"],
        registrar=None,
        whois_server=None,
        referral_url=None,
        updated_date=None,
        creation_date=None,
        expiration_date=None,
        name_servers=[],
        status=[],
        emails=[],
        dnssec=None,
        name=None,
        org=None,
        address=None,
        city=None,
        state=None,
        zipcode=None,
        country=None,
    )
    defaults.update(overrides)
    return WhoisFeatures(**defaults)


def test_whois_recent_domain_indicators():
    """Check derived WHOIS flags for a recently created domain."""
    now = datetime.utcnow()
    creation = now - timedelta(days=10, hours=2)
    expiration = now + timedelta(days=6, hours=2)
    features = _make_whois(creation_date=creation, expiration_date=expiration)

    assert features.domain_age_days is not None and features.domain_age_days >= 10
    assert features.created_within_30_days is True
    assert features.created_within_365_days is True
    assert (
        features.days_until_expiration is not None
        and features.days_until_expiration >= 6
    )
    assert features.expires_within_7_days is True
    assert features.expires_within_30_days is True
    assert features.is_expired is False
    assert features.domain_age == features.domain_age_days


def test_whois_expired_domain_indicators_from_strings():
    """Verify string dates yield expired-domain flags when appropriate."""
    now = datetime.utcnow()
    creation_str = (now - timedelta(days=800)).strftime("%Y-%m-%d")
    expiration_str = (now - timedelta(days=5)).strftime("%Y-%m-%d")
    features = _make_whois(
        creation_date=creation_str,
        expiration_date=expiration_str,
    )

    assert features.domain_age_days is not None and features.domain_age_days >= 800
    assert features.created_within_365_days is False
    assert (
        features.days_until_expiration is not None
        and features.days_until_expiration < 0
    )
    assert features.expires_within_7_days is False
    assert features.expires_within_30_days is False
    assert features.is_expired is True
