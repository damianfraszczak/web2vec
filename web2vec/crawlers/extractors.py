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
from web2vec.utils import get_domain_from_url


class Extractor:
    FEATURE_CLASS = None

    def extract_features(self, response: Response) -> object:
        raise NotImplementedError

    def features_name(self) -> str:
        return self.FEATURE_CLASS.__name__


class DNSExtractor(Extractor):
    FEATURE_CLASS = DNSFeatures

    def extract_features(self, response: Response) -> DNSFeatures:
        domain = get_domain_from_url(response.url)
        return get_dns_features_cached(domain)


class HtmlBodyExtractor(Extractor):
    FEATURE_CLASS = HtmlBodyFeatures

    def extract_features(self, response: Response) -> HtmlBodyFeatures:
        return get_html_body_features(body=response.text, url=response.url)


class HttpResponseExtractor(Extractor):
    FEATURE_CLASS = HttpResponseFeatures

    def extract_features(self, response: Response) -> HttpResponseFeatures:
        response.status_code = response.status
        return get_http_response_features(response=response)


class CertificateExtractor(Extractor):
    FEATURE_CLASS = CertificateFeatures

    def extract_features(self, response: Response) -> CertificateFeatures:
        return get_certificate_features_cached(
            hostname=get_domain_from_url(response.url)
        )


class UrlGeoExtractor(Extractor):
    FEATURE_CLASS = URLGeoFeatures

    def extract_features(self, response: Response) -> URLGeoFeatures:
        return get_url_geo_features_cached(url=response.url)


class UrlLexicalExtractor(Extractor):
    FEATURE_CLASS = URLLexicalFeatures

    def extract_features(self, response: Response) -> URLLexicalFeatures:
        return get_url_lexical_features_cached(url=response.url)


class WhoisExtractor(Extractor):
    FEATURE_CLASS = WhoisFeatures

    def extract_features(self, response: Response) -> WhoisFeatures:
        return get_whois_features_cached(domain=get_domain_from_url(response.url))


class GoogleIndexExtractor(Extractor):
    FEATURE_CLASS = GoogleIndexFeatures

    def extract_features(self, response: Response) -> GoogleIndexFeatures:
        return get_google_index_features(url=response.url)


class OpenPageRankExtractor(Extractor):
    FEATURE_CLASS = OpenPageRankFeatures

    def extract_features(self, response: Response) -> OpenPageRankFeatures:
        return get_open_page_rank_features_cached(
            domain=get_domain_from_url(response.url)
        )


class OpenPhishExtractor(Extractor):
    FEATURE_CLASS = OpenPhishFeatures

    def extract_features(self, response: Response) -> OpenPhishFeatures:
        return get_open_phish_features_cached(url=response.url)


class PhishTankExtractor(Extractor):
    FEATURE_CLASS = PhishTankFeatures

    def extract_features(self, response: Response) -> PhishTankFeatures:
        return get_phishtank_features_cached(domain=get_domain_from_url(response.url))


class SimilarWebExtractor(Extractor):
    FEATURE_CLASS = SimilarWebFeatures

    def extract_features(self, response: Response) -> SimilarWebFeatures:
        return get_similar_web_features_cached(domain=get_domain_from_url(response.url))


class UrlHausExtractor(Extractor):
    FEATURE_CLASS = URLHausFeatures

    def extract_features(self, response: Response) -> URLHausFeatures:
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
