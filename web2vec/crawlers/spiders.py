import json
import os
import re
from typing import Any

import scrapy
from scrapy.http import Response

from web2vec.config import config
from web2vec.crawlers.models import WebPage


class Web2VecSpider(scrapy.Spider):
    name = 'Web2VecSpider'

    custom_settings = {
        'DEPTH_LIMIT': config.spider_depth_limit
    }

    def __init__(self, start_urls, allowed_domains=None, custom_settings=None, *args, **kwargs):
        super(Web2VecSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.allowed_domains = allowed_domains or []
        if custom_settings:
            for key, value in custom_settings.items():
                setattr(self, key, value)

    def sanitize_filename(self, filename):
        return re.sub(r'[<>:"/\\|?*]', '_', filename)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        page = WebPage(response.url, response.text)
        sanitized_url = self.sanitize_filename(response.url)
        filename = f"output/{self.name}_{sanitized_url}.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps({
                'url': page.url,
                'title': page.get_title(),
                'html': page.html,
            }, indent=4))

        for a in response.css('a::attr(href)').getall():
            yield response.follow(a, self.parse)

