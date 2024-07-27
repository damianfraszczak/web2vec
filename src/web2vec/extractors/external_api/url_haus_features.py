import csv
import logging
from dataclasses import asdict, dataclass
from functools import cache
from io import StringIO
from typing import Generator, Optional

import requests

from web2vec.utils import fetch_file_from_url_and_read, get_domain_from_url

logger = logging.getLogger(__name__)


@dataclass
class URLHausFeatures:
    """Dataclass for URLHaus features."""

    id: str
    date_added: str
    url: str
    url_status: str
    last_online: str
    threat: str
    tags: str
    urlhaus_link: str
    reporter: str

    @property
    def domain(self) -> str:
        return get_domain_from_url(self.url)


def get_url_haus_features(domain: Optional[str] = None) -> Generator:
    """Get the url features for given domain."""
    urlhaus_url = "https://urlhaus.abuse.ch/downloads/csv_online/"
    try:
        # Get the current directory
        response_text = fetch_file_from_url_and_read(urlhaus_url)

        csv_data = StringIO(response_text)
        csv_reader = csv.reader(csv_data, delimiter=",")

        # Skip CSV headers
        for _ in range(9):
            next(csv_reader, None)

        for row in csv_reader:
            url = row[2]
            processing_domain = get_domain_from_url(url)
            if domain and processing_domain != domain:
                continue
            entry = URLHausFeatures(
                id=row[0],
                date_added=row[1],
                url=url,
                url_status=row[3],
                last_online=row[4],
                threat=row[5],
                tags=row[6],
                urlhaus_link=row[7],
                reporter=row[8],
            )
            yield entry

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URLHaus feed: {e}")
        return []


@cache
def get_url_haus_features_cached(domain: Optional[str] = None) -> URLHausFeatures:
    """Get the URLHaus features for the given domain."""
    return next(get_url_haus_features(domain), None)


if __name__ == "__main__":
    domain_to_check = "down.pcclear.com"
    entry = get_url_haus_features_cached(domain_to_check)
    print(f"Entry found - {asdict(entry)}")
