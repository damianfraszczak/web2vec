import scrapy


class WebPage:
    """Model of a web page"""

    def __init__(self, url, html):
        self.url = url
        self.html = html

    def get_title(self):
        return scrapy.Selector(text=self.html).css("title::text").get()
