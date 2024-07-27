import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from web2vec.utils import get_domain_from_url


@dataclass
class HtmlBodyFeatures:
    contains_forms: bool
    contains_obfuscated_scripts: bool
    contains_suspicious_keywords: bool
    body_length: int
    num_titles: int
    num_images: int
    num_links: int
    script_length: int
    special_characters: int
    script_to_special_chars_ratio: float
    script_to_body_ratio: float
    body_to_special_char_ratio: float
    iframe_redirection: int
    mouse_over_effect: int
    right_click_disabled: int
    num_scripts_http: int
    num_styles_http: int
    num_iframes_http: int
    num_external_scripts: int
    num_external_styles: int
    num_external_iframes: int
    num_meta_tags: int
    num_forms: int
    num_forms_post: int
    num_forms_get: int
    num_forms_external_action: int
    num_hidden_elements: int
    num_safe_anchors: int
    num_media_http: int
    num_media_external: int
    num_email_forms: int
    num_internal_links: int
    favicon_url: Optional[str]
    logo_url: Optional[str]
    found_forms: List[Dict[str, Any]] = field(default_factory=list)
    found_images: List[Dict[str, Any]] = field(default_factory=list)
    found_anchors: List[Dict[str, Any]] = field(default_factory=list)
    found_media: List[Dict[str, Any]] = field(default_factory=list)
    copyright: Optional[str] = None


def check_obfuscated_scripts(soup: BeautifulSoup) -> bool:
    """Check if the response contains any obfuscated scripts."""
    scripts = soup.find_all("script")
    for script in scripts:
        if script.get("src") and (
            "eval(" in script["src"] or "document.write(" in script["src"]
        ):
            return True
    return False


def check_suspicious_keywords(
    soup: BeautifulSoup, keywords: Optional[List[str]] = None
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
    page_content = soup.get_text().lower()
    return any(keyword in page_content for keyword in suspicious_keywords)


def body_length(soup: BeautifulSoup) -> int:
    """Get the length of the body text in the given HTML content."""
    return len(soup.get_text())


def num_titles(soup: BeautifulSoup) -> int:
    """Get the number of titles in the given HTML content."""
    titles = ["h{}".format(i) for i in range(7)]
    titles = [soup.find_all(tag) for tag in titles]
    return len([item for sublist in titles for item in sublist])


def num_images(soup: BeautifulSoup) -> int:
    """Get the number of images in the given HTML content."""
    return len(soup.find_all("img"))


def num_links(soup: BeautifulSoup) -> int:
    """Get the number of links in the given HTML content."""
    return len(soup.find_all("a"))


def script_length(soup: BeautifulSoup) -> int:
    """Get the length of the scripts in the given HTML content."""
    return len(soup.find_all("script"))


def special_characters(soup: BeautifulSoup) -> int:
    """Get the number of special characters in the given HTML content."""
    body_text = soup.get_text()
    return len([c for c in body_text if not c.isalnum() and not c.isspace()])


def script_to_special_chars_ratio(soup: BeautifulSoup) -> float:
    """Get the ratio of script length to special characters in the given HTML content."""
    schars = special_characters(soup)
    slength = script_length(soup)
    return slength / schars if schars > 0 else 0


def script_to_body_ratio(soup: BeautifulSoup) -> float:
    """Get the ratio of script length to body length in the given HTML content."""
    blength = body_length(soup)
    slength = script_length(soup)
    return slength / blength if blength > 0 else 0


def body_to_special_char_ratio(soup: BeautifulSoup) -> float:
    """Get the ratio of body length to special characters in the given HTML content."""
    blength = body_length(soup)
    schars = special_characters(soup)
    return blength / schars if schars > 0 else 0


def iframe_redirection(soup: BeautifulSoup) -> int:
    """Check if the response contains any iframe redirection."""
    if not soup:
        return 1
    return 0 if soup.find_all("iframe") or soup.find_all("frameborder") else 1


def mouse_over_effect(soup: BeautifulSoup) -> int:
    """Check if the response contains any mouse-over effect."""
    if not soup:
        return 1
    return 1 if soup.find_all(onmouseover=True) else 0


def right_click_disabled(soup: BeautifulSoup) -> int:
    """Check if the response contains any right-click disabled content."""
    if not soup:
        return 1
    return 0 if re.findall(r"event.button ?== ?2", str(soup)) else 1


def num_scripts_http(soup: BeautifulSoup) -> int:
    """Get the number of HTTP scripts in the given HTML content."""
    scripts = soup.find_all("script", src=True)
    return len([script for script in scripts if script["src"].startswith("http://")])


def num_styles_http(soup: BeautifulSoup) -> int:
    """Get the number of HTTP stylesheets in the given HTML content."""
    styles = soup.find_all("link", rel="stylesheet")
    return len([style for style in styles if style["href"].startswith("http://")])


def num_iframes_http(soup: BeautifulSoup) -> int:
    """Get the number of HTTP iframes in the given HTML content."""
    iframes = soup.find_all("iframe", src=True)
    return len([iframe for iframe in iframes if iframe["src"].startswith("http://")])


def num_external_scripts(soup: BeautifulSoup, base_domain: str) -> int:
    """Get the number of external scripts in the given HTML content."""
    scripts = soup.find_all("script", src=True)
    return len(
        [script for script in scripts if urlparse(script["src"]).netloc != base_domain]
    )


def num_external_styles(soup: BeautifulSoup, base_domain: str) -> int:
    """Get the number of external stylesheets in the given HTML content."""
    styles = soup.find_all("link", rel="stylesheet")
    return len(
        [style for style in styles if urlparse(style["href"]).netloc != base_domain]
    )


def num_external_iframes(soup: BeautifulSoup, base_domain: str) -> int:
    """Get the number of external iframes in the given HTML content."""
    iframes = soup.find_all("iframe", src=True)
    return len(
        [iframe for iframe in iframes if urlparse(iframe["src"]).netloc != base_domain]
    )


def num_meta_tags(soup: BeautifulSoup) -> int:
    """Get the number of meta tags in the given HTML content."""
    return len(soup.find_all("meta"))


def num_forms(soup: BeautifulSoup) -> int:
    """Get the number of forms in the given HTML content."""
    return len(soup.find_all("form"))


def num_forms_post(soup: BeautifulSoup) -> int:
    """Get the number of POST forms in the given HTML content."""
    return len(
        [
            form
            for form in soup.find_all("form")
            if form.get("method", "").lower() == "post"
        ]
    )


def num_forms_get(soup: BeautifulSoup) -> int:
    """Get the number of GET forms in the given HTML content."""
    return len(
        [
            form
            for form in soup.find_all("form")
            if form.get("method", "").lower() == "get"
        ]
    )


def num_forms_external_action(soup: BeautifulSoup, base_domain: str) -> int:
    """Get the number of forms with external action in the given HTML content."""
    forms = soup.find_all("form", action=True)
    return len(
        [
            form
            for form in forms
            if urlparse(form["action"]).netloc
            and urlparse(form["action"]).netloc != base_domain
        ]
    )


def hidden_elements(soup: BeautifulSoup) -> int:
    """Get the number of hidden elements in the given HTML content."""
    hidden_elements = soup.find_all(
        style=lambda value: value and "display:none" in value
    )
    return len(hidden_elements)


def num_safe_anchors(soup: BeautifulSoup, base_domain: str) -> int:
    """Get the number of safe anchors in the given HTML content."""
    anchors = soup.find_all("a", href=True)
    return len(
        [
            anchor
            for anchor in anchors
            if urlparse(anchor["href"]).netloc == base_domain
            or not urlparse(anchor["href"]).netloc
        ]
    )


def num_media_http(soup: BeautifulSoup) -> int:
    """Get the number of HTTP media in the given HTML content."""
    media = soup.find_all(["img", "video", "audio"], src=True)
    return len([m for m in media if m["src"].startswith("http://")])


def num_media_external(soup: BeautifulSoup, base_domain: str) -> int:
    """Get the number of external media in the given HTML content."""
    media = soup.find_all(["img", "video", "audio"], src=True)
    return len([m for m in media if urlparse(m["src"]).netloc != base_domain])


def num_email_forms(soup: BeautifulSoup) -> int:
    """Get the number of email forms in the given HTML content."""
    forms = soup.find_all("form", action=True)
    return len([form for form in forms if form["action"].startswith("mailto:")])


def num_internal_links(soup: BeautifulSoup, base_domain: str) -> int:
    """Get the number of internal links in the given HTML content."""
    links = soup.find_all("a", href=True)
    return len([link for link in links if urlparse(link["href"]).netloc == base_domain])


def find_favicon(soup: BeautifulSoup) -> Optional[str]:
    """Find the favicon URL in the given HTML content."""
    icon_link = soup.find("link", rel="icon")
    return icon_link["href"] if icon_link else None


def find_logo(soup: BeautifulSoup) -> Optional[str]:
    """Find the logo URL in the given HTML content."""
    logo_img = soup.find("img", alt=re.compile(r"logo", re.I))
    return logo_img["src"] if logo_img else None


def find_copyright(soup: BeautifulSoup) -> Optional[str]:
    """Find the copyright information in the given HTML content."""
    # Possible patterns to find copyright information
    patterns = [
        re.compile(r"©"),
        re.compile(r"&copy;"),
        re.compile(r"copyright", re.IGNORECASE),
        re.compile(r"All rights reserved", re.IGNORECASE),
    ]

    # Search in meta tags
    for meta in soup.find_all("meta"):
        if "content" in meta.attrs:
            content = meta.attrs["content"]
            for pattern in patterns:
                if pattern.search(content):
                    return content

    # Search in text content
    text = soup.get_text(separator=" ")
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            start = max(0, match.start() - 30)
            end = match.end() + 30
            return text[start:end]

    return None


def get_html_body_features(body: str, url: str) -> HtmlBodyFeatures:
    """Extract HTML body features from the"""
    soup = BeautifulSoup(body, "html.parser")
    base_domain = get_domain_from_url(url)

    return HtmlBodyFeatures(
        contains_forms=bool(soup.find_all("form")),
        contains_obfuscated_scripts=check_obfuscated_scripts(soup),
        contains_suspicious_keywords=check_suspicious_keywords(soup),
        body_length=body_length(soup),
        num_titles=num_titles(soup),
        num_images=num_images(soup),
        num_links=num_links(soup),
        script_length=script_length(soup),
        special_characters=special_characters(soup),
        script_to_special_chars_ratio=script_to_special_chars_ratio(soup),
        script_to_body_ratio=script_to_body_ratio(soup),
        body_to_special_char_ratio=body_to_special_char_ratio(soup),
        iframe_redirection=iframe_redirection(soup),
        mouse_over_effect=mouse_over_effect(soup),
        right_click_disabled=right_click_disabled(soup),
        num_scripts_http=num_scripts_http(soup),
        num_styles_http=num_styles_http(soup),
        num_iframes_http=num_iframes_http(soup),
        num_external_scripts=num_external_scripts(soup, base_domain),
        num_external_styles=num_external_styles(soup, base_domain),
        num_external_iframes=num_external_iframes(soup, base_domain),
        num_meta_tags=num_meta_tags(soup),
        num_forms=num_forms(soup),
        num_forms_post=num_forms_post(soup),
        num_forms_get=num_forms_get(soup),
        num_forms_external_action=num_forms_external_action(soup, base_domain),
        num_hidden_elements=hidden_elements(soup),
        num_safe_anchors=num_safe_anchors(soup, base_domain),
        num_media_http=num_media_http(soup),
        num_media_external=num_media_external(soup, base_domain),
        num_email_forms=num_email_forms(soup),
        num_internal_links=num_internal_links(soup, base_domain),
        favicon_url=find_favicon(soup),
        logo_url=find_logo(soup),
        found_forms=[form.attrs for form in soup.find_all("form")],
        found_images=[img.attrs for img in soup.find_all("img")],
        found_anchors=[a.attrs for a in soup.find_all("a")],
        found_media=[m.attrs for m in soup.find_all(["img", "video", "audio"])],
        copyright=find_copyright(soup),
    )


# Example usage:
if __name__ == "__main__":
    url = "https://www.example.com"
    response = requests.get(url, allow_redirects=True, timeout=60)

    html_body_features = get_html_body_features(response.text, response.url)

    print(html_body_features)
