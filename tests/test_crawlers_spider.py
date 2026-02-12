from dataclasses import dataclass

from scrapy.http import Headers, Request, TextResponse

from web2vec.crawlers import spiders


@dataclass
class _DummyFeatures:
    value: int = 42


class _DummyExtractor:
    def features_name(self):
        """Return a stable extractor name."""
        return "Dummy"

    def extract_features(self, response):
        """Simulate successful feature extraction."""
        return _DummyFeatures()


def test_web2vec_spider_parse_writes_output(monkeypatch, tmp_path):
    """Run the spider parse flow with a stub response and extractor."""
    spider = spiders.Web2VecSpider(
        start_urls=["https://example.com"], extractors=[_DummyExtractor()]
    )
    monkeypatch.setattr(spiders.config, "crawler_output_path", tmp_path.as_posix())

    captured = {}

    def fake_store_json(payload, path):
        captured["payload"] = payload
        captured["path"] = path

    monkeypatch.setattr(spiders, "store_json", fake_store_json)

    headers = Headers({"Content-Type": b"text/html"})
    body = b'<html><head><title>Hello</title></head><body><a href="/next">Next</a></body></html>'
    request = Request(url="https://example.com")
    response = TextResponse(
        url="https://example.com",
        request=request,
        headers=headers,
        body=body,
        encoding="utf-8",
    )
    response.status = 200

    results = list(spider.parse(response))
    assert captured["payload"]["title"] == "Hello"
    assert captured["payload"]["extractors"][0]["name"] == "Dummy"
    assert captured["payload"]["status_code"] == 200
    assert len(results) == 1
