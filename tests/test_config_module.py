from web2vec.config import Config


def test_config_default_paths(tmp_path):
    """Ensure Config derives crawler/remote paths from default root."""
    cfg = Config(
        default_output_path=str(tmp_path),
        remote_url_output_path="",
        crawler_output_path="",
    )
    assert cfg.remote_url_output_path == str(tmp_path / "remote")
    assert cfg.crawler_output_path == str(tmp_path / "crawler")


def test_config_respects_explicit_paths(tmp_path):
    """Validate that user-provided paths remain unchanged."""
    custom_remote = tmp_path / "custom-remote"
    cfg = Config(
        default_output_path=str(tmp_path),
        remote_url_output_path=str(custom_remote),
        crawler_output_path="/tmp/crawler",
    )
    assert cfg.remote_url_output_path == str(custom_remote)
    assert cfg.crawler_output_path == "/tmp/crawler"
