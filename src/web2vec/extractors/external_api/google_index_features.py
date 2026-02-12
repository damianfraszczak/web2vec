import logging
from dataclasses import dataclass
from functools import cache
from typing import Optional

import requests

from web2vec.config import config

logger = logging.getLogger(__name__)


@dataclass
class GoogleIndexFeatures:
    """Dataclass for Google index features."""

    is_indexed: Optional[bool]
    position: Optional[int] = None


def get_google_index_features(url: str) -> GoogleIndexFeatures:
    """Check if the given URL is indexed by Brave Search and return its position."""
    api_key = config.brave_search_api_key
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key,
    }
    query = f"site:{url}"  # noqa
    api_url = f"https://api.search.brave.com/res/v1/web/search?q={query}"  # noqa

    try:
        response = requests.get(api_url, headers=headers, timeout=config.api_timeout)
        response.raise_for_status()
        data = response.json()
        results = data.get("web", {}).get("results", [])
        for index, result in enumerate(results, start=1):
            link = result.get("url", "")
            if url in link:
                return GoogleIndexFeatures(is_indexed=True, position=index)
        return GoogleIndexFeatures(is_indexed=False, position=None)
    except Exception as e:  # noqa
        logger.error(f"Error checking Brave index: {e}", exc_info=True)
        return GoogleIndexFeatures(is_indexed=None, position=None)


@cache
def get_google_index_features_cached(url: str) -> GoogleIndexFeatures:
    """Get the Brave index features for the given URL."""
    return get_google_index_features(url)


if __name__ == "__main__":
    url = "wp.pl"
    result = get_google_index_features(url)
    if result.is_indexed is None:
        print(f"Error checking {url}.")
    else:
        print(f"Is {url} indexed by Brave? {'Yes' if result.is_indexed else 'No'}")
        if result.is_indexed:
            print(f"Position in search results: {result.position}")
