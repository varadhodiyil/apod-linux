"""APOD fetcher."""

import logging
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin

from wallpaper import main as set_wallpaper

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s: %(message)s : %(asctime)s",
)
logger = logging.getLogger(__name__)

APOD_URL = "https://apod.nasa.gov/apod/astropix.html"


class _APODParser(HTMLParser):
    """Extract the highest-resolution image URL from the APOD page."""

    def __init__(self) -> None:
        super().__init__()
        self.image_url: str | None = None
        self._in_image_link = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if attr is None:
            return

        if tag == "a" and attr.get("href", "").startswith("image/"):  # ty:ignore[unresolved-attribute]
            self._in_image_link = True
            self.image_url = attr["href"]
        elif tag == "img" and not self.image_url:
            src = attr.get("src", "")
            if not src:
                return
            if src.startswith("image/"):
                self.image_url = src

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self._in_image_link = False


def _is_valid_url(url: str) -> None:
    """Sanitize a string to be a valid filename."""
    if not url.startswith(("http:", "https:")):
        msg = "URL must start with 'http:' or 'https:'"
        raise ValueError(msg)


def fetch_apod_image_url(page_url: str = APOD_URL) -> str:
    """Fetch the APOD page and return the image URL."""
    logger.debug("Fetching APOD page: %s", page_url)
    _is_valid_url(page_url)
    with urllib.request.urlopen(page_url) as response:  # noqa: S310
        html = response.read().decode("utf-8", errors="replace")

    parser = _APODParser()
    parser.feed(html)

    if not parser.image_url:
        msg = "Could not find image URL on APOD page"
        raise ValueError(msg)

    image_url = urljoin(page_url, parser.image_url)
    logger.debug("Found image URL: %s", image_url)
    return image_url


def download_image(image_url: str, dest_path: str) -> str:
    """Download the image to dest_path and return the path."""
    logger.info("Downloading image: %s -> %s", image_url, dest_path)
    _is_valid_url(image_url)
    urllib.request.urlretrieve(image_url, dest_path)  # noqa: S310
    return dest_path


if __name__ == "__main__":
    try:
        image_url = fetch_apod_image_url()
        logger.info("APOD image URL: %s", image_url)
        downloaded_path = download_image(image_url, "apod.jpg")
        logger.info("Image downloaded to: %s", downloaded_path)
        set_wallpaper(downloaded_path, desktop="auto")
    except Exception:
        logger.exception("Failed to fetch and download APOD image")
