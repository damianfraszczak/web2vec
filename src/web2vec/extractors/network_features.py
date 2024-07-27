import json
import os
from typing import List, Optional
from urllib.parse import urljoin

import networkx as nx
from bs4 import BeautifulSoup

from web2vec.utils import get_domain_from_url


def build_graph(main_directory: str, allowed_domains: Optional[List] = None):
    """Build a directed graph from the crawled web pages."""
    G = nx.DiGraph()
    for filename in os.listdir(main_directory):
        if filename.endswith(".json"):
            filepath = os.path.join(main_directory, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                url = data["url"]
                html_content = data["html"]

                G.add_node(url)

                soup = BeautifulSoup(html_content, "html.parser")
                for link in soup.find_all("a", href=True):
                    target_url = link["href"]
                    if target_url.startswith("/"):
                        target_url = urljoin(url, target_url)
                    link_domain = get_domain_from_url(target_url)

                    if allowed_domains is None or link_domain in allowed_domains:
                        G.add_edge(url, target_url)

    return G
