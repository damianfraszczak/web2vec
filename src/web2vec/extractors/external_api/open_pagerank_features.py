import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import cache
from typing import Any, Dict, Iterator, List, Optional, Sequence

import requests

from web2vec.config import config

logger = logging.getLogger(__name__)

OPEN_PAGE_RANK_API_URL = "https://openpagerank.keywordseverywhere.com/v1/domains/bulk"
MAX_DOMAINS_PER_REQUEST = 100


@dataclass
class OpenPageRankHistoryEntry:
    """Dataclass for a single monthly Open PageRank measurement."""

    date: str
    open_page_rank: Optional[float]
    estimated: bool = False


@dataclass
class OpenPageRankQuota:
    """Dataclass for the quota reported by the Open PageRank API."""

    limit: Optional[int] = None
    remaining: Optional[int] = None
    reset: Optional[int] = None

    @property
    def reset_date(self) -> Optional[str]:
        """Get the quota reset moment as an ISO 8601 string."""
        if self.reset is None:
            return None
        return datetime.fromtimestamp(self.reset, tz=timezone.utc).isoformat()


@dataclass
class OpenPageRankFeatures:
    """Dataclass for Open PageRank features."""

    domain: str
    page_rank_decimal: Optional[float]
    updated_date: Optional[str]
    rank: Optional[int] = None
    referring_domains: Optional[int] = None
    found: bool = True
    history: List[OpenPageRankHistoryEntry] = field(default_factory=list)

    def page_rank_at(self, moment: str) -> Optional[OpenPageRankHistoryEntry]:
        """Get the newest history entry not younger than the given date."""
        entries = [entry for entry in self.history if entry.date <= moment]
        return max(entries, key=lambda entry: entry.date) if entries else None


def normalize_domain(domain: str) -> str:
    """Normalize a domain so that it can be used as a result key."""
    return domain.strip().lower()


def _chunked(
    domains: Sequence[str], size: int = MAX_DOMAINS_PER_REQUEST
) -> Iterator[List[str]]:
    """Split the domains into chunks accepted by a single API call."""
    for start in range(0, len(domains), size):
        yield list(domains[start : start + size])  # noqa: E203


def _parse_quota(headers: Any) -> OpenPageRankQuota:
    """Read the quota headers returned by the Open PageRank API."""

    def as_int(name: str) -> Optional[int]:
        try:
            return int(headers.get(name))
        except (AttributeError, TypeError, ValueError):
            return None

    return OpenPageRankQuota(
        limit=as_int("X-Domains-Limit"),
        remaining=as_int("X-Domains-Remaining"),
        reset=as_int("X-Domains-Reset"),
    )


def _parse_history(entries: Any) -> List[OpenPageRankHistoryEntry]:
    """Parse the monthly history of a domain, oldest entry first."""
    history = [
        OpenPageRankHistoryEntry(
            date=str(entry.get("date")),
            open_page_rank=entry.get("open_page_rank"),
            estimated=bool(entry.get("estimated", False)),
        )
        for entry in entries or []
        if entry.get("date")
    ]
    return sorted(history, key=lambda entry: entry.date)


def _parse_result(
    result: Dict[str, Any], updated_date: Optional[str]
) -> OpenPageRankFeatures:
    """Convert a single API result entry into features."""
    found = bool(result.get("found"))
    page_rank_decimal = result.get("open_page_rank") if found else None
    return OpenPageRankFeatures(
        domain=normalize_domain(str(result.get("domain", ""))),
        page_rank_decimal=page_rank_decimal,
        updated_date=updated_date,
        rank=result.get("rank"),
        referring_domains=result.get("referring_domains"),
        found=found,
        history=_parse_history(result.get("history")),
    )


def _not_found(domain: str) -> OpenPageRankFeatures:
    """Build features for a domain that is not present in the ranking."""
    return OpenPageRankFeatures(
        domain=domain,
        page_rank_decimal=None,
        updated_date=None,
        rank=None,
        referring_domains=None,
        found=False,
        history=[],
    )


class OpenPageRankAPI:
    """Client of the Open PageRank API hosted by Keywords Everywhere."""

    def __init__(self, api_key: str, include_history: bool = True):
        self.api_key = api_key
        self.base_url = OPEN_PAGE_RANK_API_URL
        self.include_history = include_history
        self.last_quota: Optional[OpenPageRankQuota] = None
        self.invalid_domains: List[str] = []

    def get_open_page_rank_features_bulk(
        self, domains: Sequence[str]
    ) -> Dict[str, OpenPageRankFeatures]:
        """Get Open PageRank features for many domains at once.

        Domains are deduplicated and sent in batches of at most
        ``MAX_DOMAINS_PER_REQUEST``. The result is keyed by the normalized
        domain and contains an entry for every requested domain except the
        ones rejected by the API, which are reported in ``invalid_domains``.
        """
        if not self.api_key:
            raise ValueError(
                "Open PageRank API key is missing, set "
                "WEB2VEC_OPEN_PAGE_RANK_API_KEY to use this extractor."
            )

        requested = sorted({normalize_domain(domain) for domain in domains if domain})
        self.invalid_domains = []
        features: Dict[str, OpenPageRankFeatures] = {}
        if not requested:
            return features

        for batch in _chunked(requested):
            features.update(self._request(batch))

        invalid = set(self.invalid_domains)
        for domain in requested:
            if domain not in features and domain not in invalid:
                logger.warning("No data found for domain %s.", domain)
                features[domain] = _not_found(domain)
        return features

    def get_open_page_rank_features(
        self, domain: str
    ) -> Optional[OpenPageRankFeatures]:
        """Get Open PageRank features for the given domain."""
        features = self.get_open_page_rank_features_bulk([domain])
        result = features.get(normalize_domain(domain))
        if result is None:
            logger.warning("No data found for the specified domain.")
        return result

    def _request(self, batch: List[str]) -> Dict[str, OpenPageRankFeatures]:
        """Fetch a single batch of at most 100 domains."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "domains": batch,
            "include_history": self.include_history,
        }
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=config.api_timeout,
        )
        response.raise_for_status()

        self.last_quota = _parse_quota(response.headers)
        self._log_quota(self.last_quota)

        data = response.json()
        invalid = data.get("invalid") or []
        if invalid:
            logger.warning("Open PageRank rejected domains: %s", invalid)
            self.invalid_domains.extend(
                normalize_domain(str(domain)) for domain in invalid
            )

        updated_date = data.get("as_of")
        features = {}
        for result in data.get("results") or []:
            entry = _parse_result(result, updated_date)
            if entry.domain:
                features[entry.domain] = entry
        return features

    @staticmethod
    def _log_quota(quota: OpenPageRankQuota) -> None:
        """Report the remaining monthly domain quota."""
        if quota.remaining is None:
            return
        message = "Open PageRank quota: %s of %s domains left, resets at %s"
        args = (quota.remaining, quota.limit, quota.reset_date)
        if quota.limit and quota.remaining <= quota.limit * 0.1:
            logger.warning(message, *args)
        else:
            logger.info(message, *args)


def get_open_page_rank_features(domain: str) -> Optional[OpenPageRankFeatures]:
    """Get Open PageRank features for the given domain."""
    api_key = config.open_page_rank_api_key
    opr_api = OpenPageRankAPI(api_key)
    return opr_api.get_open_page_rank_features(domain)


def get_open_page_rank_features_bulk(
    domains: Sequence[str],
) -> Dict[str, OpenPageRankFeatures]:
    """Get Open PageRank features for many domains, batched by 100."""
    api_key = config.open_page_rank_api_key
    opr_api = OpenPageRankAPI(api_key)
    return opr_api.get_open_page_rank_features_bulk(domains)


@cache
def get_open_page_rank_features_cached(domain: str) -> Optional[OpenPageRankFeatures]:
    """Get Open PageRank features for the given domain (cached)."""
    return get_open_page_rank_features(domain)


if __name__ == "__main__":
    api_key = config.open_page_rank_api_key

    opr_api = OpenPageRankAPI(api_key)
    page_rank_data = opr_api.get_open_page_rank_features("wp.pl")

    if page_rank_data:
        print(f"Domain: {page_rank_data.domain}")
        print(f"Found: {page_rank_data.found}")
        print(f"PageRank: {page_rank_data.page_rank_decimal}")
        print(f"Rank: {page_rank_data.rank}")
        print(f"Referring domains: {page_rank_data.referring_domains}")
        print(f"Updated Date: {page_rank_data.updated_date}")
        print(f"History entries: {len(page_rank_data.history)}")
    else:
        print("Failed to retrieve PageRank data.")

    bulk = opr_api.get_open_page_rank_features_bulk(["wp.pl", "github.com"])
    for entry in bulk.values():
        print(entry.domain, entry.found, entry.page_rank_decimal)
    print(f"Quota: {opr_api.last_quota}")
