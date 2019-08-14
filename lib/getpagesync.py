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
    def __init__(self, url):
        # If the url isn't provided with a scheme, prepend with `https://`
        self.url = requests.utils.prepend_scheme_if_needed(url, "https")
        self.domain = requests.utils.urlparse(self.url).netloc

        # Could to with adding method to handle exceptions.
        response = requests.get(self.url)
        self.response_time = response.elapsed.total_seconds()
        self.response_code = response.status_code

        self.soup = BeautifulSoup(response.text, "html.parser")

    @strip_tag
    def get_title(self):
        return self.soup.head.title

    @strip_tag
    def get_first_h1(self):
        return self.soup.body.h1

    @get_if_not_none("content")
    def get_meta_description(self):
        return self.soup.head.find(
            "meta", attrs={"name": re.compile(r"(?i)description")}
        )

    @get_if_not_none("charset")
    def get_charset(self):
        return self.soup.head.find("meta", charset=True)

    @get_if_not_none("content")
    def get_viewport(self):
        return self.soup.head.find("meta", attrs={"name": "viewport"})

    @get_if_not_none("href")
    def find_amp(self):
        return self.soup.find("link", attrs={"rel": "amphtml"})

    def find_links(self, link_type="all"):
        if link_type not in ["all", "internal", "external"]:
            return []

        if link_type == "all":
            href_ex = re.compile(r"^(?!#|tel:|mailto:)")
        elif link_type == "internal":
            href_ex = re.compile(
                r"((https?:)?//(.+\.)?%s|^/[^/]*)"
                % re.sub(r"\.", "\\.", self.domain)
            )
        elif link_type == "external":
            href_ex = self.not_domain

        a_tags = self.soup.find_all("a", attrs={"href": href_ex})

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

    def get_structured_data(self):
        json_ld = self.soup.find_all(
            "script", attrs={"type": "application/ld+json"}
        )

        return [json.loads(x.get_text()) for x in json_ld]

    def get_google_analytics(self):
        ga_obj = self.soup.find_all(
            "script",
            text=re.compile(
                r"function\(i,s,o,g,r,a,m\)\{i\[\'GoogleAnalyticsObject\'\]"
            ),
        )

        return ga_obj

    def get_seo_data(self):
        return {
            "url": self.url,
            "domain": self.domain,
            "title": self.get_title(),
            "titleCount": len(self.soup.head.find_all("title")),
            "titleLength": len_or_none(self.get_title()),
            "responseCode": self.response_code,
            "responseTime": self.response_time,
            "hasCharset": bool(self.get_charset()),
            "hasViewport": bool(self.get_viewport()),
            "ampEnabled": bool(self.find_amp()),
            "hasGoogleAnalytics": bool(self.get_google_analytics()),
            "hasDuplicateGoogleAnalytics": bool(
                len(self.get_google_analytics()) > 1
            ),
            "hasMetaDescription": bool(self.get_meta_description()),
            "metaDescription": self.get_meta_description(),
            "metaDescriptionLength": len_or_none(self.get_meta_description()),
            "hasDoctype": bool(self.get_doctype()),
            "hasH1": bool(self.get_first_h1()),
            "h1": self.get_first_h1(),
            "h1Count": len(self.soup.find_all("h1")),
            "hasH2": bool(self.soup.find_all("h2")),
            "h2Count": len(self.soup.find_all("h2")),
            "hasStructuredData": bool(self.get_structured_data()),
            "structuredData": self.get_structured_data(),
            # 'internalLinks': self.find_links('internal'),
            "internalLinksCount": len(self.find_links("internal")),
            # 'externalLinks': self.find_links('external'),
            "externalLinksCount": len(self.find_links("external")),
        }


if __name__ == "__main__":
    URL = "https://www.houseandgarden.co.uk/recipe/simple-vanilla-cake-recipe"

    page = SeoAudit(URL)

    print(json.dumps(page.get_seo_data(), indent=2))
