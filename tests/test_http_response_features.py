from types import SimpleNamespace

from web2vec.extractors.http_response_features import (
    get_http_response_features,
)

RESPONSE_HTML = """
<html>
    <body>
        <form><input type="text" name="username" /></form>
        <script src="/static/app.js"></script>
        <a href="https://example.com/next">Next</a>
        <p>Secure login form</p>
    </body>
</html>
"""


def make_response():
    """Create a fake HTTPS response object with headers and history."""
    return SimpleNamespace(
        text=RESPONSE_HTML,
        url="https://example.com/login",
        headers={"Server": "nginx", "X-Frame-Options": "DENY"},
        status_code=200,
        history=[object()],
    )


def test_http_response_feature_extraction():
    """Validate HTTP feature extraction using the stubbed response."""
    response = make_response()
    features = get_http_response_features(response=response)

    assert features.redirects is True
    assert features.redirect_count == 1
    assert features.contains_forms is True
    assert features.contains_suspicious_keywords is True
    assert features.uses_https is True
    assert features.missing_x_frame_options is False
    assert features.missing_x_xss_protection is True
    assert features.missing_content_security_policy is True
    assert features.is_live is True
    assert features.server_version == "nginx"
    assert features.num_links == 1
    assert features.script_length == 1
