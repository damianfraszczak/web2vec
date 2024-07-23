import logging
from dataclasses import dataclass
from functools import cache
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


@dataclass
class GoogleIndexFeatures:
    """Dataclass for Google index features."""

    is_indexed: Optional[bool]
    position: Optional[int] = None


def get_google_index_features(url: str) -> GoogleIndexFeatures:
    """Check if the given URL is indexed by Google and return its position."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    driver.get(f"https://www.google.com/search?q=site:{url}")  # noqa

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "rso")))

        results = driver.find_elements(By.CSS_SELECTOR, "#rso .g")
        for index, result in enumerate(results, start=1):
            link = result.find_element(By.TAG_NAME, "a").get_attribute("href")
            if url in link:
                driver.quit()
                return GoogleIndexFeatures(is_indexed=True, position=index)

        driver.quit()
        return GoogleIndexFeatures(is_indexed=False, position=None)

    except Exception as e:  # noqa
        logger.error(f"Error checking Google index: {e}", exc_info=True)
        driver.quit()
        return GoogleIndexFeatures(is_indexed=None, position=None)


@cache
def get_google_index_features_cached(url: str) -> GoogleIndexFeatures:
    """Get the Google index features for the given URL."""
    return get_google_index_features(url)


if __name__ == "__main__":
    url = "wp.pl"
    result = get_google_index_features(url)
    if result.is_indexed is None:
        print(f"Error checking {url}.")
    else:
        print(f"Is {url} indexed by Google? {'Yes' if result.is_indexed else 'No'}")
        if result.is_indexed:
            print(f"Position in search results: {result.position}")
