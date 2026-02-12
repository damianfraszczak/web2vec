from web2vec.extractors.html_body_features import get_html_body_features

HTML_DOC = """
<!DOCTYPE html>
<html>
<head>
    <title>Login Page</title>
    <meta name="description" content="All rights reserved 2026">
    <link rel="icon" href="/favicon.ico" />
    <link rel="stylesheet" href="http://cdn.example.com/style.css" />
</head>
<body onmouseover="console.log('hover')">
    <form method="post" action="https://auth.example.net/login">
        <input type="hidden" style="display:none" name="token" />
        <input type="email" name="email" />
    </form>
    <a href="/internal">Internal</a>
    <a href="http://external.example.net">External</a>
    <img alt="Company Logo" src="http://cdn.example.com/logo.png" />
    <script src="http://cdn.example.com/app.js"></script>
    <iframe src="http://cdn.example.com/frame.html"></iframe>
    <p>Please login to update your account password today.</p>
</body>
</html>
"""


def test_html_body_feature_counts():
    """Verify HTML extractor counts and flags representative elements."""
    url = "https://example.com/page"
    features = get_html_body_features(HTML_DOC, url)

    assert features.contains_forms is True
    assert features.num_forms == 1
    assert features.num_forms_post == 1
    assert features.num_forms_external_action == 1
    assert features.num_external_scripts == 1
    assert features.num_scripts_http == 1
    assert features.num_external_iframes == 1
    assert features.num_safe_anchors >= 1
    assert features.contains_suspicious_keywords is True
    assert features.iframe_redirection == 0
    assert features.mouse_over_effect == 1
    assert features.logo_url == "http://cdn.example.com/logo.png"
    assert features.favicon_url == "/favicon.ico"
