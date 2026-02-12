import json
from types import SimpleNamespace

import requests

from web2vec.extractors.external_api import (
    open_pagerank_features,
    open_phish_features,
    phish_tank_features,
    url_haus_features,
)


def test_open_pagerank_features_success(monkeypatch):
    """Ensure Open PageRank success path maps JSON into the dataclass."""

    class _FakeResponse:
        status_code = 200

        def json(self):
            return {
                "response": [{"domain": "example.com", "page_rank_decimal": 5.5}],
                "last_updated": "today",
            }

        def raise_for_status(self):
            """Pretend the request succeeded."""

    monkeypatch.setattr(
        open_pagerank_features.requests, "get", lambda *a, **k: _FakeResponse()
    )
    monkeypatch.setattr(
        open_pagerank_features.config, "open_page_rank_api_key", "token"
    )

    result = open_pagerank_features.get_open_page_rank_features("example.com")
    assert result.domain == "example.com"
    assert result.page_rank_decimal == 5.5
    assert result.updated_date == "today"


def test_open_pagerank_features_no_data(monkeypatch):
    """Return None when the API responds without entries."""

    class _EmptyResponse:
        status_code = 200

        def json(self):
            return {"response": []}

        def raise_for_status(self):
            """Pretend OK."""

    monkeypatch.setattr(
        open_pagerank_features.requests, "get", lambda *a, **k: _EmptyResponse()
    )
    monkeypatch.setattr(
        open_pagerank_features.config, "open_page_rank_api_key", "token"
    )
    assert open_pagerank_features.get_open_page_rank_features("example.com") is None


def test_open_phish_features_detects_match(monkeypatch):
    """Patch the feed download to simulate a suspicious URL."""
    monkeypatch.setattr(
        open_phish_features,
        "fetch_file_from_url_and_read",
        lambda url: "http://bad.example\nhttp://safe.example",
    )
    result = open_phish_features.get_open_phish_features("bad.example")
    assert result.is_phishing is True


def test_open_phish_features_handles_errors(monkeypatch):
    """Ensure RequestException path marks domain as safe."""
    monkeypatch.setattr(
        open_phish_features,
        "logger",
        SimpleNamespace(error=lambda *a, **k: None),
    )
    monkeypatch.setattr(
        open_phish_features,
        "fetch_file_from_url_and_read",
        lambda *_: (_ for _ in ()).throw(requests.exceptions.RequestException("boom")),
    )
    assert (
        open_phish_features.get_open_phish_features("bad.example").is_phishing is False
    )


def test_phish_tank_features_and_check(monkeypatch):
    """Cover PhishTank feed parsing plus the boolean helper."""
    payload = json.dumps(
        [
            {
                "phish_id": "1",
                "url": "http://bad.example",
                "phish_detail_url": "detail",
                "submission_time": "now",
                "verified": "yes",
                "verification_time": "now",
                "online": "yes",
                "target": "bank",
            }
        ]
    )
    monkeypatch.setattr(
        phish_tank_features, "fetch_file_from_url_and_read", lambda url: payload
    )
    entry = phish_tank_features.get_phishtank_features("bad.example")
    assert entry.phish_id == "1"
    assert phish_tank_features.check_phish_phishtank("bad.example") is True


def test_phish_tank_handles_errors(monkeypatch):
    """Return None when the feed download fails."""
    monkeypatch.setattr(
        phish_tank_features,
        "logger",
        SimpleNamespace(error=lambda *a, **k: None),
    )

    def raising_fetch(*_args, **_kwargs):
        raise requests.RequestException("boom")

    monkeypatch.setattr(
        phish_tank_features, "fetch_file_from_url_and_read", raising_fetch
    )
    assert phish_tank_features.get_phishtank_features("bad.example") is None
    assert phish_tank_features.check_phish_phishtank("bad.example") is False


def test_url_haus_features_filtering(monkeypatch):
    """Parse a tiny CSV feed and filter by domain."""
    csv_rows = ["#" for _ in range(9)] + [
        '"1","2024-01-01","http://bad.example/path","online","2024-01-02","malware","tag","link","reporter"'
    ]
    csv_payload = "\n".join(csv_rows)
    monkeypatch.setattr(
        url_haus_features, "fetch_file_from_url_and_read", lambda url: csv_payload
    )
    entries = list(url_haus_features.get_url_haus_features("bad.example"))
    assert len(entries) == 1
    assert entries[0].threat == "malware"


def test_url_haus_handles_exception(monkeypatch):
    """Return an empty iterator when the CSV fetch fails."""

    def raising_fetch(*_args, **_kwargs):
        raise requests.exceptions.RequestException("boom")

    monkeypatch.setattr(
        url_haus_features, "fetch_file_from_url_and_read", raising_fetch
    )
    assert list(url_haus_features.get_url_haus_features("bad.example")) == []
