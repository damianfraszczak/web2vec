from unittest.mock import Mock

import pytest

from web2vec.extractors.external_api import open_pagerank_features
from web2vec.extractors.external_api.open_pagerank_features import (
    MAX_DOMAINS_PER_REQUEST,
    OPEN_PAGE_RANK_API_URL,
    OpenPageRankAPI,
    OpenPageRankFeatures,
)

FOUND_RESULT = {
    "domain": "github.com",
    "found": True,
    "open_page_rank": 9.21,
    "rank": 42,
    "referring_domains": 1234567,
    "history": [
        {"date": "2026-08-01", "open_page_rank": 9.21, "estimated": False},
        {"date": "2026-06-01", "open_page_rank": 9.18, "estimated": True},
        {"date": "2026-07-01", "open_page_rank": 9.2, "estimated": False},
    ],
}

NOT_FOUND_RESULT = {
    "domain": "definitely-not-ranked-example.com",
    "found": False,
    "open_page_rank": None,
    "rank": None,
    "referring_domains": 0,
    "history": [],
}


def patch_post(mocker, response=None):
    """Replace the requests module used by the extractor with a mock."""
    requests_mock = mocker.patch.object(open_pagerank_features, "requests")
    if response is not None:
        requests_mock.post.return_value = response
    return requests_mock.post


def build_response(payload, headers=None):
    """Build a fake requests response returning the given payload."""
    response = Mock()
    response.json.return_value = payload
    response.headers = headers or {}
    response.raise_for_status.return_value = None
    return response


def test_found_domain(mocker):
    """Check that a ranked domain is parsed into features."""
    post = patch_post(
        mocker,
        build_response({"as_of": "2026-08-01", "count": 1, "results": [FOUND_RESULT]}),
    )

    result = OpenPageRankAPI("test-key").get_open_page_rank_features("GitHub.com")

    assert result.domain == "github.com"
    assert result.found is True
    assert result.page_rank_decimal == 9.21
    assert result.rank == 42
    assert result.referring_domains == 1234567
    assert result.updated_date == "2026-08-01"

    post.assert_called_once()
    args, kwargs = post.call_args
    assert args[0] == OPEN_PAGE_RANK_API_URL
    assert kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert kwargs["headers"]["Content-Type"] == "application/json"
    assert kwargs["json"] == {
        "domains": ["github.com"],
        "include_history": True,
    }


def test_not_found_domain_has_no_score(mocker):
    """Check that an unranked domain has no score instead of a zero."""
    patch_post(
        mocker,
        build_response(
            {"as_of": "2026-08-01", "count": 1, "results": [NOT_FOUND_RESULT]}
        ),
    )

    result = OpenPageRankAPI("test-key").get_open_page_rank_features(
        "definitely-not-ranked-example.com"
    )

    assert result.found is False
    assert result.page_rank_decimal is None
    assert result.page_rank_decimal != 0.0


def test_domain_missing_from_response_is_not_found(mocker):
    """Check that a domain absent from the response is reported as not found."""
    patch_post(
        mocker,
        build_response({"as_of": "2026-08-01", "count": 1, "results": [FOUND_RESULT]}),
    )

    features = OpenPageRankAPI("test-key").get_open_page_rank_features_bulk(
        ["github.com", "missing.example"]
    )

    assert features["missing.example"].found is False
    assert features["missing.example"].page_rank_decimal is None


def test_invalid_domain_returns_none(mocker):
    """Check that a domain rejected by the API yields no features."""
    patch_post(
        mocker,
        build_response(
            {
                "as_of": "2026-08-01",
                "count": 0,
                "results": [],
                "invalid": ["not a domain"],
            }
        ),
    )

    api = OpenPageRankAPI("test-key")

    assert api.get_open_page_rank_features("not a domain") is None
    assert api.invalid_domains == ["not a domain"]


def test_history_is_parsed_and_ordered(mocker):
    """Check that the monthly history is parsed and sorted by date."""
    patch_post(
        mocker,
        build_response({"as_of": "2026-08-01", "count": 1, "results": [FOUND_RESULT]}),
    )

    result = OpenPageRankAPI("test-key").get_open_page_rank_features("github.com")

    assert [entry.date for entry in result.history] == [
        "2026-06-01",
        "2026-07-01",
        "2026-08-01",
    ]
    assert result.history[0].open_page_rank == 9.18
    assert result.history[0].estimated is True
    assert result.history[-1].estimated is False
    assert result.page_rank_at("2026-07-15").date == "2026-07-01"
    assert result.page_rank_at("2026-01-01") is None


def test_bulk_batches_at_the_domain_limit(mocker):
    """Check that bulk requests are split into batches of 100 domains."""
    domains = [f"example{index}.com" for index in range(250)]
    post = patch_post(mocker, build_response({"as_of": "2026-08-01", "results": []}))

    features = OpenPageRankAPI("test-key").get_open_page_rank_features_bulk(domains)

    batches = [call.kwargs["json"]["domains"] for call in post.call_args_list]
    assert [len(batch) for batch in batches] == [
        MAX_DOMAINS_PER_REQUEST,
        MAX_DOMAINS_PER_REQUEST,
        50,
    ]
    assert sorted(domain for batch in batches for domain in batch) == sorted(domains)
    assert len(features) == 250
    assert all(entry.found is False for entry in features.values())


def test_bulk_deduplicates_domains(mocker):
    """Check that duplicated and blank domains are dropped before a request."""
    post = patch_post(mocker, build_response({"as_of": "2026-08-01", "results": []}))

    OpenPageRankAPI("test-key").get_open_page_rank_features_bulk(
        ["github.com", "GitHub.com", " github.com ", ""]
    )

    post.assert_called_once()
    assert post.call_args.kwargs["json"]["domains"] == ["github.com"]


def test_bulk_without_domains_does_not_call_the_api(mocker):
    """Check that an empty domain list makes no HTTP call."""
    post = patch_post(mocker)

    assert OpenPageRankAPI("test-key").get_open_page_rank_features_bulk([]) == {}
    post.assert_not_called()


def test_quota_headers_are_exposed(mocker):
    """Check that the quota headers are parsed and exposed to the caller."""
    patch_post(
        mocker,
        build_response(
            {"as_of": "2026-08-01", "results": [FOUND_RESULT]},
            headers={
                "X-Domains-Limit": "30000",
                "X-Domains-Remaining": "29900",
                "X-Domains-Reset": "1788220800",
            },
        ),
    )

    api = OpenPageRankAPI("test-key")
    api.get_open_page_rank_features("github.com")

    assert api.last_quota.limit == 30000
    assert api.last_quota.remaining == 29900
    assert api.last_quota.reset == 1788220800
    assert api.last_quota.reset_date == "2026-09-01T00:00:00+00:00"


def test_missing_quota_headers_are_none(mocker):
    """Check that absent quota headers do not break the quota parsing."""
    patch_post(mocker, build_response({"as_of": "2026-08-01", "results": []}))

    api = OpenPageRankAPI("test-key")
    api.get_open_page_rank_features_bulk(["github.com"])

    assert api.last_quota.limit is None
    assert api.last_quota.remaining is None
    assert api.last_quota.reset_date is None


def test_missing_api_key_is_reported(mocker):
    """Check that a missing API key is reported before any HTTP call."""
    post = patch_post(mocker)

    with pytest.raises(ValueError):
        OpenPageRankAPI("").get_open_page_rank_features("github.com")
    post.assert_not_called()


def test_features_keep_the_legacy_signature():
    """Check that the legacy three-argument construction still works."""
    features = OpenPageRankFeatures("github.com", 9.21, "2026-08-01")

    assert features.domain == "github.com"
    assert features.page_rank_decimal == 9.21
    assert features.updated_date == "2026-08-01"
    assert features.found is True
    assert features.rank is None
    assert features.referring_domains is None
    assert features.history == []
