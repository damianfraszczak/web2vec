import pytest

from web2vec.extractors import url_lexical_features as lexical


@pytest.fixture(autouse=True)
def patch_shortening_services(monkeypatch):
    """Mock the shortening-service list to a static sample."""
    monkeypatch.setattr(
        lexical,
        "fetch_file_from_url_and_read",
        lambda url: "short.ly\nbit.ly\n",
    )


def test_url_lexical_feature_flags():
    """Validate lexical metrics and shortening detection for IP URLs."""
    url = "https://192.168.0.1/path/to/file.html?foo=bar&short.ly=1"
    features = lexical.get_url_lexical_features(url)

    assert features.is_ip is True
    assert features.url_length == len(url)
    assert features.url_depth == 3
    assert features.domain_contains_keywords is False
    assert features.uses_shortening_service is not None
    assert features.count_slash_url >= 3
    assert features.domain_entropy > 0
    assert features.number_of_parameters == 2
