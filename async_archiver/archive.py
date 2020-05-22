#!/usr/bin/env python
# -*- coding: utf-8 -*-

import aiohttp
import asyncio
import uvloop
import json
import requests
import click
from dateutil.parser import parse
from datetime import datetime, timedelta
from urllib.parse import urljoin
from scrape_all_internal_links import PyCrawler


class CachedPage(Exception):
    """
    This error is raised when archive.org declines to make a new capture
    and instead returns the cached version of most recent archive.
    """

    pass


class WaybackRuntimeError(Exception):
    """
    An error returned by the Wayback Machine.
    """

    pass


class BlockedByRobots(WaybackRuntimeError):
    """
    This error is raised when archive.org has been blocked by the site's robots.txt access control instructions.
    """

    pass


UNCACHED_LINKS = set()


async def get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return response


async def get_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

def collect_links(url, max_urls):
    crawler = PyCrawler(url, max_num_visited=max_urls)
    crawler.start()
    return crawler.visited


def find_unavailable(url):
    uvloop.install()
    loop = asyncio.get_event_loop()
    links = collect_links(url=url, max_urls=10)
    coroutines = [
        get_json("https://archive.org/wayback/available?url=" + link) for link in links
    ]
    results = loop.run_until_complete(
        asyncio.gather(*coroutines, return_exceptions=True)
    )

    for url, response in zip(links, results):
        if not isinstance(response, Exception):
            if not response["archived_snapshots"]:
                UNCACHED_LINKS.add(response["url"])
                # if the capture is more than week old archive it
            now = datetime.now()
            t = parse(response["archived_snapshots"]["closest"]["timestamp"])
            delta = timedelta(days=7)
            if now - t > delta:
                UNCACHED_LINKS.add(url)
            else:
                print(f"{url} cached recently.")
        else:
            print(f"Getting status for {url} failed")


def process(resp_arr):
    for url, res in resp_arr:
        if not isinstance(res, Exception):
            try:
                archive_id = res.headers["Content-Location"]
                archive_url = urljoin("https://web.archive.org", archive_id)
                print(f"{url}: {archive_url}")
            except KeyError:
                # If it can't find that key raise the error
                click.echo(click.style(f"{url} failed due to WaybackRuntimeError", fg="red"))
        else:
            click.secho(f"{url} FAILED", fg="red")
    return


def capture():
    uvloop.install()
    loop = asyncio.get_event_loop()
    coroutines = [
        get("https://web.archive.org/save/" + link) for link in UNCACHED_LINKS
    ]
    results = loop.run_until_complete(
        asyncio.gather(*coroutines, return_exceptions=True)
    )
    process(results)
    return

@click.command()
@click.argument("url")
@click.option(
    "--max_urls",
    default=50,
    type=click.INT,
    help="The max number of urls to collect. Use 0 to set it as infinite.",
)
def main(url, max_urls):
    find_unavailable(url, max_urls)
    capture()

if __name__ == "__main__":
    main()
