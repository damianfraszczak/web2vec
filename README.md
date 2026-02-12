<p align="center"><img src=".github/images/logo.png" width="256" alt="web2vec" title="web2vec"/></p>

<h1 align="center">
    ⚔️ Web2Vec: A Python Library for Website-to-Vector Transformation ⚔️
</h1>

<p align="center">
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/web2vec.svg">
    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/web2vec.svg" href="https://pepy.tech/project/web2vec">
    <a href="https://repology.org/project/python:web2vec/versions">
        <img src="https://repology.org/badge/tiny-repos/python:web2vec.svg" alt="Packaging status">
    </a>
    <img alt="Downloads" src="https://pepy.tech/badge/web2vec">
    <img alt="GitHub license" src="https://img.shields.io/github/license/damianfraszczak/web2vec.svg" href="https://github.com/damianfraszczak/web2vec/blob/master/LICENSE">
    <img alt="Documentation Status" src="https://readthedocs.org/projects/web2vec/badge/?version=latest" href="https://web2vec.readthedocs.io/en/latest/?badge=latest">
</p>

<p align="center">
  <a href="https://github.com/damianfraszczak/web2vec?tab=readme-ov-file#why-web2vec">✨ Why Web2Vec?</a>
  <a href="https://github.com/damianfraszczak/web2vec?tab=readme-ov-file#features">📦 Features</a>
<a href="https://github.com/damianfraszczak/web2vec/blob/master/docs/files/QUICK_START.md">🚀 Quick Start</a>
  <a href="https://github.com/damianfraszczak/web2vec?tab=readme-ov-file#integration-and-configuration">🧑‍💻 Installation and configuration</a>
  <a href="https://web2vec.readthedocs.io/">📮 Documentation</a>
  <a href="https://github.com/damianfraszczak/web2vec/blob/master/docs/files/jupyter">📓 Jupyter Notebook examples</a>
  <a href="LICENSE">🔑 License</a>
</p>

Web2Vec is a comprehensive library designed to convert websites into vector parameters. It provides ready-to-use implementations of web crawlers using Scrapy, making it accessible for less experienced researchers. This tool is invaluable for website analysis tasks, including SEO, disinformation detection, and phishing identification.

Website analysis is crucial in various fields, such as SEO, where it helps improve website ranking, and in security, where it aids in identifying phishing sites. By building datasets based on known safe and malicious websites, Web2Vec facilitates the collection and analysis of their parameters, making it an ideal solution for these tasks.

The goal of Web2Vec is to offer a comprehensive repository for implementing a broad spectrum of website processing-related methods. Many available tools exist, but learning and using them can be time-consuming. Moreover, new features are continually being introduced, making it difficult to keep up with the latest techniques. Web2Vec aims to bridge this gap by providing a complete solution for website analysis. This repository facilitates the collection and analysis of extensive information about websites, supporting both academic research and industry applications.

**If you use Web2Vec as support to your research consider citing:**


``
D. Frąszczak, E. Frąszczak. Web2Vec: A python library for website-to-vector transformation. SoftwareX. 2025. `` DOI:[10.1016/j.softx.2025.102070](https://doi.org/10.1016/j.softx.2025.102070).


* **Free software:** MIT license,
* **Documentation:** https://web2vec.readthedocs.io/en/latest/,
* **Python versions:** 3.9 | 3.10 | 3.11
* **Tested OS:** Windows, Ubuntu, Fedora and CentOS. **However, that does not mean it does not work on others.**
* **All-in-One Solution::**  Web2Vec is an all-in-one solution that allows for the collection of a wide range of information about websites.
* **Efficiency and Expertise: :** Building a similar solution independently would be very time-consuming and require specialized knowledge. Web2Vec not only integrates with available APIs but also checks site indexation using the Brave Search API.
* **Open Source Advantage: :** Publishing this tool as open source will facilitate many studies, making them simpler and allowing researchers and industry professionals to focus on more advanced tasks.
* **Continuous Improvement: :** New techniques will be added successively, ensuring continuous growth in this area.

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
- Temporal Risk Signals: Derived TTL, creation, and expiration proximity indicators across DNS, WHOIS, and SSL outputs to plug directly into ML pipelines.

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

@dataclass
class DNSFeatures:
    domain: str
    records: List[DNSRecordFeatures]
    min_ttl: Optional[int]
    ttl_expires_within_hour: Optional[bool]
    ttl_expires_within_day: Optional[bool]
    ttl_expires_within_week: Optional[bool]

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
    issuer_common_name: Optional[str]
    issuer_organization_name: Optional[str]
    issuer_is_lets_encrypt: Optional[bool]
    issuer_is_free_ca: Optional[bool]
    validity_duration_days: Optional[int]
    days_until_expiration: Optional[int]
    expires_within_7_days: Optional[bool]
    expires_within_30_days: Optional[bool]
    valid_in_7_days: Optional[bool]
    valid_in_30_days: Optional[bool]
    is_expired: Optional[bool]

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
    creation_datetime: Optional[datetime] = None
    expiration_datetime: Optional[datetime] = None
    domain_age_days: Optional[int] = None
    days_until_expiration: Optional[int] = None
    expires_within_7_days: Optional[bool] = None
    expires_within_30_days: Optional[bool] = None
    created_within_30_days: Optional[bool] = None
    created_within_365_days: Optional[bool] = None
    is_expired: Optional[bool] = None
```
### Google Index
```python
@dataclass
class GoogleIndexFeatures:
    is_indexed: Optional[bool]
    position: Optional[int] = None
```
*Note: As of July 2024, the Google Index feature is now powered by the Brave Search API. It checks if a site is indexed in Brave Search, which is a large, independent web index. You need a Brave Search API key to use this feature.*

#### Configuration for Brave Search API
Set your Brave Search API key as an environment variable:
```shell
export WEB2VEC_BRAVE_SEARCH_API_KEY=YOUR_API_KEY
```

The extractor will use this key automatically. See https://api.search.brave.com/ for details on obtaining a key.

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
export WEB2VEC_BRAVE_SEARCH_API_KEY=XXXXX
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
    "html": "HTML body, removed too big to show",
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

## Testing
Run the extractor-focused unit tests to make sure recent DNS/WHOIS/SSL additions and supporting modules behave deterministically:
```bash
python -m pytest tests/test_dns_features.py \
                 tests/test_whois_features.py \
                 tests/test_ssl_certification_features.py \
                 tests/test_html_body_features.py \
                 tests/test_http_response_features.py \
                 tests/test_network_features.py \
                 tests/test_url_geo_features.py \
                 tests/test_url_lexical_features.py
```
Each extractor now has a dedicated test module so regressions in derived properties (e.g., TTL proximity flags or certificate issuer signals) are caught quickly.


## Contributing

For contributing, refer to its [CONTRIBUTING.md](.github/CONTRIBUTING.md) file.
We are a welcoming community... just follow the [Code of Conduct](.github/CODE_OF_CONDUCT.md).

## Maintainers

Project maintainers are:

- Damian Frąszczak
- Edyta Frąszczak
- Krystian Magdziarz
