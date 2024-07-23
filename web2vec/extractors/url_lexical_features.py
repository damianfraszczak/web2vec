import re
from dataclasses import dataclass
from functools import cache
from typing import Optional
from urllib.parse import parse_qs, urlparse

import tldextract

from web2vec.utils import entropy, fetch_file_from_url_and_read, valid_ip

shortening_services = (
    r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|"
    r"yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|"
    r"short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|"
    r"doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|db\.tt|"
    r"qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|"
    r"po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|"
    r"prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|"
    r"tr\.im|link\.zip\.net"
)


# Helper functions
def count_char(character: str, string: str) -> int:
    """Count the number of occurrences of the character in the string."""
    return string.count(character)


def count_vowels(string: str) -> int:
    """Count the number of vowels in the string."""
    return len(re.findall(r"[aeiouAEIOU]", string))


def contains_keywords(string: str, keywords: list) -> bool:
    """Check if the string contains any of the keywords."""
    return any(keyword in string.lower() for keyword in keywords)


def tld_count(string: str) -> int:
    """Count the number of times the TLD appears in the URL."""
    extracted = tldextract.extract(string)
    tld = extracted.suffix
    return string.lower().count(f".{tld}") if tld else 0


def url_depth(url):
    """Calculate the depth of the URL."""
    return len([segment for segment in urlparse(url).path.split("/") if segment])


def uses_shortening_service(url) -> Optional[str]:
    """Check if the URL uses a shortening service."""
    shortening_services_text = fetch_file_from_url_and_read(
        "https://raw.githubusercontent.com/korlabsio/urlshortener/main/names.txt"
    )
    shortening_services_list = shortening_services_text.split("\n")
    shortening_services_list = [
        service.strip() for service in shortening_services_list if service.strip()
    ]
    services_lookup = "|".join(map(re.escape, shortening_services_list))

    return re.search(services_lookup, url)


@dataclass
class URLLexicalFeatures:
    count_dot_url: int
    count_dash_url: int
    count_underscore_url: int
    count_slash_url: int
    count_question_url: int
    count_equals_url: int
    count_at_url: int
    count_ampersand_url: int
    count_exclamation_url: int
    count_space_url: int
    count_tilde_url: int
    count_comma_url: int
    count_plus_url: int
    count_asterisk_url: int
    count_hash_url: int
    count_dollar_url: int
    count_percent_url: int
    url_length: int
    tld_amount_url: int
    count_dot_domain: int
    count_dash_domain: int
    count_underscore_domain: int
    count_slash_domain: int
    count_question_domain: int
    count_equals_domain: int
    count_at_domain: int
    count_ampersand_domain: int
    count_exclamation_domain: int
    count_space_domain: int
    count_tilde_domain: int
    count_comma_domain: int
    count_plus_domain: int
    count_asterisk_domain: int
    count_hash_domain: int
    count_dollar_domain: int
    count_percent_domain: int
    domain_length: int
    vowel_count_domain: int
    domain_in_ip_format: bool
    domain_contains_keywords: bool
    count_dot_directory: int
    count_dash_directory: int
    count_underscore_directory: int
    count_slash_directory: int
    count_question_directory: int
    count_equals_directory: int
    count_at_directory: int
    count_ampersand_directory: int
    count_exclamation_directory: int
    count_space_directory: int
    count_tilde_directory: int
    count_comma_directory: int
    count_plus_directory: int
    count_asterisk_directory: int
    count_hash_directory: int
    count_dollar_directory: int
    count_percent_directory: int
    directory_length: int
    count_dot_parameters: int
    count_dash_parameters: int
    count_underscore_parameters: int
    count_slash_parameters: int
    count_question_parameters: int
    count_equals_parameters: int
    count_at_parameters: int
    count_ampersand_parameters: int
    count_exclamation_parameters: int
    count_space_parameters: int
    count_tilde_parameters: int
    count_comma_parameters: int
    count_plus_parameters: int
    count_asterisk_parameters: int
    count_hash_parameters: int
    count_dollar_parameters: int
    count_percent_parameters: int
    parameters_length: int
    tld_presence_in_arguments: int
    number_of_parameters: int
    email_present_in_url: bool
    domain_entropy: float
    url_depth: int
    uses_shortening_service: Optional[str]
    is_ip: bool = False


def get_url_lexical_features(url: str) -> URLLexicalFeatures:
    """Get the lexical features for the given URL."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path
    query = parsed_url.query
    directory = "/".join(path.split("/")[:-1])

    features = URLLexicalFeatures(
        count_dot_url=count_char(".", url),
        count_dash_url=count_char("-", url),
        count_underscore_url=count_char("_", url),
        count_slash_url=count_char("/", url),
        count_question_url=count_char("?", url),
        count_equals_url=count_char("=", url),
        count_at_url=count_char("@", url),
        count_ampersand_url=count_char("&", url),
        count_exclamation_url=count_char("!", url),
        count_space_url=count_char(" ", url),
        count_tilde_url=count_char("~", url),
        count_comma_url=count_char(",", url),
        count_plus_url=count_char("+", url),
        count_asterisk_url=count_char("*", url),
        count_hash_url=count_char("#", url),
        count_dollar_url=count_char("$", url),
        count_percent_url=count_char("%", url),
        url_length=len(url),
        tld_amount_url=tld_count(url),
        count_dot_domain=count_char(".", domain),
        count_dash_domain=count_char("-", domain),
        count_underscore_domain=count_char("_", domain),
        count_slash_domain=count_char("/", domain),
        count_question_domain=count_char("?", domain),
        count_equals_domain=count_char("=", domain),
        count_at_domain=count_char("@", domain),
        count_ampersand_domain=count_char("&", domain),
        count_exclamation_domain=count_char("!", domain),
        count_space_domain=count_char(" ", domain),
        count_tilde_domain=count_char("~", domain),
        count_comma_domain=count_char(",", domain),
        count_plus_domain=count_char("+", domain),
        count_asterisk_domain=count_char("*", domain),
        count_hash_domain=count_char("#", domain),
        count_dollar_domain=count_char("$", domain),
        count_percent_domain=count_char("%", domain),
        domain_length=len(domain),
        vowel_count_domain=count_vowels(domain),
        domain_in_ip_format=domain.replace(".", "").isdigit(),
        domain_contains_keywords=contains_keywords(domain, ["server", "client"]),
        count_dot_directory=count_char(".", directory),
        count_dash_directory=count_char("-", directory),
        count_underscore_directory=count_char("_", directory),
        count_slash_directory=count_char("/", directory),
        count_question_directory=count_char("?", directory),
        count_equals_directory=count_char("=", directory),
        count_at_directory=count_char("@", directory),
        count_ampersand_directory=count_char("&", directory),
        count_exclamation_directory=count_char("!", directory),
        count_space_directory=count_char(" ", directory),
        count_tilde_directory=count_char("~", directory),
        count_comma_directory=count_char(",", directory),
        count_plus_directory=count_char("+", directory),
        count_asterisk_directory=count_char("*", directory),
        count_hash_directory=count_char("#", directory),
        count_dollar_directory=count_char("$", directory),
        count_percent_directory=count_char("%", directory),
        directory_length=len(directory),
        count_dot_parameters=count_char(".", query),
        count_dash_parameters=count_char("-", query),
        count_underscore_parameters=count_char("_", query),
        count_slash_parameters=count_char("/", query),
        count_question_parameters=count_char("?", query),
        count_equals_parameters=count_char("=", query),
        count_at_parameters=count_char("@", query),
        count_ampersand_parameters=count_char("&", query),
        count_exclamation_parameters=count_char("!", query),
        count_space_parameters=count_char(" ", query),
        count_tilde_parameters=count_char("~", query),
        count_comma_parameters=count_char(",", query),
        count_plus_parameters=count_char("+", query),
        count_asterisk_parameters=count_char("*", query),
        count_hash_parameters=count_char("#", query),
        count_dollar_parameters=count_char("$", query),
        count_percent_parameters=count_char("%", query),
        parameters_length=len(query),
        tld_presence_in_arguments=tld_count(query),
        number_of_parameters=len(parse_qs(query)),
        email_present_in_url=bool(
            re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", url)
        ),
        domain_entropy=entropy(domain),
        url_depth=url_depth(url),
        uses_shortening_service=uses_shortening_service(url),
        is_ip=valid_ip(domain),
    )

    return features


@cache
def get_url_lexical_features_cached(url: str) -> URLLexicalFeatures:
    """Get the lexical features for the given URL."""
    return get_url_lexical_features(url)


# Example usage
if __name__ == "__main__":
    url = "https://192.1.10.1/path/to/file.html?arg1=val1&arg2=val2"
    features = get_url_lexical_features(url)
    print(features)
