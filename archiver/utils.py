import os
from urllib.parse import urlparse

TO_IGNORE_EXT = {
    ".exe",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".zip",
    ".gz",
    ".iso",
    ".bat",
    ".sh",
}
TO_IGNORE_IN = {"javascript:", "mailto:"}


def write_output(url: str, visited: set):
    """
    Writes the internal links scraped to a txt file.
    """
    domain_name = urlparse(url).netloc
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
    with open(f"outputs/{domain_name}_internal_links.txt", "w") as f:
        for internal_link in visited:
            print(internal_link.strip(), file=f)


def is_valid(url: str):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def is_link_clean(href: str, domain: str):
    """
    Checks if link is clean.        
    """
    for ext in TO_IGNORE_EXT:
        if href.lower().endswith(ext):
            return False

    for st in TO_IGNORE_IN:
        if href.lower().startswith(st):
            return False
    if urlparse(href).netloc != domain:
        return False
    return True

def convert_to_valid_url(url: str):
    """ 
    Attaches scheme to schemeless urls.
    """
    
    if not urlparse(url).scheme:
        return "https://" + url
    return url