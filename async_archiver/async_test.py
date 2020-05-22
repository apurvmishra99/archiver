import asyncio
import aiohttp
import uvloop
import re
from urllib.parse import urljoin, urlparse
import utils
import click
import aiorun
import signals
from bs4 import BeautifulSoup


class AsyncCrawler(object):
    def __init__(self, starting_url, max_num_visited=50):
        self.starting_url = starting_url
        self.domain_name = urlparse(starting_url).netloc
        self.seen = set()
        self.max_num_visited = max_num_visited
        self.num_visited = 0

    async def read_url(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as content:
                    return await content.text()
        except Exception as e:
            return ""

    def find_urls(self, url, content):
        parsed = urlparse(url)
        links = set(re.findall('''<a\s+(?:[^>]*?\s+)?href="([^"]*)"''', content))
        clean_links = set()
        for link in links:
            # join the URL if it's relative (/ something)
            href = urljoin(url, link)
            parsed_href = urlparse(href)
            # remove URL GET parameters, URL fragments, etc.
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if href.startswith("http:"):
                href = href.replace("http:", "https:")
            if href.endswith("/"):
                href = href[:-1]
            if not utils.is_valid(href):
                # not a valid URL
                continue
            if not utils.is_link_clean(href, self.domain_name):
                continue
            clean_links.add(href)
        return clean_links

    async def crawler(self):
        while self.num_visited < self.max_num_visited:
            current = await self.q.get()
            click.secho(f"URL: {current}", fg="green")
            self.num_visited += 1
            content = await self.read_url(current)
            for url in self.find_urls(current, content):
                if not url in self.seen:
                    self.seen.add(url)
                    self.q.put_nowait(url)
            self.q.task_done()
        else:
            tasks = asyncio.all_tasks(asyncio.get_running_loop())
            for task in tasks:
                task.cancel()
            try:
                await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
            except asyncio.CancelledError:
                await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
                raise

    async def run(self, n, url):
        self.q = asyncio.Queue()
        self.q.put_nowait(url)
        self.seen.add(url)
        tasks = [asyncio.create_task(self.crawler()) for i in range(n)]
        await self.q.join()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    def start(self, num_workers, url):
        asyncio.run(self.run(num_workers, url))


@click.command()
@click.argument("url")
@click.option(
    "--max_urls",
    default=50,
    type=click.INT,
    help="The max number of urls to collect. Use 0 to set it as infinite.",
)
def main(url, max_urls):
    url = utils.convert_to_valid_url(url)
    crawler = AsyncCrawler(url, max_num_visited=max_urls)
    num_workers = 2
    crawler.start(num_workers, url)
    utils.write_output(url, crawler.seen)


if __name__ == "__main__":
    main()
