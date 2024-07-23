import json
import logging
from dataclasses import dataclass
from functools import cache
from typing import Optional

from requests import RequestException

from web2vec.utils import fetch_file_from_url_and_read, get_domain_from_url

logger = logging.getLogger(__name__)


@dataclass
class PhishTankFeatures:
    """Dataclass for PhishTank features."""

    phish_id: str
    url: str
    phish_detail_url: str
    submission_time: str
    verified: str
    verification_time: str
    online: str
    target: str

    @property
    def domain(self) -> str:
        return get_domain_from_url(self.url)


def get_phishtank_feed():
    """Get the PhishTank feed."""
    phishtank_url = "https://raw.githubusercontent.com/ProKn1fe/phishtank-database/master/online-valid.json"
    try:
        json_text = fetch_file_from_url_and_read(phishtank_url)

        entries_data = json.loads(json_text)
        for item in entries_data:
            yield PhishTankFeatures(
                phish_id=item["phish_id"],
                url=item["url"],
                phish_detail_url=item["phish_detail_url"],
                submission_time=item["submission_time"],
                verified=item["verified"],
                verification_time=item["verification_time"],
                online=item["online"],
                target=item["target"],
            )

    except RequestException as e:
        logger.error(f"Error fetching PhishTank feed: {e}", e)
        return None


def get_phishtank_features(domain: str) -> Optional[PhishTankFeatures]:
    """Get PhishTank features for the given domain."""
    entries = get_phishtank_feed()
    for entry in entries:
        if entry.domain == domain:
            return entry
    return None


@cache
def get_phishtank_features_cached(domain: str) -> Optional[PhishTankFeatures]:
    """Get PhishTank features for the given domain."""
    return get_phishtank_features(domain)


def check_phish_phishtank(domain: str) -> bool:
    """Check if the given domain is listed in the PhishTank feed."""
    entries = get_phishtank_feed()
    for entry in entries:
        if entry.domain == domain:
            return True
    return False


if __name__ == "__main__":
    domain = "allegrolokalnie.kategorie-baseny93.pl"
    entry = get_phishtank_features_cached(domain)
    print(f"{domain} is phishing: {entry}")
