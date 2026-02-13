import asyncio
import logging
from dataclasses import dataclass, field
from functools import cache
from typing import List, Optional, Tuple

import dns.asyncresolver
import dns.exception
import dns.resolver

from web2vec.config import config
from web2vec.utils import get_domain_from_url

logger = logging.getLogger(__name__)
DNS_RECORD_TYPES = ["A", "AAAA", "MX", "TXT", "NS", "CNAME"]
_ASYNC_RESOLVER: dns.asyncresolver.Resolver | None = None


@dataclass
class DNSRecordFeatures:
    record_type: str
    ttl: int
    values: List[str]


@dataclass
class DNSFeatures:
    domain: str
    records: List[DNSRecordFeatures] = field(default_factory=list)
    min_ttl: Optional[int] = field(init=False, default=None)
    ttl_expires_within_hour: Optional[bool] = field(init=False, default=None)
    ttl_expires_within_day: Optional[bool] = field(init=False, default=None)
    ttl_expires_within_week: Optional[bool] = field(init=False, default=None)

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

    def _address_record_ttls(self) -> List[int]:
        return [
            record.ttl
            for record in self.records
            if record.record_type in ["A", "AAAA"] and record.ttl is not None
        ]

    def compute_derived_features(self) -> None:
        """Populate TTL-based indicators for downstream ML usage."""
        ttl_values = self._address_record_ttls()
        self.min_ttl = min(ttl_values) if ttl_values else None

        if self.min_ttl is None:
            self.ttl_expires_within_hour = None
            self.ttl_expires_within_day = None
            self.ttl_expires_within_week = None
            return

        self.ttl_expires_within_hour = self.min_ttl <= 3600  # 1 hour
        self.ttl_expires_within_day = self.min_ttl <= 86400  # 24 hours
        self.ttl_expires_within_week = self.min_ttl <= 604800  # 7 days

    @property
    def extract_ttl(self) -> Optional[int]:
        """Return Time-to-live (TTL) value associated with hostname."""
        if self.min_ttl is not None:
            return self.min_ttl
        ttl_records = self._address_record_ttls()
        return ttl_records[0] if ttl_records else None


def _get_async_resolver() -> dns.asyncresolver.Resolver:
    global _ASYNC_RESOLVER
    if _ASYNC_RESOLVER is None:
        resolver = dns.asyncresolver.Resolver(configure=True)
        resolver.timeout = config.dns_resolver_timeout
        _ASYNC_RESOLVER = resolver
    return _ASYNC_RESOLVER


async def _resolve_record(
    domain: str, record_type: str
) -> Tuple[str, Optional[dns.resolver.Answer], Optional[Exception]]:
    resolver = _get_async_resolver()
    try:
        answers = await resolver.resolve(domain, record_type)
        return record_type, answers, None
    except Exception as exc:  # noqa
        return record_type, None, exc


async def _collect_records_async(domain: str):
    tasks = [_resolve_record(domain, record_type) for record_type in DNS_RECORD_TYPES]
    return await asyncio.gather(*tasks)


def _run_dns_tasks(domain: str):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_collect_records_async(domain))
    else:
        return loop.run_until_complete(_collect_records_async(domain))


def get_dns_features(domain: str) -> DNSFeatures:
    """Get DNS features for the given domain."""
    dns_result = DNSFeatures(domain=domain)
    try:
        results = _run_dns_tasks(domain)
        for record_type, answers, error in results:
            if answers:
                record_values = [rdata.to_text() for rdata in answers]
                ttl = answers.rrset.ttl
                dns_result.records.append(
                    DNSRecordFeatures(record_type, ttl, record_values)
                )
                continue

            if isinstance(error, dns.resolver.NoAnswer):
                logger.debug("No %s record found for %s", record_type, domain)
            elif isinstance(error, dns.resolver.NXDOMAIN):
                logger.warning("%s does not exist", domain)
            elif isinstance(error, dns.exception.Timeout):
                logger.warning(
                    "Timeout resolving %s record for %s: %s",
                    record_type,
                    domain,
                    error,
                )
            elif error:
                logger.warning(
                    "Error fetching %s records for %s: %s", record_type, domain, error
                )
    except Exception as e:  # noqa
        logger.warning("General error fetching DNS records for %s: %s", domain, e)
    dns_result.compute_derived_features()
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
