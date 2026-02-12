from types import SimpleNamespace

from web2vec.extractors import url_geo_features


class _DummyReader:
    """Context manager mimicking geoip2 database reader."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def country(self, ip):
        """Return a fake country lookup."""
        return SimpleNamespace(country=SimpleNamespace(iso_code="US"))

    def asn(self, ip):
        """Return a fake ASN lookup."""
        return SimpleNamespace(autonomous_system_number=64512)


def test_get_geolite_country_and_asn(monkeypatch, tmp_path):
    """Patch repo downloads and reader to cover geo helpers."""
    assets = {
        url_geo_features.GeoLiteDbType.COUNTRY: tmp_path / "country.mmdb",
        url_geo_features.GeoLiteDbType.ASN: tmp_path / "asn.mmdb",
    }
    for asset in assets.values():
        asset.write_bytes(b"\x00")

    monkeypatch.setattr(
        url_geo_features,
        "get_geolite_db_files",
        lambda db_type=None: assets if db_type is None else str(assets[db_type]),
    )
    monkeypatch.setattr(
        url_geo_features.geoip2.database,
        "Reader",
        lambda path: _DummyReader(),
    )

    assert url_geo_features.get_country("1.1.1.1") == "US"
    assert url_geo_features.get_asn("1.1.1.1") == 64512


def test_get_geolite_db_files_downloads_assets(monkeypatch, tmp_path):
    """Verify asset resolution via the GitHub release helper."""
    release_info = {
        "assets": [
            {
                "name": f"{url_geo_features.GeoLiteDbType.COUNTRY.value}.mmdb",
                "browser_download_url": "https://example.com/country",
            },
            {
                "name": f"{url_geo_features.GeoLiteDbType.ASN.value}.mmdb",
                "browser_download_url": "https://example.com/asn",
            },
        ]
    }

    def fake_fetch(url, directory=None, headers=None, timeout=86400):
        filename = (
            "GeoLite2-Country.mmdb" if url.endswith("country") else "GeoLite2-ASN.mmdb"
        )
        path = tmp_path / filename
        path.write_text("data", encoding="utf-8")
        return str(path)

    monkeypatch.setattr(
        url_geo_features,
        "get_github_repo_release_info",
        lambda repo: release_info,
    )
    monkeypatch.setattr(url_geo_features, "fetch_file_from_url", fake_fetch)

    files = url_geo_features.get_geolite_db_files()
    assert len(files) == 2
    country_path = url_geo_features.get_geolite_db_files(
        url_geo_features.GeoLiteDbType.COUNTRY
    )
    assert country_path.endswith("GeoLite2-Country.mmdb")
