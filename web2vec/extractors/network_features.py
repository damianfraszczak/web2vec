import json
import os
from typing import List, Optional
from urllib.parse import urljoin

import matplotlib.pyplot as plt
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


def visualize_graph(graph: nx.Graph):
    """Visualize the graph of web pages."""
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(12, 12))
    nx.draw(
        graph,
        pos,
        with_labels=True,
        node_size=50,
        node_color="skyblue",
        font_size=8,
        font_weight="bold",
        edge_color="gray",
    )
    plt.title("Graph of Web Pages")
    plt.show()


def visualize_graph_with_centrality(graph: nx.Graph):
    """Visualize the graph of web pages with centrality."""
    degree_centrality = nx.degree_centrality(graph)

    sorted_nodes = sorted(
        degree_centrality.items(), key=lambda item: item[1], reverse=True
    )

    table_data = [["Node", "Degree Centrality"]]
    for node, centrality in sorted_nodes[:20]:
        table_data.append([str(node), f"{centrality:.4f}"])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 12))

    pos = nx.spring_layout(graph)
    nx.draw(
        graph,
        pos,
        with_labels=True,
        node_size=50,
        node_color="skyblue",
        font_size=8,
        font_weight="bold",
        edge_color="gray",
        ax=ax1,
    )
    ax1.set_title("Graph of Web Pages")

    ax2.axis("off")
    table = ax2.table(cellText=table_data, cellLoc="center", loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.5, 1.5)
    ax2.set_title("Top 10 Degree Centrality of Nodes")

    plt.show()
