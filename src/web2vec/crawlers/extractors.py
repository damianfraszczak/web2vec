import logging
import os
import time
from dataclasses import asdict
from typing import List

from requests import Response as ReqResponse
from scrapy.http import Response

from web2vec.config import config
from web2vec.extractors.dns_features import (
    DNSFeatures,
    get_dns_features_cached,
)
from web2vec.extractors.external_api.google_index_features import (
    GoogleIndexFeatures,
    get_google_index_features,
)
from web2vec.extractors.external_api.open_pagerank_features import (
    OpenPageRankFeatures,
    get_open_page_rank_features_cached,
)
from web2vec.extractors.external_api.open_phish_features import (
    OpenPhishFeatures,
    get_open_phish_features_cached,
)
from web2vec.extractors.external_api.phish_tank_features import (
    PhishTankFeatures,
    get_phishtank_features_cached,
)
from web2vec.extractors.external_api.similar_web_features import (
    SimilarWebFeatures,
    get_similar_web_features_cached,
)
from web2vec.extractors.external_api.url_haus_features import (
    URLHausFeatures,
    get_url_haus_features_cached,
)
from web2vec.extractors.html_body_features import (
    HtmlBodyFeatures,
    get_html_body_features,
)
from web2vec.extractors.http_response_features import (
    HttpResponseFeatures,
    get_http_response_features,
)
from web2vec.extractors.ssl_certification_features import (
    CertificateFeatures,
    get_certificate_features_cached,
)
from web2vec.extractors.url_geo_features import (
    URLGeoFeatures,
    get_url_geo_features_cached,
)
from web2vec.extractors.url_lexical_features import (
    URLLexicalFeatures,
    get_url_lexical_features_cached,
)
from web2vec.extractors.whois_features import (
    WhoisFeatures,
    get_whois_features_cached,
)
from web2vec.utils import (
    fetch_url,
    get_domain_from_url,
    is_numerical_type,
    sanitize_filename,
    transform_value,
)

logger = logging.getLogger(__name__)


class Extractor:
    FEATURE_CLASS = None
    FEATURE_TYPE = None

    def extract_features(
        self, response: Response | ReqResponse | ReqResponse
    ) -> FEATURE_CLASS:
        raise NotImplementedError

    def features_name(self) -> str:
        return self.FEATURE_CLASS.__name__


class DNSExtractor(Extractor):
    FEATURE_CLASS = DNSFeatures
    FEATURE_TYPE = "DNS"

    def extract_features(self, response: Response | ReqResponse) -> DNSFeatures:
        domain = get_domain_from_url(response.url)
        return get_dns_features_cached(domain)


class HtmlBodyExtractor(Extractor):
    FEATURE_CLASS = HtmlBodyFeatures
    FEATURE_TYPE = "HTML"

    def __init__(
        self,
        enable_js_render: bool = False,
        save_html_snapshot: bool = False,
        snapshot_output_dir: str | None = None,
        render_wait_seconds: float = 2.0,
    ) -> None:
        self.enable_js_render = enable_js_render
        self.save_html_snapshot = save_html_snapshot
        self.snapshot_output_dir = snapshot_output_dir
        self.render_wait_seconds = render_wait_seconds

    def _snapshot_dir(self) -> str:
        return self.snapshot_output_dir or os.path.join(
            config.crawler_output_path, "html_snapshots"
        )

    def _save_snapshot(self, html: str, url: str, rendered: bool) -> str | None:
        try:
            suffix = "_rendered" if rendered else "_raw"
            file_name = f"{sanitize_filename(url)}{suffix}.html"
            output_dir = self._snapshot_dir()
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, file_name)
            with open(output_path, "w", encoding="utf-8") as handle:
                handle.write(html)
            return output_path
        except Exception as exc:  # noqa
            logger.warning(f"Could not save HTML snapshot for {url}: {exc}")
            return None

    def _render_with_selenium(self, url: str) -> str | None:
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
        except Exception as exc:  # noqa
            logger.warning(f"Selenium rendering not available for {url}: {exc}")
            return None

        driver = None
        try:
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--allow-insecure-localhost")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(url)
            if self.render_wait_seconds > 0:
                time.sleep(self.render_wait_seconds)
            return driver.page_source
        except Exception as exc:  # noqa
            logger.warning(f"Selenium rendering failed for {url}: {exc}")
            return None
        finally:
            if driver:
                driver.quit()

    def extract_features(self, response: Response | ReqResponse) -> HtmlBodyFeatures:
        body = response.text
        source_mode = "raw_http"
        was_js_rendered = False

        if self.enable_js_render:
            rendered_body = self._render_with_selenium(response.url)
            if rendered_body:
                body = rendered_body
                source_mode = "selenium_rendered"
                was_js_rendered = True

        html_snapshot_path = None
        if self.save_html_snapshot:
            html_snapshot_path = self._save_snapshot(
                html=body, url=response.url, rendered=was_js_rendered
            )

        return get_html_body_features(
            body=body,
            url=response.url,
            source_mode=source_mode,
            was_js_rendered=was_js_rendered,
            html_snapshot_path=html_snapshot_path,
        )


class HttpResponseExtractor(Extractor):
    FEATURE_CLASS = HttpResponseFeatures
    FEATURE_TYPE = "HTTP"

    def extract_features(
        self, response: Response | ReqResponse
    ) -> HttpResponseFeatures:
        response.status_code = getattr(response, "status", response.status_code)
        url = response.url
        return get_http_response_features(response=response, url=url)


class CertificateExtractor(Extractor):
    FEATURE_CLASS = CertificateFeatures
    FEATURE_TYPE = "SSL"

    def extract_features(self, response: Response | ReqResponse) -> CertificateFeatures:
        return get_certificate_features_cached(
            hostname=get_domain_from_url(response.url)
        )


class UrlGeoExtractor(Extractor):
    FEATURE_CLASS = URLGeoFeatures
    FEATURE_TYPE = "GEO"

    def extract_features(self, response: Response | ReqResponse) -> URLGeoFeatures:
        return get_url_geo_features_cached(url=response.url)


class UrlLexicalExtractor(Extractor):
    FEATURE_CLASS = URLLexicalFeatures
    FEATURE_TYPE = "LEXICAL"

    def extract_features(self, response: Response | ReqResponse) -> URLLexicalFeatures:
        return get_url_lexical_features_cached(url=response.url)


class WhoisExtractor(Extractor):
    FEATURE_CLASS = WhoisFeatures
    FEATURE_TYPE = "WHOIS"

    def extract_features(self, response: Response | ReqResponse) -> WhoisFeatures:
        return get_whois_features_cached(domain=get_domain_from_url(response.url))


class GoogleIndexExtractor(Extractor):
    FEATURE_CLASS = GoogleIndexFeatures
    FEATURE_TYPE = "GOOGLE_INDEX"

    def extract_features(self, response: Response | ReqResponse) -> GoogleIndexFeatures:
        return get_google_index_features(url=response.url)


class OpenPageRankExtractor(Extractor):
    FEATURE_CLASS = OpenPageRankFeatures
    FEATURE_TYPE = "OPEN_PAGE_RANK"

    def extract_features(
        self, response: Response | ReqResponse
    ) -> OpenPageRankFeatures:
        return get_open_page_rank_features_cached(
            domain=get_domain_from_url(response.url)
        )


class OpenPhishExtractor(Extractor):
    FEATURE_CLASS = OpenPhishFeatures
    FEATURE_TYPE = "OPEN_PHISH"

    def extract_features(self, response: Response | ReqResponse) -> OpenPhishFeatures:
        return get_open_phish_features_cached(url=response.url)


class PhishTankExtractor(Extractor):
    FEATURE_CLASS = PhishTankFeatures
    FEATURE_TYPE = "PHISH_TANK"

    def extract_features(self, response: Response | ReqResponse) -> PhishTankFeatures:
        return get_phishtank_features_cached(domain=get_domain_from_url(response.url))


class SimilarWebExtractor(Extractor):
    FEATURE_CLASS = SimilarWebFeatures
    FEATURE_TYPE = "SIMILAR_WEB"

    def extract_features(self, response: Response | ReqResponse) -> SimilarWebFeatures:
        return get_similar_web_features_cached(domain=get_domain_from_url(response.url))


class UrlHausExtractor(Extractor):
    FEATURE_CLASS = URLHausFeatures
    FEATURE_TYPE = "URL_HAUS"

    def extract_features(self, response: Response | ReqResponse) -> URLHausFeatures:
        return get_url_haus_features_cached(domain=get_domain_from_url(response.url))


ALL_EXTRACTORS = [
    DNSExtractor(),
    HtmlBodyExtractor(),
    HttpResponseExtractor(),
    CertificateExtractor(),
    UrlGeoExtractor(),
    UrlLexicalExtractor(),
    WhoisExtractor(),
    GoogleIndexExtractor(),
    OpenPageRankExtractor(),
    OpenPhishExtractor(),
    PhishTankExtractor(),
    SimilarWebExtractor(),
    UrlHausExtractor(),
]


def process_extractors(
    url: str, extractors: List[Extractor], use_only_numerical: bool = False
) -> dict:
    """Process a list of extractors for a given URL."""
    extractors_result = {}
    try:
        response = fetch_url(url)

        for extractor in extractors:
            try:
                result = extractor.extract_features(response)
                result_as_dict = asdict(result)
                extractors_result.update(
                    {
                        f"{extractor.FEATURE_TYPE}_{key}": transform_value(value)
                        for key, value in result_as_dict.items()
                        if not use_only_numerical or is_numerical_type(value)
                    }
                )
            except Exception as e:  # noqa
                logger.warning(
                    f"Error extracting features with {extractor.features_name()}: {e}"
                )
    except Exception as e:  # noqa
        logger.warning(f"Couldn't reach {url}. {e}")
    return extractors_result
