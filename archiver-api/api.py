from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address, Request
from slowapi.errors import RateLimitExceeded
from archiver.scrape_all_internal_links import PyCrawler
from archiver.archive import Archiver
from archiver.utils import convert_to_valid_url

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return "Hello this is the API for archiver."

@app.get("/sitemap/")
@limiter.limit("5/minute")
def generate_sitemap(request: Request, url: str, limit: int = 50):
    url = convert_to_valid_url(url)
    crawler = PyCrawler(url, limit)
    crawler.start()
    result = crawler.visited
    return {"Internal Urls": result}    

@app.get("/save_all/")
@limiter.limit("5/minute")
def save_in_archive(request: Request, url:str, limit: int = 50, days: int = 7):
    url = convert_to_valid_url(url)
    archiver = Archiver(url=url, max_urls=limit, days=days)
    archiver.sync_get_unavailable()
    archiver.sync_capture()
    archive_urls = archiver.archive_urls
    return {"Archived URLS": archive_urls}