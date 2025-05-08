from web2vec.extractors.external_api.google_index_features import (
    get_google_index_features,
)


def test_real_api_wppl():
    url = "wp.pl"
    result = get_google_index_features(url)
    print(f"Is {url} indexed by Brave? {result.is_indexed}")
    if result.is_indexed:
        print(f"Position in search results: {result.position}")
    assert result.is_indexed is not None
