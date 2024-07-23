import logging
from dataclasses import dataclass
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from web2vec.config import config

logger = logging.getLogger(__name__)


@dataclass
class HttpResponseFeatures:
    redirects: bool
    redirect_count: int
    contains_forms: bool
    contains_obfuscated_scripts: bool
    contains_suspicious_keywords: bool
    uses_https: bool
    missing_x_frame_options: bool
    missing_x_xss_protection: bool
    missing_content_security_policy: bool
    missing_strict_transport_security: bool
    missing_x_content_type_options: bool
    is_live: bool
    server_version: Optional[str] = None
    body_length: int = 0
    num_titles: int = 0
    num_images: int = 0
    num_links: int = 0
    script_length: int = 0
    special_characters: int = 0
    script_to_special_chars_ratio: float = 0.0
    script_to_body_ratio: float = 0.0
    body_to_special_char_ratio: float = 0.0


def check_redirects(response: requests.Response) -> bool:
    """Check if the response has been redirected."""
    return len(getattr(response, "history", [])) > 0


def count_redirects(response: requests.Response) -> int:
    """Count the number of redirects in the response."""
    return len(getattr(response, "history", []))


def check_forms(response: requests.Response) -> bool:
    """Check if the response contains any forms."""
    soup = BeautifulSoup(response.text, "html.parser")
    return bool(soup.find_all("form"))


def check_obfuscated_scripts(response: requests.Response) -> bool:
    """Check if the response contains any obfuscated scripts."""
    soup = BeautifulSoup(response.text, "html.parser")
    scripts = soup.find_all("script")
    for script in scripts:
        if script.get("src") and (
            "eval(" in script["src"] or "document.write(" in script["src"]
        ):
            return True
    return False


def check_suspicious_keywords(
    response: requests.Response, keywords: Optional[List[str]] = None
) -> bool:
    """Check if the response contains any suspicious keywords."""
    suspicious_keywords = keywords or [
        "login",
        "update",
        "verify",
        "password",
        "bank",
        "account",
    ]
    page_content = response.text.lower()
    return any(keyword in page_content for keyword in suspicious_keywords)


def check_https(response: requests.Response) -> bool:
    """Check if the response uses HTTPS."""
    return response.url.startswith("https://")


def check_header_x_frame_options(response: requests.Response) -> bool:
    """Check if the response is missing the X-Frame-Options header."""
    return "X-Frame-Options" not in response.headers


def check_header_x_xss_protection(response: requests.Response) -> bool:
    """Check if the response is missing the X-XSS-Protection header"""
    return "X-XSS-Protection" not in response.headers


def check_header_content_security_policy(response: requests.Response) -> bool:
    """Check if the response is missing the Content-Security-Policy header."""
    return "Content-Security-Policy" not in response.headers


def check_header_strict_transport_security(response: requests.Response) -> bool:
    """Check if the response is missing the Strict-Transport-Security"""
    return "Strict-Transport-Security" not in response.headers


def check_header_x_content_type_options(response: requests.Response) -> bool:
    """Check if the response is missing the X-Content-Type-Options"""
    return "X-Content-Type-Options" not in response.headers


def is_live(response: requests.Response) -> bool:
    """Check if the response is live."""
    return response.status_code == 200


def check_server_version(response: requests.Response) -> Optional[str]:
    """Check the server version of the response."""
    return response.headers.get("Server")


def body_length(response: requests.Response) -> int:
    """Get the length of the body of the response."""
    soup = BeautifulSoup(response.text, "html.parser")
    return len(soup.get_text())


def num_titles(response: requests.Response) -> int:
    """Get the number of titles in the response."""
    soup = BeautifulSoup(response.text, "html.parser")
    titles = ["h{}".format(i) for i in range(7)]
    titles = [soup.find_all(tag) for tag in titles]
    return len([item for sublist in titles for item in sublist])


def num_images(response: requests.Response) -> int:
    """Get the number of images in the response"""
    soup = BeautifulSoup(response.text, "html.parser")
    return len(soup.find_all("img"))


def num_links(response: requests.Response) -> int:
    """Get the number of links in the response."""
    soup = BeautifulSoup(response.text, "html.parser")
    return len(soup.find_all("a"))


def script_length(response: requests.Response) -> int:
    """Get the length of the scripts in the"""
    soup = BeautifulSoup(response.text, "html.parser")
    return len(soup.find_all("script"))


def special_characters(response: requests.Response) -> int:
    """Get the number of special characters in the response."""
    soup = BeautifulSoup(response.text, "html.parser")
    body_text = soup.get_text()
    return len([c for c in body_text if not c.isalnum() and not c.isspace()])


def script_to_special_chars_ratio(response: requests.Response) -> float:
    """Get the ratio of scripts to special characters in the response"""
    schars = special_characters(response)
    slength = script_length(response)
    return slength / schars if schars > 0 else 0


def script_to_body_ratio(response: requests.Response) -> float:
    """Get the ratio of scripts to body in"""
    blength = body_length(response)
    slength = script_length(response)
    return slength / blength if blength > 0 else 0


def body_to_special_char_ratio(response: requests.Response) -> float:
    """Get the ratio of body to special characters in the response."""
    blength = body_length(response)
    schars = special_characters(response)
    return blength / schars if schars > 0 else 0


def get_http_response_features(
    url: Optional[str] = None, response: Optional[requests.Response] = None
) -> HttpResponseFeatures:
    """Get the HTTP response features for a given URL or response object."""
    if not url and not response:
        raise ValueError("Either URL or response object must be provided.")
    if not response:
        try:
            response = requests.get(
                url, allow_redirects=True, timeout=config.api_timeout
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL: {e}", e)
            return HttpResponseFeatures(
                redirects=False,
                redirect_count=0,
                contains_forms=False,
                contains_obfuscated_scripts=False,
                contains_suspicious_keywords=False,
                uses_https=False,
                missing_x_frame_options=True,
                missing_x_xss_protection=True,
                missing_content_security_policy=True,
                missing_strict_transport_security=True,
                missing_x_content_type_options=True,
                is_live=False,
            )

    return HttpResponseFeatures(
        redirects=check_redirects(response),
        redirect_count=count_redirects(response),
        contains_forms=check_forms(response),
        contains_obfuscated_scripts=check_obfuscated_scripts(response),
        contains_suspicious_keywords=check_suspicious_keywords(response),
        uses_https=check_https(response),
        missing_x_frame_options=check_header_x_frame_options(response),
        missing_x_xss_protection=check_header_x_xss_protection(response),
        missing_content_security_policy=check_header_content_security_policy(response),
        missing_strict_transport_security=check_header_strict_transport_security(
            response
        ),
        missing_x_content_type_options=check_header_x_content_type_options(response),
        is_live=is_live(response),
        server_version=check_server_version(response),
        body_length=body_length(response),
        num_titles=num_titles(response),
        num_images=num_images(response),
        num_links=num_links(response),
        script_length=script_length(response),
        special_characters=special_characters(response),
        script_to_special_chars_ratio=script_to_special_chars_ratio(response),
        script_to_body_ratio=script_to_body_ratio(response),
        body_to_special_char_ratio=body_to_special_char_ratio(response),
    )


if __name__ == "__main__":
    url = "https://www.example.com"
    features = get_http_response_features(url)
    print(features)
