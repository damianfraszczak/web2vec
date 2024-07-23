# Web2Vec: Website to Vector Library
## Overview
Web2Vec is a comprehensive library designed to convert websites into vector parameters. It provides ready-to-use implementations of web crawlers using Scrapy, making it accessible for less experienced researchers. This tool is invaluable for website analysis tasks, including SEO, disinformation detection, and phishing identification.

Website analysis is crucial in various fields, such as SEO, where it helps improve website ranking, and in security, where it aids in identifying phishing sites. By building datasets based on known safe and malicious websites, Web2Vec facilitates the collection and analysis of their parameters, making it an ideal solution for these tasks.

The goal of Web2Vec is to offer a comprehensive repository for implementing a broad spectrum of website processing-related methods. Many available tools exist, but learning and using them can be time-consuming. Moreover, new features are continually being introduced, making it difficult to keep up with the latest techniques. Web2Vec aims to bridge this gap by providing a complete solution for website analysis. This repository facilitates the collection and analysis of extensive information about websites, supporting both academic research and industry applications.
Crucial factors:
- All-in-One Solution: Web2Vec is an all-in-one solution that allows for the collection of a wide range of information about websites.
- Efficiency and Expertise: Building a similar solution independently would be very time-consuming and require specialized knowledge. Web2Vec not only integrates with available APIs but also scrapes results from services like Google Index using Selenium.
- Open Source Advantage: Publishing this tool as open source will facilitate many studies, making them simpler and allowing researchers and industry professionals to focus on more advanced tasks.
- Continuous Improvement: New techniques will be added successively, ensuring continuous growth in this area.

## Features
- Crawler Implementation: Easily crawl specified websites with customizable depth and allowed domains.
- Network Analysis: Build and analyze networks of connected websites.
- Parameter Extraction: Extract a wide range of features for detailed analysis, each providerer returns Python dataclass for maintainability and easier process of adding new parameters, including:
 - HTML Content
 - DNS
 - HTTP Response
 - SSL Certificate
 - URL related geographical location
 - URL Lexical Analysis
 - WHOIS Integration
 - Google Index
 - Open Page Rank
 - Open Phish
 - Phish Tank
 - Similar Web
 - URL House

By using this library, you can easily collect and analyze almost 200 parameters to describe a website comprehensively.

### Html Content parameters
```python
@dataclass
class HtmlBodyFeatures:
    contains_forms: bool
    contains_obfuscated_scripts: bool
    contains_suspicious_keywords: bool
    body_length: int
    num_titles: int
    num_images: int
    num_links: int
    script_length: int
    special_characters: int
    script_to_special_chars_ratio: float
    script_to_body_ratio: float
    body_to_special_char_ratio: float
    iframe_redirection: int
    mouse_over_effect: int
    right_click_disabled: int
    num_scripts_http: int
    num_styles_http: int
    num_iframes_http: int
    num_external_scripts: int
    num_external_styles: int
    num_external_iframes: int
    num_meta_tags: int
    num_forms: int
    num_forms_post: int
    num_forms_get: int
    num_forms_external_action: int
    num_hidden_elements: int
    num_safe_anchors: int
    num_media_http: int
    num_media_external: int
    num_email_forms: int
    num_internal_links: int
    favicon_url: Optional[str]
    logo_url: Optional[str]
    found_forms: List[Dict[str, Any]] = field(default_factory=list)
    found_images: List[Dict[str, Any]] = field(default_factory=list)
    found_anchors: List[Dict[str, Any]] = field(default_factory=list)
    found_media: List[Dict[str, Any]] = field(default_factory=list)
    copyright: Optional[str] = None
```
### DNS parameters
```python
@dataclass
class DNSRecordFeatures:
    record_type: str
    ttl: int
    values: List[str]

```
### HTTP Response parameters
```python
@dataclass
class HttpResponseFeatures:
    redirects: bool
    redirect_count: int
    contains_forms: bool
    contains_obfuscated_scripts: bool
    contains_suspicious_keywords: bool
    uses_https: bool
    missing_x_frame_options: bool
    missing_x_xss_protection: bool
    missing_content_security_policy: bool
    missing_strict_transport_security: bool
    missing_x_content_type_options: bool
    is_live: bool
    server_version: Optional[str] = None
    body_length: int = 0
    num_titles: int = 0
    num_images: int = 0
    num_links: int = 0
    script_length: int = 0
    special_characters: int = 0
    script_to_special_chars_ratio: float = 0.0
    script_to_body_ratio: float = 0.0
    body_to_special_char_ratio: float = 0.0
```
### SSLCertificate
```python
@dataclass
class CertificateFeatures:
    subject: Dict[str, Any]
    issuer: Dict[str, Any]
    not_before: datetime
    not_after: datetime
    is_valid: bool
    validity_message: str
    is_trusted: bool
    trust_message: str

```
### URL related geographical location
```python
@dataclass
class URLGeoFeatures:
    url: str
    country_code: str
    asn: int
```
### URL Lexical Analysis
```python

@dataclass
class URLLexicalFeatures:
    count_dot_url: int
    count_dash_url: int
    count_underscore_url: int
    count_slash_url: int
    count_question_url: int
    count_equals_url: int
    count_at_url: int
    count_ampersand_url: int
    count_exclamation_url: int
    count_space_url: int
    count_tilde_url: int
    count_comma_url: int
    count_plus_url: int
    count_asterisk_url: int
    count_hash_url: int
    count_dollar_url: int
    count_percent_url: int
    url_length: int
    tld_amount_url: int
    count_dot_domain: int
    count_dash_domain: int
    count_underscore_domain: int
    count_slash_domain: int
    count_question_domain: int
    count_equals_domain: int
    count_at_domain: int
    count_ampersand_domain: int
    count_exclamation_domain: int
    count_space_domain: int
    count_tilde_domain: int
    count_comma_domain: int
    count_plus_domain: int
    count_asterisk_domain: int
    count_hash_domain: int
    count_dollar_domain: int
    count_percent_domain: int
    domain_length: int
    vowel_count_domain: int
    domain_in_ip_format: bool
    domain_contains_keywords: bool
    count_dot_directory: int
    count_dash_directory: int
    count_underscore_directory: int
    count_slash_directory: int
    count_question_directory: int
    count_equals_directory: int
    count_at_directory: int
    count_ampersand_directory: int
    count_exclamation_directory: int
    count_space_directory: int
    count_tilde_directory: int
    count_comma_directory: int
    count_plus_directory: int
    count_asterisk_directory: int
    count_hash_directory: int
    count_dollar_directory: int
    count_percent_directory: int
    directory_length: int
    count_dot_parameters: int
    count_dash_parameters: int
    count_underscore_parameters: int
    count_slash_parameters: int
    count_question_parameters: int
    count_equals_parameters: int
    count_at_parameters: int
    count_ampersand_parameters: int
    count_exclamation_parameters: int
    count_space_parameters: int
    count_tilde_parameters: int
    count_comma_parameters: int
    count_plus_parameters: int
    count_asterisk_parameters: int
    count_hash_parameters: int
    count_dollar_parameters: int
    count_percent_parameters: int
    parameters_length: int
    tld_presence_in_arguments: int
    number_of_parameters: int
    email_present_in_url: bool
    domain_entropy: float
    url_depth: int
    uses_shortening_service: Optional[str]
    is_ip: bool = False
```
### WHOIS Integration
```python
@dataclass
class WhoisFeatures:
    domain_name: List[str]
    registrar: Optional[str]
    whois_server: Optional[str]
    referral_url: Optional[str]
    updated_date: Optional[datetime]
    creation_date: Optional[datetime]
    expiration_date: Optional[datetime]
    name_servers: List[str]
    status: List[str]
    emails: List[str]
    dnssec: Optional[str]
    name: Optional[str]
    org: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zipcode: Optional[str]
    country: Optional[str]
    raw: Dict = field(default_factory=dict)
```
### Google Index
```python
@dataclass
class GoogleIndexFeatures:
    is_indexed: Optional[bool]
    position: Optional[int] = None
```
### Open Page Rank
```python
@dataclass
class OpenPageRankFeatures:
    domain: str
    page_rank_decimal: Optional[float]
    updated_date: Optional[str]
```
### Open Phish
```python
@dataclass
class OpenPhishFeatures:
    is_phishing: bool
```
### Phish Tank
```python
@dataclass
class PhishTankFeatures:
    phish_id: str
    url: str
    phish_detail_url: str
    submission_time: str
    verified: str
    verification_time: str
    online: str
    target: str
```
### Similar Web
```python
@dataclass
class SimilarWebFeatures:
    Version: int
    SiteName: str
    Description: str
    TopCountryShares: List[TopCountryShare]
    Title: str
    Engagements: Engagements
    EstimatedMonthlyVisits: List[EstimatedMonthlyVisit]
    GlobalRank: int
    CountryRank: int
    CountryCode: str
    CategoryRank: str
    Category: str
    LargeScreenshot: str
    TrafficSources: TrafficSource
    TopKeywords: List[TopKeyword]
    RawData: dict = field(default_factory=dict)
```
### URL Haus
```python
@dataclass
class URLHausFeatures:
    id: str
    date_added: str
    url: str
    url_status: str
    last_online: str
    threat: str
    tags: str
    urlhaus_link: str
    reporter: str
```
## Why Web2Vec?
While many scripts and solutions exist that perform some of the tasks offered by Web2Vec, none provide a complete all-in-one package. Web2Vec not only offers comprehensive functionality but also ensures maintainability and ease of use.

## Integration and Configuration
Web2Vec focuses on integration with free services, leveraging their APIs or scraping their responses. Configuration is handled via Python settings, making it easily configurable through traditional methods (environment variables, configuration files, etc.). Its integration with dedicated phishing detection services makes it a robust tool for building phishing detection datasets.


## How to use
Library can be installed using pip:

```bash
pip install web2vec
```

## Code usage
### Configuration
Configure the library using environment variables or configuration files.
```shell
export WEB2VEC_CRAWLER_SPIDER_DEPTH_LIMIT=2
export WEB2VEC_DEFAULT_OUTPUT_PATH=/home/admin/crawler/output
export WEB2VEC_OPEN_PAGE_RANK_API_KEY=XXXXX
```
### Crawling websites and extract parameters

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
        "DEPTH_LIMIT": 1,
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
and as a results you will get each processed page stored in a separate file as json with the following keys:
- url - processed url
- title - website title extracted from HTML
- html - HTTP response text attribute
- response_headers - HTTP response headers
- status_code - HTTP response status code
- extractors - dictionary with extractors results

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
### Website analysis
Websites can be analysed without scrapping process, by using extractors directly. For example to get data from SimilarWeb for given domain you have just to call appropriate method:

```python
from src.web2vec.extractors.external_api.similar_web_features import \
    get_similar_web_features

domain_to_check = "down.pcclear.com"
entry = get_similar_web_features(domain_to_check)
print(entry)
```

All modules are exported into main package, so you can use import module and invoke them directly.
```python
import web2vec as w2v

domain_to_check = "down.pcclear.com"
entry = w2v.get_similar_web_features(domain_to_check)
print(entry)
```


## Contributing

For contributing, refer to its [CONTRIBUTING.md](.github/CONTRIBUTING.md) file.
We are a welcoming community... just follow the [Code of Conduct](.github/CODE_OF_CONDUCT.md).

## Maintainers

Project maintainers are:

- Damian Frąszczak
- Edyta Frąszczak
