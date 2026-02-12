from datetime import datetime, timedelta

from web2vec.extractors import whois_features as whois_features_module
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


def test_get_whois_features_parses_response(monkeypatch):
    """Patch the whois client to return a predictable response payload."""

    class FakeWhois:
        domain_name = "example.com"
        registrar = "Registrar"
        whois_server = "whois.example.com"
        referral_url = None
        updated_date = datetime.utcnow()
        creation_date = datetime.utcnow()
        expiration_date = datetime.utcnow()
        name_servers = "ns1.example.com"
        status = "active"
        emails = "admin@example.com"
        dnssec = None
        name = "Example"
        org = "Example Org"
        address = "Street"
        city = "City"
        state = "State"
        zipcode = "00000"
        country = "Country"

    monkeypatch.setattr(
        whois_features_module.whois, "whois", lambda domain: FakeWhois()
    )
    features = whois_features_module.get_whois_features("example.com")
    assert isinstance(features, WhoisFeatures)
    assert features.domain_name == ["example.com"]
    assert features.name_servers == ["ns1.example.com"]
    assert features.status == ["active"]


def test_normalize_datetime_from_list():
    """Ensure list-based timestamps normalize to the first valid entry."""
    now = datetime.utcnow()
    future = now + timedelta(days=30)
    features = _make_whois(creation_date=[now], expiration_date=[future])
    assert features.creation_datetime == now
    assert features.expiration_datetime == future
