import json
import logging
from dataclasses import dataclass

from requests import RequestException

from web2vec.utils import fetch_file_from_url, get_domain_from_url

logger = logging.getLogger(__name__)


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

    @property
    def domain(self) -> str:
        return get_domain_from_url(self.url)


def get_phishtank_feed(domain=None):
    """Get the PhishTank feed."""
    phishtank_url = "https://raw.githubusercontent.com/ProKn1fe/phishtank-database/master/online-valid.json"
    try:
        json_text, _ = fetch_file_from_url(phishtank_url)

        entries_data = json.loads(json_text)
        results = []
        for item in entries_data:
            if domain and domain != item["url"]:
                continue
            entry = PhishTankFeatures(
                phish_id=item["phish_id"],
                url=item["url"],
                phish_detail_url=item["phish_detail_url"],
                submission_time=item["submission_time"],
                verified=item["verified"],
                verification_time=item["verification_time"],
                online=item["online"],
                target=item["target"],
            )
            results.append(entry)
        return results

    except RequestException as e:
        logger.error(f"Error fetching PhishTank feed: {e}", e)
        return []


def check_phish_phishtank(domain: str) -> bool:
    """Check if the given domain is listed in the PhishTank feed."""
    entries = get_phishtank_feed()
    for entry in entries:
        if entry.domain == domain:
            return True
    return False


if __name__ == "__main__":
    domain = "allegrolokalnie.kategorie-baseny93.pl"
    is_phish = check_phish_phishtank(domain)
    print(f"{domain} is phishing: {is_phish}")
