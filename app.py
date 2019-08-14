# app.py

import asyncio

from lib.logtimer import log_time
from lib.loggerinit import logger_init
from lib.bulkcrawl import bulk_crawl_and_write
from lib.urlgetter import get_organic_urls

logger = logger_init(__name__)


@log_time
def main():
    keyword = input("Enter a keyword or phrase: ")
    limit: int = int(input("How many search results?: "))

    import pathlib

    here = pathlib.Path(__file__).parent

    urls = asyncio.run(get_organic_urls(keyword=keyword, limit=limit))

    outpath = here.joinpath("foundurls.txt")
    with open(outpath, "w") as outfile:
        outfile.write("source_url\tparsed_url\n")

    asyncio.run(bulk_crawl_and_write(file=outpath, urls=urls))


if __name__ == "__main__":
    main()
