import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
import urllib3
from bs4 import BeautifulSoup

from web2vec.config import config
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
    source_mode: str = "raw_http"
    was_js_rendered: bool = False
    likely_js_spa: bool = False
    html_snapshot_path: Optional[str] = None
    num_network_requests: int = 0
    num_external_network_requests: int = 0
    num_api_endpoints: int = 0
    found_network_requests: List[str] = field(default_factory=list)
    found_api_endpoints: List[str] = field(default_factory=list)


def check_obfuscated_scripts(
    soup: BeautifulSoup, scripts: Optional[List[Any]] = None
) -> bool:
    """Check if the response contains any obfuscated scripts."""
    scripts = scripts if scripts is not None else soup.find_all("script")
    for script in scripts:
        if script.get("src") and (
            "eval(" in script["src"] or "document.write(" in script["src"]
        ):
            return True
    return False


def check_suspicious_keywords(
    soup: BeautifulSoup,
    keywords: Optional[List[str]] = None,
    page_text: Optional[str] = None,
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
    page_content = (
        page_text.lower() if page_text is not None else soup.get_text().lower()
    )
    return any(keyword in page_content for keyword in suspicious_keywords)


def body_length(soup: BeautifulSoup, text_content: Optional[str] = None) -> int:
    """Get the length of the body text in the given HTML content."""
    content = text_content if text_content is not None else soup.get_text()
    return len(content)


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


def special_characters(soup: BeautifulSoup, text_content: Optional[str] = None) -> int:
    """Get the number of special characters in the given HTML content."""
    body_text = text_content if text_content is not None else soup.get_text()
    return len([c for c in body_text if not c.isalnum() and not c.isspace()])


def script_to_special_chars_ratio(
    soup: BeautifulSoup,
    special_char_count: Optional[int] = None,
    script_count: Optional[int] = None,
) -> float:
    """Get the ratio of script length to special characters in the given HTML content."""
    schars = (
        special_char_count
        if special_char_count is not None
        else special_characters(soup)
    )
    slength = script_count if script_count is not None else script_length(soup)
    return slength / schars if schars > 0 else 0


def script_to_body_ratio(
    soup: BeautifulSoup,
    body_len: Optional[int] = None,
    script_count: Optional[int] = None,
) -> float:
    """Get the ratio of script length to body length in the given HTML content."""
    blength = body_len if body_len is not None else body_length(soup)
    slength = script_count if script_count is not None else script_length(soup)
    return slength / blength if blength > 0 else 0


def body_to_special_char_ratio(
    soup: BeautifulSoup,
    body_len: Optional[int] = None,
    special_char_count: Optional[int] = None,
) -> float:
    """Get the ratio of body length to special characters in the given HTML content."""
    blength = body_len if body_len is not None else body_length(soup)
    schars = (
        special_char_count
        if special_char_count is not None
        else special_characters(soup)
    )
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


def detect_likely_js_spa(soup: BeautifulSoup) -> bool:
    """Heuristic signal that a page likely depends on JS rendering."""
    spa_roots = [
        "#root",
        "#app",
        "#__next",
        "#__nuxt",
        "[data-reactroot]",
        "[ng-app]",
    ]
    if any(soup.select(selector) for selector in spa_roots):
        return True

    text_len = len(soup.get_text(strip=True))
    scripts_count = len(soup.find_all("script"))
    has_noscript = bool(soup.find("noscript"))
    return scripts_count >= 3 and text_len < 200 and has_noscript


def is_external_url(url: str, base_domain: str) -> bool:
    """Return True when URL points outside current page domain."""
    parsed = urlparse(url)
    if not parsed.netloc:
        return False
    return parsed.netloc != base_domain


def detect_api_endpoints(urls: List[str]) -> List[str]:
    """Return URLs that look like API/JSON endpoints."""
    api_like = []
    pattern = re.compile(r"(/api/|/graphql|/rest/|/v\d+/|[?&]format=json)", re.I)
    for candidate in urls:
        lowered = candidate.lower()
        if lowered.endswith(".json") or pattern.search(lowered):
            api_like.append(candidate)
    return list(dict.fromkeys(api_like))


def get_html_body_features(
    body: str,
    url: str,
    source_mode: str = "raw_http",
    was_js_rendered: bool = False,
    html_snapshot_path: Optional[str] = None,
    network_request_urls: Optional[List[str]] = None,
) -> HtmlBodyFeatures:
    """Extract HTML body features from the"""
    soup = BeautifulSoup(body, "html.parser")
    base_domain = get_domain_from_url(url)
    page_text = soup.get_text()

    def _safe_attr(tag, attr) -> str:
        value = tag.get(attr)
        if isinstance(value, str):
            return value
        if isinstance(value, list) and value:
            return value[0]
        return ""

    forms = soup.find_all("form")
    forms_with_action = [form for form in forms if form.get("action")]
    scripts = soup.find_all("script")
    scripts_with_src = [script for script in scripts if script.get("src")]
    styles = soup.find_all("link", rel="stylesheet")
    styles_with_href = [style for style in styles if style.get("href")]
    iframes = soup.find_all("iframe", src=True)
    anchors = soup.find_all("a", href=True)
    images = soup.find_all("img")
    media = soup.find_all(["img", "video", "audio"], src=True)
    headings = []
    for i in range(7):
        headings.extend(soup.find_all(f"h{i}"))

    body_len = len(page_text)
    special_char_count = len(
        [c for c in page_text if not c.isalnum() and not c.isspace()]
    )
    script_len = len(scripts)

    def _netloc(value: str) -> str:
        return urlparse(value or "").netloc
    discovered_urls = list(dict.fromkeys(network_request_urls or []))
    external_discovered = [
        item for item in discovered_urls if is_external_url(item, base_domain)
    ]
    found_api_endpoints = detect_api_endpoints(discovered_urls)

    return HtmlBodyFeatures(
        contains_forms=bool(forms),
        contains_obfuscated_scripts=check_obfuscated_scripts(soup, scripts),
        contains_suspicious_keywords=check_suspicious_keywords(
            soup, page_text=page_text
        ),
        body_length=body_len,
        num_titles=len(headings),
        num_images=len(images),
        num_links=len(anchors),
        script_length=script_len,
        special_characters=special_char_count,
        script_to_special_chars_ratio=script_to_special_chars_ratio(
            soup, special_char_count, script_len
        ),
        script_to_body_ratio=script_to_body_ratio(soup, body_len, script_len),
        body_to_special_char_ratio=body_to_special_char_ratio(
            soup, body_len, special_char_count
        ),
        iframe_redirection=iframe_redirection(soup),
        mouse_over_effect=mouse_over_effect(soup),
        right_click_disabled=right_click_disabled(soup),
        num_scripts_http=len(
            [
                script
                for script in scripts_with_src
                if _safe_attr(script, "src").startswith("http://")
            ]
        ),
        num_styles_http=len(
            [
                style
                for style in styles_with_href
                if _safe_attr(style, "href").startswith("http://")
            ]
        ),
        num_iframes_http=len(
            [
                iframe
                for iframe in iframes
                if _safe_attr(iframe, "src").startswith("http://")
            ]
        ),
        num_external_scripts=len(
            [
                script
                for script in scripts_with_src
                if _netloc(_safe_attr(script, "src"))
                and _netloc(_safe_attr(script, "src")) != base_domain
            ]
        ),
        num_external_styles=len(
            [
                style
                for style in styles_with_href
                if _netloc(_safe_attr(style, "href"))
                and _netloc(_safe_attr(style, "href")) != base_domain
            ]
        ),
        num_external_iframes=len(
            [
                iframe
                for iframe in iframes
                if _netloc(_safe_attr(iframe, "src"))
                and _netloc(_safe_attr(iframe, "src")) != base_domain
            ]
        ),
        num_meta_tags=num_meta_tags(soup),
        num_forms=len(forms),
        num_forms_post=len(
            [form for form in forms if form.get("method", "").lower() == "post"]
        ),
        num_forms_get=len(
            [form for form in forms if form.get("method", "").lower() == "get"]
        ),
        num_forms_external_action=len(
            [
                form
                for form in forms_with_action
                if _netloc(_safe_attr(form, "action"))
                and _netloc(_safe_attr(form, "action")) != base_domain
            ]
        ),
        num_hidden_elements=hidden_elements(soup),
        num_safe_anchors=len(
            [
                anchor
                for anchor in anchors
                if _netloc(_safe_attr(anchor, "href")) == base_domain
                or not _netloc(_safe_attr(anchor, "href"))
            ]
        ),
        num_media_http=len(
            [item for item in media if _safe_attr(item, "src").startswith("http://")]
        ),
        num_media_external=len(
            [
                item
                for item in media
                if _netloc(_safe_attr(item, "src"))
                and _netloc(_safe_attr(item, "src")) != base_domain
            ]
        ),
        num_email_forms=len(
            [
                form
                for form in forms_with_action
                if _safe_attr(form, "action").startswith("mailto:")
            ]
        ),
        num_internal_links=len(
            [
                anchor
                for anchor in anchors
                if _netloc(_safe_attr(anchor, "href")) == base_domain
            ]
        ),
        favicon_url=find_favicon(soup),
        logo_url=find_logo(soup),
        found_forms=[form.attrs for form in forms],
        found_images=[img.attrs for img in images],
        found_anchors=[a.attrs for a in anchors],
        found_media=[m.attrs for m in media],
        copyright=find_copyright(soup),
        source_mode=source_mode,
        was_js_rendered=was_js_rendered,
        likely_js_spa=detect_likely_js_spa(soup),
        html_snapshot_path=html_snapshot_path,
        num_network_requests=len(discovered_urls),
        num_external_network_requests=len(external_discovered),
        num_api_endpoints=len(found_api_endpoints),
        found_network_requests=discovered_urls,
        found_api_endpoints=found_api_endpoints,
    )


# Example usage:
if __name__ == "__main__":
    from web2vec.crawlers.extractors import HtmlBodyExtractor

    url = "https://shop.volvocars.ca"
    if not config.ssl_verify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.get(
        url, allow_redirects=True, timeout=60, verify=config.ssl_verify
    )

    extractor = HtmlBodyExtractor(
        enable_js_render=True,
        save_html_snapshot=True,
        render_wait_seconds=2.0,
    )
    html_body_features = extractor.extract_features(response)

    print(html_body_features)
    print(f"Snapshot path: {html_body_features.html_snapshot_path}")
