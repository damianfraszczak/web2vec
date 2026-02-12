from web2vec.extractors import url_geo_features as geo_features


def test_url_geo_features_monkeypatched(monkeypatch):
    """Ensure URL geo extractor returns patched ASN and country data."""
    monkeypatch.setattr(geo_features, "get_ip_from_url", lambda url: "1.1.1.1")
    monkeypatch.setattr(geo_features, "get_country", lambda ip: "US")
    monkeypatch.setattr(geo_features, "get_asn", lambda ip: 13335)

    features = geo_features.get_url_geo_features("https://example.com")

    assert features.url == "https://example.com"
    assert features.country_code == "US"
    assert features.asn == 13335
