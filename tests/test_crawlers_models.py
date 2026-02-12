from web2vec.crawlers.models import WebPage


def test_webpage_get_title_extracts_text():
    """Ensure WebPage.get_title leverages scrapy Selectors correctly."""
    html = "<html><head><title>Hello</title></head><body></body></html>"
    page = WebPage("https://example.com", html)
    assert page.get_title() == "Hello"
