import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from functools import cache
from typing import Dict, List, Optional

import whois

logger = logging.getLogger(__name__)

WHOIS_DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S%z",
    "%d-%b-%Y",
    "%d-%b-%Y %H:%M:%S",
    "%Y/%m/%d",
    "%Y.%m.%d",
    "%d.%m.%Y",
)


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
    creation_datetime: Optional[datetime] = field(init=False, default=None)
    expiration_datetime: Optional[datetime] = field(init=False, default=None)
    domain_age_days: Optional[int] = field(init=False, default=None)
    days_until_expiration: Optional[int] = field(init=False, default=None)
    expires_within_7_days: Optional[bool] = field(init=False, default=None)
    expires_within_30_days: Optional[bool] = field(init=False, default=None)
    created_within_30_days: Optional[bool] = field(init=False, default=None)
    created_within_365_days: Optional[bool] = field(init=False, default=None)
    is_expired: Optional[bool] = field(init=False, default=None)

    def __post_init__(self) -> None:
        self.creation_datetime = self._normalize_datetime(self.creation_date)
        self.expiration_datetime = self._normalize_datetime(self.expiration_date)
        now = datetime.utcnow()

        if self.creation_datetime:
            age_delta = now - self.creation_datetime
            self.domain_age_days = age_delta.days
            self.created_within_30_days = age_delta <= timedelta(days=30)
            self.created_within_365_days = age_delta <= timedelta(days=365)
        else:
            self.domain_age_days = None
            self.created_within_30_days = None
            self.created_within_365_days = None

        if self.expiration_datetime:
            expiration_delta = self.expiration_datetime - now
            self.days_until_expiration = expiration_delta.days
            self.is_expired = expiration_delta.total_seconds() < 0
            self.expires_within_7_days = 0 <= expiration_delta.days <= 7
            self.expires_within_30_days = 0 <= expiration_delta.days <= 30
        else:
            self.days_until_expiration = None
            self.is_expired = None
            self.expires_within_7_days = None
            self.expires_within_30_days = None

    @property
    def domain_age(self):
        if self.domain_age_days is not None:
            return self.domain_age_days
        creation_date = self._normalize_datetime(self.creation_date)
        age_days = (datetime.utcnow() - creation_date).days if creation_date else 0
        if creation_date:
            self.domain_age_days = age_days
        return age_days

    @staticmethod
    def _normalize_datetime(
        value: Optional[datetime | List[datetime] | str],
    ) -> Optional[datetime]:
        if isinstance(value, list):
            for entry in value:
                normalized = WhoisFeatures._normalize_datetime(entry)
                if normalized:
                    return normalized
            return None
        if isinstance(value, tuple):
            for entry in value:
                normalized = WhoisFeatures._normalize_datetime(entry)
                if normalized:
                    return normalized
            return None
        if isinstance(value, datetime):
            return WhoisFeatures._ensure_utc_naive(value)
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                return None
            iso_candidate = cleaned.replace("Z", "+00:00")
            try:
                parsed = datetime.fromisoformat(iso_candidate)
                return WhoisFeatures._ensure_utc_naive(parsed)
            except ValueError:
                pass
            for fmt in WHOIS_DATE_FORMATS:
                try:
                    parsed = datetime.strptime(cleaned, fmt)
                    return WhoisFeatures._ensure_utc_naive(parsed)
                except ValueError:
                    continue
        return None

    @staticmethod
    def _ensure_utc_naive(value: datetime) -> datetime:
        if value.tzinfo:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value


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
