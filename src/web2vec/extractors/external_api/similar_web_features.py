import logging
from dataclasses import dataclass, field
from functools import cache
from typing import List, Optional

import requests

from web2vec.config import config

logger = logging.getLogger(__name__)


@dataclass
class Engagements:
    BounceRate: float
    Month: int
    Year: int
    PagePerVisit: float
    Visits: int
    TimeOnSite: float


@dataclass
class TopCountryShare:
    Country: int
    CountryCode: str
    Value: float


@dataclass
class EstimatedMonthlyVisit:
    date: str
    visits: int


@dataclass
class TrafficSource:
    Social: float
    PaidReferrals: float
    Mail: float
    Referrals: float
    Search: float
    Direct: float


@dataclass
class TopKeyword:
    Name: str
    EstimatedValue: int
    Volume: int
    Cpc: Optional[float]


@dataclass
class SimilarWebFeatures:
    """Dataclass for SimilarWeb features."""

    Version: int
    SiteName: str
    Description: str
    TopCountryShares: List[TopCountryShare]
    Title: str
    Engagements: Engagements
    EstimatedMonthlyVisits: List[EstimatedMonthlyVisit]
    GlobalRank: int
    CountryRank: int
    CountryCode: str
    CategoryRank: str
    Category: str
    LargeScreenshot: str
    TrafficSources: TrafficSource
    TopKeywords: List[TopKeyword]
    RawData: dict = field(default_factory=dict)


def get_similar_web_features(domain: str) -> Optional[SimilarWebFeatures]:
    """Get SimilarWeb features for a given domain."""
    url = f"https://data.similarweb.com/api/v1/data?domain={domain}"  # noqa

    try:
        response = requests.get(
            url, headers={"User-Agent": "Mozilla/5.0"}, timeout=config.api_timeout
        )
        response.raise_for_status()
        data = response.json()

        top_country_shares = [
            TopCountryShare(**country) for country in data.get("TopCountryShares", [])
        ]

        engagements = Engagements(
            BounceRate=float(data["Engagments"]["BounceRate"]),
            Month=int(data["Engagments"]["Month"]),
            Year=int(data["Engagments"]["Year"]),
            PagePerVisit=float(data["Engagments"]["PagePerVisit"]),
            Visits=int(data["Engagments"]["Visits"]),
            TimeOnSite=float(data["Engagments"]["TimeOnSite"]),
        )

        estimated_monthly_visits = [
            EstimatedMonthlyVisit(date=k, visits=v)
            for k, v in data.get("EstimatedMonthlyVisits", {}).items()
        ]

        traffic_sources = TrafficSource(
            Social=data["TrafficSources"]["Social"],
            PaidReferrals=data["TrafficSources"]["Paid Referrals"],
            Mail=data["TrafficSources"]["Mail"],
            Referrals=data["TrafficSources"]["Referrals"],
            Search=data["TrafficSources"]["Search"],
            Direct=data["TrafficSources"]["Direct"],
        )

        top_keywords = [
            TopKeyword(**keyword) for keyword in data.get("TopKeywords", [])
        ]

        similarweb_data = SimilarWebFeatures(
            Version=data.get("Version", 0),
            SiteName=data.get("SiteName", ""),
            Description=data.get("Description", ""),
            TopCountryShares=top_country_shares,
            Title=data.get("Title", ""),
            Engagements=engagements,
            EstimatedMonthlyVisits=estimated_monthly_visits,
            GlobalRank=data["GlobalRank"]["Rank"],
            CountryRank=data["CountryRank"]["Rank"],
            CountryCode=data["CountryRank"]["CountryCode"],
            CategoryRank=data["CategoryRank"]["Rank"],
            Category=data.get("Category", ""),
            LargeScreenshot=data.get("LargeScreenshot", ""),
            TrafficSources=traffic_sources,
            TopKeywords=top_keywords,
            RawData=data,
        )
        return similarweb_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {e}", e)
        return None


@cache
def get_similar_web_features_cached(domain: str) -> Optional[SimilarWebFeatures]:
    """Get the SimilarWeb features for the given domain."""
    return get_similar_web_features(domain)


if __name__ == "__main__":
    domain_to_check = "down.pcclear.com"
    entry = get_similar_web_features(domain_to_check)
    print(entry)
