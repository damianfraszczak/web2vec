import ipaddress
import json
import logging
import math
import os
import re
import socket
from datetime import datetime, timedelta
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


def valid_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except Exception as e:
        logger.warn(e)
        return False


def get_domain_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.netloc


def get_ip_from_domain(domain: str) -> str:
    return socket.gethostbyname(domain)


def get_ip_from_url(url: str) -> str:
    return get_ip_from_domain(get_domain_from_url(url))


def entropy(string: str) -> float:
    prob = [float(string.count(c)) / len(string) for c in dict.fromkeys(list(string))]
    return -sum([(p * math.log(p) / math.log(2.0)) for p in prob])


def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def get_file_path_for_url(url, directory=None, timeout=86400) -> str:
    """Returns the path to the file for the given URL."""
    if not directory:
        current_directory = os.getcwd()
        directory = os.path.join(current_directory, 'data')

    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Determine the appropriate filename based on the timeout value
    current_time = datetime.now()
    if timeout is None:  # No timeout, just use the base filename
        timestamp = ""
    elif timeout >= 86400:  # 1 day or more
        timestamp = current_time.strftime('%Y%m%d')
    elif timeout >= 3600:  # 1 hour or more
        timestamp = current_time.strftime('%Y%m%d_%H')
    else:  # less than 1 hour
        timestamp = current_time.strftime('%Y%m%d_%H%M')

    sanitized_filename = sanitize_filename(url)
    file_name = os.path.join(directory, f"{timestamp}_{sanitized_filename}" if timestamp else sanitized_filename)
    return file_name


def fetch_file_from_url(url, directory=None, headers=None, timeout=86400) -> str:
    """
    Checks if the file exists in the directory and is newer than the timeout.
    If not, downloads the file from the URL, saves it in the directory, and returns the path.

    :param directory: Directory where the file should be saved.
    :param url: URL of the file to download.
    :param timeout: Timeout in seconds (default is 86400 = day).
    :return: File path.
    """
    file_name = get_file_path_for_url(url, directory, timeout)

    # Check if the file exists and its modification time
    if os.path.exists(file_name):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_name))
        if timeout is None or datetime.now() - file_mod_time < timedelta(seconds=timeout):
            return file_name

    # Download the file from the URL
    response = requests.get(url, headers=headers or {})
    if response.status_code == 200:
        with open(file_name, 'wb') as file:
            file.write(response.content)
        return file_name
    else:
        response.raise_for_status()


def fetch_file_from_url_and_read(url, directory=None, headers=None, timeout=86400) -> str:
    """Returns the content of the file for the given URL."""

    file_name = fetch_file_from_url(url, directory, headers, timeout)
    with open(file_name, 'r', encoding='utf-8') as file:
        return file.read()


def get_github_repo_release_info(repo: str) -> dict:
    """Returns the latest release information for the given GitHub repository."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    text = fetch_file_from_url_and_read(url)
    return json.loads(text)
