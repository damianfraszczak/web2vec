import os

from scrapy.crawler import CrawlerProcess

from src.web2vec.config import config
from src.web2vec.crawlers.extractors import ALL_EXTRACTORS
from src.web2vec.crawlers.spiders import Web2VecSpider
from src.web2vec.extractors.external_api.similar_web_features import (
    get_similar_web_features,
)


def run_spider():
    """Run sample spider process to collect web pages features."""
    process = CrawlerProcess(
        settings={
            "FEEDS": {
                os.path.join(config.crawler_output_path, "output.json"): {
                    "format": "json",
                    "encoding": "utf8",
                }
            },
            "DEPTH_LIMIT": config.crawler_spider_depth_limit,
            "LOG_LEVEL": "INFO",
        }
    )

    process.crawl(
        Web2VecSpider,
        start_urls=["http://quotes.toscrape.com/"],
        allowed_domains=["quotes.toscrape.com"],
        extractors=ALL_EXTRACTORS,
    )
    process.start()


if __name__ == "__main__":
    run_spider()
    # G = build_graph(config.crawler_output_path)
    # visualize_graph_with_centrality(G)

domain_to_check = "down.pcclear.com"
entry = get_similar_web_features(domain_to_check)
print(entry)
