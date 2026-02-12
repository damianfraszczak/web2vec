from types import SimpleNamespace

from web2vec.extractors import dns_features as dns_module
from web2vec.extractors.dns_features import DNSFeatures, DNSRecordFeatures


def test_dns_ttl_derived_flags():
    """Ensure TTL-based features flag the shortest TTL correctly."""
    records = [
        DNSRecordFeatures("A", 400, ["192.0.2.1"]),
        DNSRecordFeatures("AAAA", 7200, ["2001:db8::1"]),
    ]
    features = DNSFeatures(domain="example.com", records=records)
    features.compute_derived_features()

    assert features.min_ttl == 400
    assert features.ttl_expires_within_hour is True
    assert features.ttl_expires_within_day is True
    assert features.ttl_expires_within_week is True
    assert features.extract_ttl == 400


def test_dns_ttl_absent_flags_none():
    """Ensure derived TTL flags remain None when no records exist."""
    features = DNSFeatures(domain="example.com", records=[])
    features.compute_derived_features()

    assert features.min_ttl is None
    assert features.ttl_expires_within_hour is None
    assert features.ttl_expires_within_day is None
    assert features.ttl_expires_within_week is None
    assert features.extract_ttl is None


def test_get_dns_features_collects_records(monkeypatch):
    """Patch dns.resolver to exercise the network fetch logic."""

    class DummyRdata:
        def __init__(self, text):
            self._text = text

        def to_text(self):
            """Return the stored record text."""
            return self._text

    class FakeAnswers(list):
        def __init__(self, values, ttl):
            super().__init__([DummyRdata(value) for value in values])
            self.rrset = SimpleNamespace(ttl=ttl)

    def fake_resolve(domain, record_type):
        if record_type == "A":
            return FakeAnswers(["1.2.3.4"], 120)
        raise dns_module.dns.resolver.NoAnswer("no data")

    monkeypatch.setattr(dns_module.dns.resolver, "resolve", fake_resolve)
    features = dns_module.get_dns_features("example.com")
    assert features.records[0].values == ["1.2.3.4"]
    assert features.min_ttl == 120
