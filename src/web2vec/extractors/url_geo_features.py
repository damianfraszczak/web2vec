import logging
from dataclasses import dataclass
from enum import Enum
from functools import cache
from typing import Dict, Optional, Union

import geoip2.database

from web2vec.utils import (
    fetch_file_from_url,
    get_github_repo_release_info,
    get_ip_from_url,
)

logger = logging.getLogger(__name__)


class GeoLiteDbType(Enum):
    COUNTRY = "GeoLite2-Country"
    ASN = "GeoLite2-ASN"


@dataclass
class URLGeoFeatures:
    url: str
    country_code: str
    asn: int


def get_geolite_db_files(
    type: Optional[GeoLiteDbType] = None,
) -> Union[Dict[GeoLiteDbType, str], str]:
    """Download the latest GeoLite2-Country and GeoLite2-ASN database files from GitHub."""
    repo = "PrxyHunter/GeoLite2"
    release_info = get_github_repo_release_info(repo)
    result = {}
    for db_type in GeoLiteDbType:
        asset_name = f"{db_type.value}.mmdb"
        for asset in release_info["assets"]:
            if asset["name"] == asset_name:
                file_path = fetch_file_from_url(asset["browser_download_url"])
                result[db_type] = file_path
    if type:
        return result[type]
    return result


def get_country(ip_address: str) -> Optional[str]:
    """Return the country code associated with the given IP address."""
    try:
        path = get_geolite_db_files(GeoLiteDbType.COUNTRY)
        with geoip2.database.Reader(path) as reader:
            response = reader.country(ip_address)
            return response.country.iso_code
    except Exception as e:  # noqa
        logger.error(f"Error retrieving country for IP {ip_address}: {e}", e)
        return None


def get_asn(ip_address: str) -> Optional[int]:
    """Return the ASN associated with the given IP address."""
    try:
        path = get_geolite_db_files(GeoLiteDbType.ASN)
        with geoip2.database.Reader(path) as reader:
            response = reader.asn(ip_address)
            return response.autonomous_system_number
    except Exception as e:  # noqa
        logger.error(f"Error retrieving ASN for IP {ip_address}: {e}", e)
        return None


def get_url_geo_features(url: str) -> URLGeoFeatures:
    """Return information about the given URL."""
    ip_address = get_ip_from_url(url)
    country_code = get_country(ip_address)
    asn = get_asn(ip_address)

    return URLGeoFeatures(
        url=url,
        country_code=country_code,
        asn=asn,
    )


@cache
def get_url_geo_features_cached(url: str) -> URLGeoFeatures:
    """Get the geo features for the given URL."""
    return get_url_geo_features(url)


if __name__ == "__main__":
    # Example usage
    url = "https://example.com"
    info = get_url_geo_features(url)
    print(info)
