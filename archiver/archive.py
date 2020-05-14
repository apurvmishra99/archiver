#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests
import click
from urllib.parse import urljoin
from datetime import datetime, timedelta
from dateutil.parser import parse
from archiver.scrape_all_internal_links import PyCrawler

class Archiver(object):
    def __init__(self, url: str, max_urls: int = 50, days: int = 7):
        self.UNCACHED_LINKS = set()
        self.AVAILABLE_ENDPOINT = "https://archive.org/wayback/available?url="
        self.SAVE_ENDPOINT = "https://archive.org/wayback/available?url="
        self.start_url = url
        self.max_urls = max_urls
        self.days = days
        self.archive_urls = []
                
    def sync_get(self, url):
        try:
            res = requests.get(url)
            return res
        except Exception as e:
            return e


    def sync_get_json(self, url):
        try:
            res = requests.get(url).json()
            return res["archived_snapshots"]
        except Exception as e:
            return e


    def collect_links(self):
        crawler = PyCrawler(self.start_url, max_num_visited=self.max_urls)
        crawler.start()
        return crawler.visited


    def sync_get_unavailable(self):
        links = self.collect_links()
        get_status = (
            (url, self.sync_get_json(self.AVAILABLE_ENDPOINT + url))
            for url in links
        )
        for url, status in get_status:
            if isinstance(status, Exception):
                click.echo(
                    click.style(f"cannot get status for {url} due to {status}", fg="red")
                )
                continue
            if not status:
                self.UNCACHED_LINKS.add(url)
                continue

            # if the capture is more than {self.days} old archive it again
            now = datetime.now()
            t = parse(status["closest"]["timestamp"])
            delta = timedelta(days=self.days)
            if now - t > delta:
                self.UNCACHED_LINKS.add(url)
            else:
                click.echo((click.style(f"{url} already cached recently.", fg="blue")))


    def sync_capture(self):
        resp_arr = (
            (link, self.sync_get(self.SAVE_ENDPOINT + link))
            for link in self.UNCACHED_LINKS
        )
        self.process(resp_arr)


    def process(self, resp_arr):
        for url, res in resp_arr:
            if not isinstance(res, Exception):
                try:
                    archive_id = res.headers["Content-Location"]
                    archive_url = urljoin("https://web.archive.org", archive_id)
                    click.secho(f"{url}: {archive_url}", fg="yellow")
                    self.archive_urls.append(f"{url}: {archive_url}")
                except KeyError:
                    # If it can't find that key raise the error
                    click.echo(
                        click.style(f"{url} failed due to WaybackRuntimeError", fg="red")
                    )
                    self.archive_urls.append(f"{url} failed due to WaybackRuntimeError")
            else:
                click.secho(f"{url} FAILED", fg="red")
                self.archive_urls.append(f"{url} FAILED")
        return


@click.command()
@click.argument("url")
@click.option(
    "--max_urls",
    "-m",
    default=50,
    type=click.INT,
    help="The max number of urls to collect. The default value is 50.Use 0 to set it as infinite.",
)
@click.option(
    "--days",
    "-d",
    default=7,
    type=click.INT,
    help="The time difference(in days) of the current copy of the page if it exists and we want to archive it again. The default value is 7 days. Use 0 to archive all pages again.",
)
def main(url, max_urls, days):
    archiver = Archiver(url=url, max_urls=max_urls, days=days)
    archiver.sync_get_unavailable()
    archiver.sync_capture()


if __name__ == "__main__":
    main()
