import json

from web2vec.extractors.network_features import build_graph


def test_build_graph_filters_disallowed_domains(tmp_path):
    """Ensure build_graph respects allowed domains when linking nodes."""
    data = {
        "url": "https://example.com/page",
        "html": """
            <a href="/internal">Internal</a>
            <a href="https://allowed.com/resource">Allowed</a>
            <a href="https://blocked.com/phishing">Blocked</a>
        """,
    }
    json_path = tmp_path / "page.json"
    json_path.write_text(json.dumps(data), encoding="utf-8")

    graph = build_graph(str(tmp_path), allowed_domains=["example.com", "allowed.com"])

    assert "https://example.com/page" in graph.nodes
    assert "https://example.com/internal" in graph.nodes
    assert graph.has_edge("https://example.com/page", "https://example.com/internal")
    assert graph.has_edge("https://example.com/page", "https://allowed.com/resource")
    assert "https://blocked.com/phishing" not in graph
