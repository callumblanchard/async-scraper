import os

from aiohttp import ClientSession
from typing import IO

from lib.loggerinit import logger_init

logger = logger_init(__name__)


def get_urls_from_file(url_file: IO) -> set:
    """Get a set of URLs from a .txt file."""
    with open(url_file) as infile:
        urls = set(map(str.strip, infile))

    return urls


async def get_organic_urls(
    keyword: str, limit: int = 10, db: str = "uk",
) -> set:
    """
    Get top N SERP results from SEMrush for a given keyword.

    Default database = UK
    Default limit = 10
    """
    keyname = "SEMRUSH_API_KEY"

    key = os.getenv(keyname, None)
    if key is None:
        logger.error("Couldn't find environment variable: %s", keyname)
        return set()

    url = (
        f"https://api.semrush.com/?key={key}"
        + f"&type=phrase_organic"
        + f"&phrase={keyword}"
        + f"&export_columns=Ur"
        + f"&database={db}"
        + f"&display_limit={limit}"
    )

    async with ClientSession() as session:
        resp = await session.request(method="GET", url=url)
        resp.raise_for_status()
        logger.info("Got top %i URLs from SEMrush", limit)

        response = await resp.text()

        response_list = response.split("\r\n")

        parsed = {response_list[0]: response_list[1:]}

        urls = set(map(str.strip, parsed.get("Url", [])))

    return urls
