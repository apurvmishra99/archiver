#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests
import click
from urllib.parse import urljoin
from datetime import datetime, timedelta
from dateutil.parser import parse
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

def sync_get(url):
    try:
        res = requests.get(url)
        return res
    except Exception as e:
        return e


def sync_get_json(url):
    try:
        res = requests.get(url).json()
        return res["archived_snapshots"]
    except Exception as e:
        return e


def collect_links(url, max_urls):
    crawler = PyCrawler(url, max_num_visited=max_urls)
    crawler.start()
    return crawler.visited


def sync_get_unavailable(url, max_urls):
    links = collect_links(url=url, max_urls=max_urls)
    get_status = (
        (url, sync_get_json("https://archive.org/wayback/available?url=" + url))
        for url in links
    )
    for url, status in get_status:
        if isinstance(status, Exception):
            click.echo(click.style(f"cannot get status for {url} due to {status}", fg="red"))
            continue
        if not status:
            UNCACHED_LINKS.add(url)
            continue
        
        # if the capture is more than week old archive it
        now = datetime.now()
        t = parse(status["closest"]["timestamp"])
        delta = timedelta(days=7)
        if now - t > delta:
            UNCACHED_LINKS.add(url)
        else:
            click.echo((click.style(f"{url} already cached recently.", fg="blue")))

def sync_capture():
    resp_arr = (
        (link, sync_get("https://web.archive.org/save/" + link))
        for link in UNCACHED_LINKS
    )
    process(resp_arr)


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


@click.command()
@click.argument("url")
@click.option(
    "--max_urls",
    default=50,
    type=click.INT,
    help="The max number of urls to collect. Use 0 to set it as infinite.",
)
def main(url, max_urls):
    sync_get_unavailable(url, max_urls)
    sync_capture()

if __name__ == "__main__":
    main()
