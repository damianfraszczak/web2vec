import logging
from dataclasses import asdict
from typing import List

logger = logging.getLogger(__name__)

from requests import Response as ReqResponse
from scrapy.http import Response

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
    transform_value,
)


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

    def extract_features(self, response: Response | ReqResponse) -> HtmlBodyFeatures:
        return get_html_body_features(body=response.text, url=response.url)


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
            except Exception as e:
                logger.warning(
                    f"Error extracting features with {extractor.features_name()}: {e}"
                )
    except Exception as e:
        logger.exception(e)
        logger.warning(f"Couldn't reach {url}.")
    return extractors_result
