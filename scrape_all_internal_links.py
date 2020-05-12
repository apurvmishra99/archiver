#!venv/bin/python3

import click
import requests
import re
from urllib.parse import urlparse, urljoin
import os

class PyCrawler(object):
    def __init__(self, starting_url, max_num_visited=50):
        self.starting_url = starting_url
        self.domain_name = urlparse(starting_url).netloc
        self.visited = set()
        self.max_num_visited = max_num_visited
        self.num_visited = 0
        
    @staticmethod    
    def is_valid(url):
        """
        Checks whether `url` is a valid URL.
        """
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def get_html(self, url):
        try:
            html = requests.get(url)
        except Exception as e:
            print(e)
            return ""
        return html.content.decode("latin-1")

    def get_links(self, url):
        html = self.get_html(url)
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        links = re.findall('''<a\s+(?:[^>]*?\s+)?href="([^"]*)"''', html)
        clean_links = set()
        for i, link in enumerate(links):
            # join the URL if it's relative (not absolute link)
            href = urljoin(url, link)
            parsed_href = urlparse(href)
            # remove URL GET parameters, URL fragments, etc.
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if href.startswith("http:"):
                href = href.replace("http:", "https:")
            if not PyCrawler.is_valid(href):
                # not a valid URL
                continue
            clean_links.add(href)

        return set(filter(lambda x: "mailto" not in x and urlparse(x).netloc == self.domain_name, clean_links))

    def crawl(self, url):
        for link in self.get_links(url):
            if self.num_visited >= self.max_num_visited:
                break
            if link in self.visited:
                continue
            self.visited.add(link)
            self.num_visited += 1
            click.echo(click.style(f"[*] Link: {link}", fg="green"))
            self.crawl(link)

    def start(self):
        self.crawl(self.starting_url)

@click.command()
@click.argument("url")
@click.option(
    "--max_urls",
    default=50,
    type=click.INT,
    help="The max number of urls to collect. Use 0 to set it as infinite.",
)
def main(url, max_urls):
    crawler = PyCrawler(url, max_num_visited=max_urls)
    crawler.start()
    domain_name = urlparse(url).netloc
    with open(f"{domain_name}_internal_links.txt", "w") as f:
        for internal_link in crawler.visited:
            print(internal_link.strip(), file=f)

if __name__ == "__main__":
    main()