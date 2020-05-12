#! /usr/bin/env python3

import aiohttp
import asyncio
import async_timeout
import uvloop
from bs4 import BeautifulSoup
from collections import Counter
import re
from urllib.parse import urlparse, urljoin


visited = set()

async def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


async def fetch(session, url):
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()


async def extract_local_links(url, html, root_domain):

    parsed_url = urlparse(url)
    links = re.findall('''<a\s+(?:[^>]*?\s+)?href="([^"]*)"''', html)
    for i, link in enumerate(links):
        # join the URL if it's relative (not absolute link)
        href = urljoin(parsed_url.scheme + "://" + parsed_url.netloc, link)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        vaild = await is_valid(href)
        if not vaild:
            # not a valid URL
            continue
        links[i] = href

    return set(
        filter(
            lambda x: "mailto" not in x and urlparse(x).netloc == root_domain,
            links,
        )
    )

async def crawl(url, root_domain):
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        links = await extract_local_links(url, html, root_domain)
        for link in links:
            if link in visited:
                continue
            visited.add(link)
            print(f"[*] Link: {link}")
            await crawl(link, root_domain)


async def main(url):
    async with aiohttp.ClientSession() as session:
        parsed_url = urlparse(url)
        root_domain = parsed_url.netloc
        await crawl(url, root_domain)
        with open(f"bbb_internal_links.txt", "w") as f:
            for internal_link in visited:
                print(internal_link.strip(), file=f)


uvloop.install()
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main("https://apurvmishra.xyz"))
except Exception as e:
    print(e.with_traceback())
