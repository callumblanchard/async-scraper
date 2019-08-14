#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup, Doctype
import re
import json


def none_iferror(func):
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except Exception as e:
            print(e)
            return None

    return func_wrapper


def strip_tag(func):
    def func_wrapper(*args, **kwargs):
        rtn = func(*args, **kwargs)
        if rtn is None:
            return rtn
        return rtn.get_text().strip()

    return func_wrapper


def get_if_not_none(attribute):
    def wrap(func):
        def func_wrapper(*args, **kwargs):
            rtn = func(*args, **kwargs)
            if rtn is None:
                return rtn
            return rtn.get(attribute)

        return func_wrapper

    return wrap


def len_or_none(val):
    if val is None:
        return val
    return len(val)


class SeoAudit:
    async def __init__(self, url):
        # If the url isn't provided with a scheme, prepend with `https://`
        self.url = await requests.utils.prepend_scheme_if_needed(url, "https")
        self.domain = await requests.utils.urlparse(self.url).netloc

        # Could to with adding method to handle exceptions.
        response = await requests.get(self.url)
        self.response_time = await response.elapsed.total_seconds()
        self.response_code = await response.status_code

        self.soup = await BeautifulSoup(response.text, "html.parser")

    @strip_tag
    async def get_title(self):
        return await self.soup.head.title

    @strip_tag
    async def get_first_h1(self):
        return await self.soup.body.h1

    @get_if_not_none("content")
    async def get_meta_description(self):
        return await self.soup.head.find(
            "meta", attrs={"name": re.compile(r"(?i)description")}
        )

    @get_if_not_none("charset")
    async def get_charset(self):
        return await self.soup.head.find("meta", charset=True)

    @get_if_not_none("content")
    async def get_viewport(self):
        return await self.soup.head.find("meta", attrs={"name": "viewport"})

    @get_if_not_none("href")
    async def find_amp(self):
        return await self.soup.find("link", attrs={"rel": "amphtml"})

    async def find_links(self, link_type="all"):
        if link_type not in ["all", "internal", "external"]:
            return []

        if link_type == "all":
            href_ex = await re.compile(r"^(?!#|tel:|mailto:)")
        elif link_type == "internal":
            href_ex = await re.compile(
                r"((https?:)?//(.+\.)?%s|^/[^/]*)"
                % re.sub(r"\.", "\\.", self.domain)
            )
        elif link_type == "external":
            href_ex = await self.not_domain

        a_tags = await self.soup.find_all("a", attrs={"href": href_ex})

        return [tags.get("href") for tags in a_tags]

    def not_domain(self, href):
        return href and (
            re.compile(r"^(https?:)?//").search(href)
            and not re.compile(re.sub(r"\.", "\\.", self.domain)).search(href)
        )

    def get_doctype(self):
        for item in self.soup.contents:
            if isinstance(item, Doctype):
                return item
        return None

    async def get_structured_data(self):
        json_ld = await self.soup.find_all(
            "script", attrs={"type": "application/ld+json"}
        )

        return [json.loads(x.get_text()) for x in json_ld]

    async def get_google_analytics(self):
        ga_obj = await self.soup.find_all(
            "script",
            text=re.compile(
                r"function\(i,s,o,g,r,a,m\)\{i\[\'GoogleAnalyticsObject\'\]"
            ),
        )

        return ga_obj

    async def get_seo_data(self):
        return {
            "url": await self.url,
            "domain": await self.domain,
            "title": await self.get_title(),
            "titleCount": await len(self.soup.head.find_all("title")),
            "titleLength": await len_or_none(self.get_title()),
            "responseCode": await self.response_code,
            "responseTime": await self.response_time,
            "hasCharset": await bool(self.get_charset()),
            "hasViewport": await bool(self.get_viewport()),
            "ampEnabled": await bool(self.find_amp()),
            "hasGoogleAnalytics": await bool(self.get_google_analytics()),
            "hasDuplicateGoogleAnalytics": await bool(
                len(self.get_google_analytics()) > 1
            ),
            "hasMetaDescription": await bool(self.get_meta_description()),
            "metaDescription": await self.get_meta_description(),
            "metaDescriptionLength": await len_or_none(
                self.get_meta_description()
            ),
            "hasDoctype": await bool(self.get_doctype()),
            "hasH1": await bool(self.get_first_h1()),
            "h1": await self.get_first_h1(),
            "h1Count": await len(self.soup.find_all("h1")),
            "hasH2": await bool(self.soup.find_all("h2")),
            "h2Count": await len(self.soup.find_all("h2")),
            "hasStructuredData": await bool(self.get_structured_data()),
            "structuredData": await self.get_structured_data(),
            # 'internalLinks': await self.find_links('internal'),
            "internalLinksCount": await len(self.find_links("internal")),
            # 'externalLinks': await self.find_links('external'),
            "externalLinksCount": await len(self.find_links("external")),
        }


if __name__ == "__main__":
    URL = "https://www.houseandgarden.co.uk/recipe/simple-vanilla-cake-recipe"

    page = SeoAudit(URL)

    print(json.dumps(page.get_seo_data(), indent=2))
