from aiohttp import ClientSession

from lib.loggerinit import logger_init

logger = logger_init(__name__)


# Asyncronous fetching of a page from URL

async def fetch_html(url: str, session: ClientSession, **kwargs) -> str:
    """
    GET request wrapper to fetch page HTML.

    kwargs are passed to `session.request()`.
    """

    resp = await session.request(method="GET", url=url, **kwargs)
    resp.raise_for_status()
    logger.info("Got response [%s] for URL: %s", resp.status, url)
    html = await resp.text()
    return html
