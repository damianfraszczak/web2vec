import logging
from dataclasses import dataclass
from functools import cache
from typing import Optional

import requests

from web2vec.config import config

logger = logging.getLogger(__name__)


@dataclass
class OpenPageRankFeatures:
    """Dataclass for Open PageRank features."""

    domain: str
    page_rank_decimal: Optional[float]
    updated_date: Optional[str]


class OpenPageRankAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://openpagerank.com/api/v1.0/getPageRank"

    def get_open_page_rank_features(
        self, domain: str
    ) -> Optional[OpenPageRankFeatures]:
        """Get Open PageRank features for the given domain."""
        headers = {"API-OPR": self.api_key}
        params = {"domains[]": domain}
        response = requests.get(
            self.base_url, headers=headers, params=params, timeout=config.api_timeout
        )

        if response.status_code == 200:
            data = response.json()
            if "response" in data and len(data["response"]) > 0:
                domain_data = data["response"][0]
                return OpenPageRankFeatures(
                    domain=domain_data["domain"],
                    page_rank_decimal=domain_data.get("page_rank_decimal"),
                    updated_date=data["last_updated"],
                )
            else:
                logger.warning("No data found for the specified domain.")
                return None
        else:
            response.raise_for_status()


def get_open_page_rank_features(domain: str) -> Optional[OpenPageRankFeatures]:
    """Get Open PageRank features for the given domain."""
    api_key = config.open_page_rank_api_key
    opr_api = OpenPageRankAPI(api_key)
    return opr_api.get_open_page_rank_features(domain)


@cache
def get_open_page_rank_features_cached(domain: str) -> Optional[OpenPageRankFeatures]:
    """Get Open PageRank features for the given domain (cached)."""
    return get_open_page_rank_features(domain)


if __name__ == "__main__":
    api_key = config.open_page_rank_api_key
    domain = "wp.pl"

    opr_api = OpenPageRankAPI(api_key)
    page_rank_data = opr_api.get_open_page_rank_features(domain)

    if page_rank_data:
        print(f"Domain: {page_rank_data.domain}")
        print(f"PageRank: {page_rank_data.page_rank_decimal}")
        print(f"Updated Date: {page_rank_data.updated_date}")
    else:
        print("Failed to retrieve PageRank data.")
