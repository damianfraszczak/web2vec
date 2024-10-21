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
import web2vec as w2v

process = CrawlerProcess(
    settings={
        "FEEDS": {
            os.path.join(w2v.config.crawler_output_path, "output.json"): {
                "format": "json",
                "encoding": "utf8",
            }
        },
        "DEPTH_LIMIT": w2v.config.crawler_spider_depth_limit,
        "LOG_LEVEL": "INFO",
    }
)

process.crawl(
    w2v.Web2VecSpider,
    start_urls=["http://quotes.toscrape.com/"], # pages to process
    allowed_domains=["quotes.toscrape.com"], # domains to process for links
    extractors=w2v.ALL_EXTRACTORS, # extractors to use
)
process.start()

```
and you will get files with similar structure:
```json

sample content
```json
{
    "url": "http://quotes.toscrape.com/",
    "title": "Quotes to Scrape",
    "html": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n\t<meta charset=\"UTF-8\">\n\t<title>Quotes to Scrape</title>\n    <link rel=\"stylesheet\" href=\"/static/bootstrap.min.css\">\n    <link rel=\"stylesheet\" href=\"/static/main.css\">\n</head>\n<body>\n    <div class=\"container\">\n        <div class=\"row header-box\">\n            <div class=\"col-md-8\">\n                <h1>\n                    <a href=\"/\" style=\"text-decoration: none\">Quotes to Scrape</a>\n                </h1>\n            </div>\n            <div class=\"col-md-4\">\n                <p>\n                \n                    <a href=\"/login\">Login</a>\n                \n                </p>\n            </div>\n        </div>\n    \n\n<div class=\"row\">\n    <div class=\"col-md-8\">\n\n    <div class=\"quote\" itemscope itemtype=\"http://schema.org/CreativeWork\">\n        <span class=\"text\" itemprop=\"text\">\u201cThe world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.\u201d</span>\n        <span>by <small class=\"author\" itemprop=\"author\">Albert Einstein</small>\n        <a href=\"/author/Albert-Einstein\">(about)</a>\n        </span>\n        <div class=\"tags\">\n            Tags:\n            <meta class=\"keywords\" itemprop=\"keywords\" content=\"change,deep-thoughts,thinking,world\" /    > \n            \n            <a class=\"tag\" href=\"/tag/change/page/1/\">change</a>\n            \n            <a class=\"tag\" href=\"/tag/deep-thoughts/page/1/\">deep-thoughts</a>\n            \n            <a class=\"tag\" href=\"/tag/thinking/page/1/\">thinking</a>\n            \n            <a class=\"tag\" href=\"/tag/world/page/1/\">world</a>\n            \n        </div>\n    </div>\n\n    <div class=\"quote\" itemscope itemtype=\"http://schema.org/CreativeWork\">\n        <span class=\"text\" itemprop=\"text\">\u201cIt is our choices, Harry, that show what we truly are, far more than our abilities.\u201d</span>\n        <span>by <small class=\"author\" itemprop=\"author\">J.K. Rowling</small>\n        <a href=\"/author/J-K-Rowling\">(about)</a>\n        </span>\n        <div class=\"tags\">\n            Tags:\n            <meta class=\"keywords\" itemprop=\"keywords\" content=\"abilities,choices\" /    > \n            \n            <a class=\"tag\" href=\"/tag/abilities/page/1/\">abilities</a>\n            \n            <a class=\"tag\" href=\"/tag/choices/page/1/\">choices</a>\n            \n        </div>\n    </div>\n\n    <div class=\"quote\" itemscope itemtype=\"http://schema.org/CreativeWork\">\n        <span class=\"text\" itemprop=\"text\">\u201cThere are only two ways to live your life. One is as though nothing is a miracle. The other is as though everything is a miracle.\u201d</span>\n        <span>by <small class=\"author\" itemprop=\"author\">Albert Einstein</small>\n        <a href=\"/author/Albert-Einstein\">(about)</a>\n        </span>\n        <div class=\"tags\">\n            Tags:\n            <meta class=\"keywords\" itemprop=\"keywords\" content=\"inspirational,life,live,miracle,miracles\" /    > \n            \n            <a class=\"tag\" href=\"/tag/inspirational/page/1/\">inspirational</a>\n            \n            <a class=\"tag\" href=\"/tag/life/page/1/\">life</a>\n            \n            <a class=\"tag\" href=\"/tag/live/page/1/\">live</a>\n            \n            <a class=\"tag\" href=\"/tag/miracle/page/1/\">miracle</a>\n            \n            <a class=\"tag\" href=\"/tag/miracles/page/1/\">miracles</a>\n            \n        </div>\n    </div>\n\n    <div class=\"quote\" itemscope itemtype=\"http://schema.org/CreativeWork\">\n        <span class=\"text\" itemprop=\"text\">\u201cThe person, be it gentleman or lady, who has not pleasure in a good novel, must be intolerably stupid.\u201d</span>\n        <span>by <small class=\"author\" itemprop=\"author\">Jane Austen</small>\n        <a href=\"/author/Jane-Austen\">(about)</a>\n        </span>\n        <div class=\"tags\">\n            Tags:\n            <meta class=\"keywords\" itemprop=\"keywords\" content=\"aliteracy,books,classic,humor\" /    > \n            \n            <a class=\"tag\" href=\"/tag/aliteracy/page/1/\">aliteracy</a>\n            \n            <a class=\"tag\" href=\"/tag/books/page/1/\">books</a>\n            \n            <a class=\"tag\" href=\"/tag/classic/page/1/\">classic</a>\n            \n            <a class=\"tag\" href=\"/tag/humor/page/1/\">humor</a>\n            \n        </div>\n    </div>\n\n    <div class=\"quote\" itemscope itemtype=\"http://schema.org/CreativeWork\">\n        <span class=\"text\" itemprop=\"text\">\u201cImperfection is beauty, madness is genius and it&#39;s better to be absolutely ridiculous than absolutely boring.\u201d</span>\n        <span>by <small class=\"author\" itemprop=\"author\">Marilyn Monroe</small>\n        <a href=\"/author/Marilyn-Monroe\">(about)</a>\n        </span>\n        <div class=\"tags\">\n            Tags:\n            <meta class=\"keywords\" itemprop=\"keywords\" content=\"be-yourself,inspirational\" /    > \n            \n            <a class=\"tag\" href=\"/tag/be-yourself/page/1/\">be-yourself</a>\n            \n            <a class=\"tag\" href=\"/tag/inspirational/page/1/\">inspirational</a>\n            \n        </div>\n    </div>\n\n    <div class=\"quote\" itemscope itemtype=\"http://schema.org/CreativeWork\">\n        <span class=\"text\" itemprop=\"text\">\u201cTry not to become a man of success. Rather become a man of value.\u201d</span>\n        <span>by <small class=\"author\" itemprop=\"author\">Albert Einstein</small>\n        <a href=\"/author/Albert-Einstein\">(about)</a>\n        </span>\n        <div class=\"tags\">\n            Tags:\n            <meta class=\"keywords\" itemprop=\"keywords\" content=\"adulthood,success,value\" /    > \n            \n            <a class=\"tag\" href=\"/tag/adulthood/page/1/\">adulthood</a>\n            \n            <a class=\"tag\" href=\"/tag/success/page/1/\">success</a>\n            \n            <a class=\"tag\" href=\"/tag/value/page/1/\">value</a>\n            \n        </div>\n    </div>\n\n    <div class=\"quote\" itemscope itemtype=\"http://schema.org/CreativeWork\">\n        <span class=\"text\" itemprop=\"text\">\u201cIt is better to be hated for what you are than to be loved for what you are not.\u201d</span>\n        <span>by <small class=\"author\" itemprop=\"author\">Andr\u00e9 Gide</small>\n        <a href=\"/author/Andre-Gide\">(about)</a>\n        </span>\n        <div class=\"tags\">\n            Tags:\n            <meta class=\"keywords\" itemprop=\"keywords\" content=\"life,love\" /    > \n            \n            <a class=\"tag\" href=\"/tag/life/page/1/\">life</a>\n            \n            <a class=\"tag\" href=\"/tag/love/page/1/\">love</a>\n            \n        </div>\n    </div>\n\n    <div class=\"quote\" itemscope itemtype=\"http://schema.org/CreativeWork\">\n        <span class=\"text\" itemprop=\"text\">\u201cI have not failed. I&#39;ve just found 10,000 ways that won&#39;t work.\u201d</span>\n        <span>by <small class=\"author\" itemprop=\"author\">Thomas A. Edison</small>\n        <a href=\"/author/Thomas-A-Edison\">(about)</a>\n        </span>\n        <div class=\"tags\">\n            Tags:\n            <meta class=\"keywords\" itemprop=\"keywords\" content=\"edison,failure,inspirational,paraphrased\" /    > \n            \n            <a class=\"tag\" href=\"/tag/edison/page/1/\">edison</a>\n            \n            <a class=\"tag\" href=\"/tag/failure/page/1/\">failure</a>\n            \n            <a class=\"tag\" href=\"/tag/inspirational/page/1/\">inspirational</a>\n            \n            <a class=\"tag\" href=\"/tag/paraphrased/page/1/\">paraphrased</a>\n            \n        </div>\n    </div>\n\n    <div class=\"quote\" itemscope itemtype=\"http://schema.org/CreativeWork\">\n        <span class=\"text\" itemprop=\"text\">\u201cA woman is like a tea bag; you never know how strong it is until it&#39;s in hot water.\u201d</span>\n        <span>by <small class=\"author\" itemprop=\"author\">Eleanor Roosevelt</small>\n        <a href=\"/author/Eleanor-Roosevelt\">(about)</a>\n        </span>\n        <div class=\"tags\">\n            Tags:\n            <meta class=\"keywords\" itemprop=\"keywords\" content=\"misattributed-eleanor-roosevelt\" /    > \n            \n            <a class=\"tag\" href=\"/tag/misattributed-eleanor-roosevelt/page/1/\">misattributed-eleanor-roosevelt</a>\n            \n        </div>\n    </div>\n\n    <div class=\"quote\" itemscope itemtype=\"http://schema.org/CreativeWork\">\n        <span class=\"text\" itemprop=\"text\">\u201cA day without sunshine is like, you know, night.\u201d</span>\n        <span>by <small class=\"author\" itemprop=\"author\">Steve Martin</small>\n        <a href=\"/author/Steve-Martin\">(about)</a>\n        </span>\n        <div class=\"tags\">\n            Tags:\n            <meta class=\"keywords\" itemprop=\"keywords\" content=\"humor,obvious,simile\" /    > \n            \n            <a class=\"tag\" href=\"/tag/humor/page/1/\">humor</a>\n            \n            <a class=\"tag\" href=\"/tag/obvious/page/1/\">obvious</a>\n            \n            <a class=\"tag\" href=\"/tag/simile/page/1/\">simile</a>\n            \n        </div>\n    </div>\n\n    <nav>\n        <ul class=\"pager\">\n            \n            \n            <li class=\"next\">\n                <a href=\"/page/2/\">Next <span aria-hidden=\"true\">&rarr;</span></a>\n            </li>\n            \n        </ul>\n    </nav>\n    </div>\n    <div class=\"col-md-4 tags-box\">\n        \n            <h2>Top Ten tags</h2>\n            \n            <span class=\"tag-item\">\n            <a class=\"tag\" style=\"font-size: 28px\" href=\"/tag/love/\">love</a>\n            </span>\n            \n            <span class=\"tag-item\">\n            <a class=\"tag\" style=\"font-size: 26px\" href=\"/tag/inspirational/\">inspirational</a>\n            </span>\n            \n            <span class=\"tag-item\">\n            <a class=\"tag\" style=\"font-size: 26px\" href=\"/tag/life/\">life</a>\n            </span>\n            \n            <span class=\"tag-item\">\n            <a class=\"tag\" style=\"font-size: 24px\" href=\"/tag/humor/\">humor</a>\n            </span>\n            \n            <span class=\"tag-item\">\n            <a class=\"tag\" style=\"font-size: 22px\" href=\"/tag/books/\">books</a>\n            </span>\n            \n            <span class=\"tag-item\">\n            <a class=\"tag\" style=\"font-size: 14px\" href=\"/tag/reading/\">reading</a>\n            </span>\n            \n            <span class=\"tag-item\">\n            <a class=\"tag\" style=\"font-size: 10px\" href=\"/tag/friendship/\">friendship</a>\n            </span>\n            \n            <span class=\"tag-item\">\n            <a class=\"tag\" style=\"font-size: 8px\" href=\"/tag/friends/\">friends</a>\n            </span>\n            \n            <span class=\"tag-item\">\n            <a class=\"tag\" style=\"font-size: 8px\" href=\"/tag/truth/\">truth</a>\n            </span>\n            \n            <span class=\"tag-item\">\n            <a class=\"tag\" style=\"font-size: 6px\" href=\"/tag/simile/\">simile</a>\n            </span>\n            \n        \n    </div>\n</div>\n\n    </div>\n    <footer class=\"footer\">\n        <div class=\"container\">\n            <p class=\"text-muted\">\n                Quotes by: <a href=\"https://www.goodreads.com/quotes\">GoodReads.com</a>\n            </p>\n            <p class=\"copyright\">\n                Made with <span class='zyte'>\u2764</span> by <a class='zyte' href=\"https://www.zyte.com\">Zyte</a>\n            </p>\n        </div>\n    </footer>\n</body>\n</html>",
    "response_headers": {
        "b'Content-Length'": "[b'11054']",
        "b'Date'": "[b'Tue, 23 Jul 2024 06:05:10 GMT']",
        "b'Content-Type'": "[b'text/html; charset=utf-8']"
    },
    "status_code": 200,
    "extractors": [
        {
            "name": "DNSFeatures",
            "result": {
                "domain": "quotes.toscrape.com",
                "records": [
                    {
                        "record_type": "A",
                        "ttl": 225,
                        "values": [
                            "35.211.122.109"
                        ]
                    },
                    {
                        "record_type": "CNAME",
                        "ttl": 225,
                        "values": [
                            "ingress.prod-01.gcp.infra.zyte.group."
                        ]
                    }
                ]
            }
        }
    ]
}
```

## Website analysis
Websites can be analysed without scrapping process, by using extractors directly. For example to get data from SimilarWeb for given domain you have just to call appropriate method:

```python
import web2vec as w2v

domain_to_check = "down.pcclear.com"
entry = w2v.get_similar_web_features(domain_to_check)
print(entry)
```

If you would like to test ``Web2Vec`` functionalities without installing it on your machine consider using the preconfigured [Jupyter notebook](jupyter/web2vec.ipynb).
How to create own website related dataset using Web2Vec is described in [this notebook](jupyter/web2vec_dataset_creation.ipynb).
How to train ML model using Web2Vec dataset is described in [this notebook](jupyter/web2vec_model_training.ipynb).
