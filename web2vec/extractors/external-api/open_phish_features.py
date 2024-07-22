import logging
from dataclasses import dataclass

import requests

from web2vec.processing.utils import fetch_file_from_url_and_read

logger = logging.getLogger(__name__)


@dataclass
class OpenPhishFeatures:
    is_phishing: bool


def get_open_phish_features(url: str) -> OpenPhishFeatures:
    """Check if the given URL is listed in the OpenPhish feed."""
    openphish_url = "https://openphish.com/feed.txt"

    try:
        text = fetch_file_from_url_and_read(openphish_url)
        urls = text.splitlines()

        for p_url in urls:
            if url in p_url:
                return OpenPhishFeatures(is_phishing=True)
        return OpenPhishFeatures(is_phishing=False)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching OpenPhish feed: {e}", e)
        return OpenPhishFeatures(is_phishing=False)


if __name__ == "__main__":
    url = "http://www.example.com"
    result = get_open_phish_features(url)
    print(f"{url} is phishing: {result.is_phishing}")
