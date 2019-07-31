# app.py

import asyncio

from lib.logtimer import log_time
from lib.loggerinit import logger_init
from lib.bulkcrawl import bulk_crawl_and_write
from lib.urlgetter import get_urls

logger = logger_init(__name__)


@log_time
def main():
    import pathlib

    here = pathlib.Path(__file__).parent

    urls = get_urls(here.joinpath("urls.txt"))

    outpath = here.joinpath("foundurls.txt")
    with open(outpath, "w") as outfile:
        outfile.write("source_url\tparsed_url\n")

    asyncio.run(bulk_crawl_and_write(file=outpath, urls=urls))


if __name__ == "__main__":
    main()
