import os
from dataclasses import asdict
from typing import Any

import scrapy
from scrapy.http import Response

from web2vec.config import config
from web2vec.crawlers.models import WebPage
from web2vec.utils import sanitize_filename, store_json


class Web2VecSpider(scrapy.Spider):
    name = "Web2VecSpider"

    def __init__(
        self,
        start_urls,
        allowed_domains=None,
        custom_settings=None,
        extractors=None,
        *args,
        **kwargs,
    ):
        super(Web2VecSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.allowed_domains = allowed_domains or []
        self.extractors = extractors or []
        if custom_settings:
            for key, value in custom_settings.items():
                setattr(self, key, value)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        page = WebPage(response.url, response.text)
        sanitized_url = sanitize_filename(response.url)
        filename = f"{self.name}_{sanitized_url}.json"
        file_path = os.path.join(config.crawler_output_path, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        extractors_result = []
        for extractor in self.extractors:
            try:
                extractor_result = extractor.extract_features(response)
                if extractor_result is None:
                    continue
                extractors_result.append(
                    {
                        "name": extractor.features_name(),
                        "result": asdict(extractor_result),
                    }
                )
            except Exception as e:  # noqa
                self.logger.warning(
                    f"Error extracting features with {extractor.features_name()}: {e}"
                )
        store_json(
            {
                "url": page.url,
                "title": page.get_title(),
                "html": page.html,
                "response_headers": {
                    str(key): str(value) for key, value in response.headers.items()
                },
                "status_code": response.status,
                "extractors": extractors_result,
            },
            file_path,
        )

        for a in response.css("a::attr(href)").getall():
            yield response.follow(a, self.parse)
