from bs4 import BeautifulSoup
import requests
import re
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)


def scrape_website(url, timeout=10, headers=None):
    """Retrieve the textual content of a webpage.

    Returns the page text on success, or None on failure.
    """
    if headers is None:
        headers = {"User-Agent": "chatbot-univ-lille/1.0 (+https://example.org)"}

    try:
        resp = requests.get(url, timeout=timeout, headers=headers)
        resp.raise_for_status()
    except requests.RequestException as e:
        logging.error("Request failed for %s: %s", url, e)
        return None

    soup = BeautifulSoup(resp.content, "html.parser")
    return soup.get_text()


def _safe_name_from_url(url):
    """Create a filesystem-safe name from a URL's netloc.

    Example: 'www.univ-lille.fr' -> 'www_univ-lille_fr'
    """
    parsed = urlparse(url)
    netloc = parsed.netloc or "site"
    safe = re.sub(r'[^A-Za-z0-9._-]+', '_', netloc)
    return safe


def save_text(content, url, data_dir=None):
    """Save scraped text into `data/` with a timestamped filename and return the path."""
    if data_dir is None:
        # project root /data
        data_dir = Path(__file__).resolve().parents[1] / "data"
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    name = _safe_name_from_url(url)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{name}_{timestamp}.txt"
    path = data_dir / filename

    path.write_text(content, encoding="utf-8")
    logging.info("Saved scraped content to %s", path)
    return path


if __name__ == "__main__":
    url = "https://www.univ-lille.fr"

    content = scrape_website(url)
    if content:
        saved_path = save_text(content, url)
        print(f"Contenu sauvegardé dans : {saved_path}")
    else:
        print("Failed to retrieve website content.")