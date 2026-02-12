from __future__ import annotations

from datetime import datetime

import pytest
import requests

from web2vec import utils


class _FixedDatetime(datetime):
    """Deterministic datetime replacement for file-path tests."""

    @classmethod
    def now(cls, tz=None):  # noqa: D401 - behave like datetime.now
        return cls(2024, 1, 2, 3, 4, 5, tzinfo=tz)


def test_valid_ip_and_domain_helpers():
    """Validate the small helpers that work without network access."""
    assert utils.valid_ip("192.0.2.1") is True
    assert utils.valid_ip("invalid-ip") is False
    assert utils.get_domain_from_url("https://example.com/path") == "example.com"
    assert utils.sanitize_filename('exa:mple*file?name"') == "exa_mple_file_name_"
    assert utils.is_numerical_type(42) is True
    assert utils.is_numerical_type(False) is True  # bool is treated as numeric
    assert utils.is_numerical_type("42") is False
    assert utils.transform_value(True) == 1
    assert utils.transform_value(datetime(2024, 1, 1, 0, 0)) == "2024-01-01T00:00:00"
    assert utils.transform_value("text") == "text"
    assert utils.entropy("aaaaabbbbcc") == pytest.approx(1.49, rel=0.01)


def test_get_file_path_for_url_timestamp_variants(monkeypatch, tmp_path):
    """Ensure timestamp selection logic matches timeout buckets."""
    monkeypatch.setattr(utils, "datetime", _FixedDatetime)
    monkeypatch.setattr(utils.config, "remote_url_output_path", tmp_path.as_posix())

    day_path = utils.get_file_path_for_url("https://one", timeout=86400)
    hour_path = utils.get_file_path_for_url("https://two", timeout=3600)
    minute_path = utils.get_file_path_for_url("https://three", timeout=3599)
    none_path = utils.get_file_path_for_url("https://four", timeout=None)

    assert day_path.endswith("20240102_https___one")
    assert hour_path.endswith("20240102_03_https___two")
    assert minute_path.endswith("20240102_0304_https___three")
    assert none_path.endswith("https___four")


def test_fetch_file_from_url_uses_cached_copy(monkeypatch, tmp_path):
    """Exercise caching branch when the file is still fresh."""
    target_dir = tmp_path / "remote"
    monkeypatch.setattr(utils.config, "remote_url_output_path", target_dir.as_posix())

    calls = {"count": 0}

    class _FakeResponse:
        status_code = 200
        content = b"payload"

        def raise_for_status(self):
            """Pretend the request succeeded."""

    def fake_fetch(url, headers=None, ssl_verify=False):  # noqa: D401
        calls["count"] += 1
        return _FakeResponse()

    monkeypatch.setattr(utils, "fetch_url", fake_fetch)

    cached_path = utils.fetch_file_from_url(
        "https://example.com/file.txt", timeout=3600
    )
    assert cached_path.startswith(target_dir.as_posix())
    assert calls["count"] == 1

    # Second call should reuse on-disk file and avoid network fetch.
    cached_again = utils.fetch_file_from_url(
        "https://example.com/file.txt", timeout=3600
    )
    assert cached_again == cached_path
    assert calls["count"] == 1

    assert (
        utils.fetch_file_from_url_and_read("https://example.com/file.txt", timeout=3600)
        == "payload"
    )


def test_fetch_file_from_url_raises_for_http_error(monkeypatch, tmp_path):
    """Propagate HTTP errors when remote download fails."""
    monkeypatch.setattr(utils.config, "remote_url_output_path", tmp_path.as_posix())

    class _ErrorResponse:
        status_code = 500

        def raise_for_status(self):
            """Raise an HTTPError."""
            raise requests.HTTPError("boom")

    monkeypatch.setattr(utils, "fetch_url", lambda *args, **kwargs: _ErrorResponse())

    with pytest.raises(requests.HTTPError):
        utils.fetch_file_from_url("https://example.com/file.txt", timeout=None)


def test_get_github_repo_release_info(monkeypatch):
    """Verify JSON parsing path for GitHub release helper."""
    payload = {"tag_name": "v1.0.0"}
    monkeypatch.setattr(
        utils, "fetch_file_from_url_and_read", lambda repo, *_: '{"tag_name":"v1.0.0"}'
    )
    assert utils.get_github_repo_release_info("owner/repo") == payload


def test_store_json_serializes_datetimes(tmp_path):
    """Confirm store_json writes ISO-formatted timestamps."""
    target = tmp_path / "data.json"
    utils.store_json({"at": datetime(2024, 1, 1, 0, 0)}, target.as_posix())
    assert '"2024-01-01T00:00:00"' in target.read_text(encoding="utf-8")
