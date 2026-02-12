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
