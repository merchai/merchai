"""
Headless browser runner for loading webpages and returning raw HTML.

Experimental infrastructure to support models/tools that do not provide APIs.
Runs reliably inside Docker with no GUI dependencies.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from src.logger import get_logger

logger = get_logger(__name__)


def get_page_html(url: str, timeout_seconds: int = 30) -> str:
    """
    Load a URL in a headless browser and return the page HTML as a string.

    Args:
        url: The URL to load.
        timeout_seconds: Page load timeout in seconds.

    Returns:
        The raw HTML of the loaded page (driver.page_source).

    Raises:
        Exception: On driver creation or page load failure.
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")

    # Use Chromium binary when present (e.g. in Docker); otherwise default Chrome.
    chromium_bin = os.environ.get("CHROMIUM_PATH", "/usr/bin/chromium")
    if Path(chromium_bin).exists():
        options.binary_location = chromium_bin

    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
    service = Service(executable_path=chromedriver_path) if chromedriver_path else None

    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.set_page_load_timeout(timeout_seconds)
        driver.get(url)
        return driver.page_source
    finally:
        driver.quit()


def main() -> None:
    """CLI entrypoint: load a URL and print its HTML to stdout."""
    if len(sys.argv) < 2:
        #print("Usage: python -m src.infra.headless_runner <url>", file=sys.stderr)
        logger.error("Usage: python -m src.infra.headless_runner <url>")
        sys.exit(1)
    url = sys.argv[1]
    try:
        html = get_page_html(url)
        #print(html)
        logger.info(f"Loaded {len(html)} characters from {url}")
    except Exception as e:
        #print(f"Error: {e}", file=sys.stderr)
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
