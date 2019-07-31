from lib.loggerinit import logger_init

logger = logger_init(__name__)


def get_urls(url_file):
    with open(url_file) as infile:
        urls = set(map(str.strip, infile))

    return urls
