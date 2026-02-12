from types import SimpleNamespace

from web2vec.extractors.external_api import google_index_features


def test_google_index_features_detects_match(monkeypatch):
    """Ensure API results mark URLs as indexed when a match appears."""

    def fake_get(url, headers=None, timeout=0):  # noqa: D401
        return SimpleNamespace(
            status_code=200,
            json=lambda: {
                "web": {
                    "results": [
                        {"url": "https://example.com/landing"},
                        {"url": "https://other.com"},
                    ]
                }
            },
            raise_for_status=lambda: None,
        )

    monkeypatch.setattr(google_index_features.requests, "get", fake_get)
    features = google_index_features.get_google_index_features("example.com")
    assert features.is_indexed is True
    assert features.position == 1


def test_google_index_features_handles_errors(monkeypatch):
    """Return None when the API raises an exception."""

    def raising_get(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(google_index_features.requests, "get", raising_get)
    features = google_index_features.get_google_index_features("missing.com")
    assert features.is_indexed is None
    assert features.position is None


def test_google_index_features_marks_not_indexed(monkeypatch):
    """Return False when search results do not contain the domain."""

    def fake_get(url, headers=None, timeout=0):  # noqa: D401
        return SimpleNamespace(
            status_code=200,
            json=lambda: {"web": {"results": [{"url": "https://other.com"}]}},
            raise_for_status=lambda: None,
        )

    monkeypatch.setattr(google_index_features.requests, "get", fake_get)
    features = google_index_features.get_google_index_features("example.com")
    assert features.is_indexed is False
    assert features.position is None
