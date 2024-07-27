import logging
from dataclasses import dataclass, field
from functools import cache
from typing import List, Optional

import dns.resolver

from web2vec.utils import get_domain_from_url

logger = logging.getLogger(__name__)


@dataclass
class DNSRecordFeatures:
    record_type: str
    ttl: int
    values: List[str]


@dataclass
class DNSFeatures:
    domain: str
    records: List[DNSRecordFeatures] = field(default_factory=list)

    @property
    def count_ips(self) -> int:
        """Return the number of resolved IPs (IPv4)."""
        ip_records = [record for record in self.records if record.record_type == "A"]
        return len(ip_records[0].values) if ip_records else 0

    @property
    def count_name_servers(self) -> int:
        """Return number of NameServers (NS) resolved."""
        ns_records = [record for record in self.records if record.record_type == "NS"]
        return len(ns_records[0].values) if ns_records else 0

    @property
    def count_mx_servers(self) -> int:
        """Return number of resolved MX Servers."""
        mx_records = [record for record in self.records if record.record_type == "MX"]
        return len(mx_records[0].values) if mx_records else 0

    @property
    def extract_ttl(self) -> Optional[int]:
        """Return Time-to-live (TTL) value associated with hostname."""
        ttl_records = [
            record.ttl for record in self.records if record.record_type in ["A", "AAAA"]
        ]
        return ttl_records[0] if ttl_records else None


def get_dns_features(domain: str) -> DNSFeatures:
    """Get DNS features for the given domain."""
    dns_result = DNSFeatures(domain=domain)
    try:
        for record_type in ["A", "AAAA", "MX", "TXT", "NS", "CNAME"]:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                record_values = [rdata.to_text() for rdata in answers]
                ttl = answers.rrset.ttl
                dns_result.records.append(
                    DNSRecordFeatures(record_type, ttl, record_values)
                )
            except dns.resolver.NoAnswer:
                logger.warning(f"No {record_type} record found for {domain}")
            except dns.resolver.NXDOMAIN:
                print(f"{domain} does not exist")
            except Exception as e:  # noqa
                logger.warning(
                    f"Error fetching {record_type} records for {domain}: {e}", e
                )
    except Exception as e:  # noqa
        logger.warning(f"General error fetching DNS records for {domain}: {e}", e)
    return dns_result


@cache
def get_dns_features_cached(domain: str) -> DNSFeatures:
    """Get DNS features for the given domain."""
    return get_dns_features(domain)


if __name__ == "__main__":
    url = "https://www.example.com"
    domain = get_domain_from_url(url)
    result = get_dns_features(domain)
    print(result)
