import logging
from dataclasses import dataclass, field
from datetime import datetime
from functools import cache
from typing import Dict, List, Optional

import whois

logger = logging.getLogger(__name__)


@dataclass
class WhoisFeatures:
    domain_name: List[str]
    registrar: Optional[str]
    whois_server: Optional[str]
    referral_url: Optional[str]
    updated_date: Optional[datetime]
    creation_date: Optional[datetime]
    expiration_date: Optional[datetime]
    name_servers: List[str]
    status: List[str]
    emails: List[str]
    dnssec: Optional[str]
    name: Optional[str]
    org: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zipcode: Optional[str]
    country: Optional[str]
    raw: Dict = field(default_factory=dict)

    @property
    def domain_age(self):
        creation_date = self.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        age_days = (datetime.now() - creation_date).days if creation_date else 0
        return age_days


def get_whois_features(domain: str) -> Optional[WhoisFeatures]:
    """Fetch WHOIS data for a given domain."""
    try:
        w = whois.whois(domain)
        whois_data = WhoisFeatures(
            domain_name=(
                w.domain_name if isinstance(w.domain_name, list) else [w.domain_name]
            ),
            registrar=w.registrar,
            whois_server=w.whois_server,
            referral_url=w.referral_url,
            updated_date=w.updated_date,
            creation_date=w.creation_date,
            expiration_date=w.expiration_date,
            name_servers=(
                w.name_servers if isinstance(w.name_servers, list) else [w.name_servers]
            ),
            status=w.status if isinstance(w.status, list) else [w.status],
            emails=w.emails if isinstance(w.emails, list) else [w.emails],
            dnssec=w.dnssec,
            name=w.name,
            org=w.org,
            address=w.address,
            city=w.city,
            state=w.state,
            zipcode=w.zipcode,
            country=w.country,
            raw=w.__dict__,  # Store all raw data for reference
        )
        return whois_data
    except Exception as e:  # noqa
        logger.error(f"Error fetching WHOIS data: {e}", e)
        return None


@cache
def get_whois_features_cached(domain: str) -> WhoisFeatures:
    """Cache the WHOIS data for a given domain."""
    return get_whois_features(domain)


if __name__ == "__main__":
    domain = "example.com"
    whois_data = get_whois_features(domain)

    if whois_data:
        print(whois_data)
    else:
        print("Failed to retrieve WHOIS data.")
