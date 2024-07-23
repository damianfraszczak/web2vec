# Quick Start Guide for Web2Vec

Web2Vec is a comprehensive library designed to convert websites into vector parameters. It provides ready-to-use implementations of web crawlers using Scrapy, making it accessible for less experienced researchers. This tool is invaluable for website analysis tasks, including SEO, disinformation detection, and phishing identification.

## Installation

Install Web2Vec using pip:

```bash
pip install web2vec
```
## Configuration
Configure the library using environment variables or configuration files.
```shell
export WEB2VEC_CRAWLER_SPIDER_DEPTH_LIMIT=2
export WEB2VEC_DEFAULT_OUTPUT_PATH=/home/admin/crawler/output
export WEB2VEC_OPEN_PAGE_RANK_API_KEY=XXXXX
```
## Crawling websites and extract parameters

```python
import os

from scrapy.crawler import CrawlerProcess

from src.web2vec.config import config
from src.web2vec.crawlers.extractors import ALL_EXTRACTORS
from src.web2vec.crawlers.spiders import Web2VecSpider

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
    start_urls=["http://quotes.toscrape.com/"], # pages to process
    allowed_domains=["quotes.toscrape.com"], # domains to process for links
    extractors=ALL_EXTRACTORS, # extractors to use
)
process.start()
```

## Website analysis
Websites can be analysed without scrapping process, by using extractors directly. For example to get data from SimilarWeb for given domain you have just to call appropriate method:

```python
from src.web2vec.extractors.external_api.similar_web_features import \
    get_similar_web_features

domain_to_check = "down.pcclear.com"
entry = get_similar_web_features(domain_to_check)
print(entry)
```

If you would like to test ``Web2Vec`` functionalities without installing it on your machine consider using the preconfigured [Jupyter notebook](web2vec.ipynb).
