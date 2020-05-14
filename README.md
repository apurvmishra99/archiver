# Archive

A simple python script to generate a sitemap of a given website and archive all the pages not already stored in the wayback machine.

### Setup

```console
$ git clone https://github.com/apurvmishra99/archiver.git
$ cd archiver
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### Usage 

```console
Usage: archive.py [OPTIONS] URL

Options:
  -m, --max_urls INTEGER  The max number of urls to collect. The default value
                          is 50.Use 0 to set it as infinite.
  -d, --days INTEGER      The time difference(in days) of the current copy of
                          the page if it exists and we want to archive it
                          again. The default value is 7 days. Use 0 to archive
                          all pages again.
  --help                  Show this message and exit.
  
```
### Example

```console 
$ python archive.py --days=7 --max_urls=50 https://apurvmishra.xyz
```

### Alternative use

If you just want to scrape all the internal links on the website and write it to a txt file you can `scrape_all_internal_links.py`

### Usage

``` console 
Usage: scrape_all_internal_links.py [OPTIONS] URL

Options:
  --max_urls INTEGER  The max number of urls to collect. Use 0 to set it as
                      infinite.
  --help              Show this message and exit.
```
### Example

```console 
$ python scrape_all_internal_links.py --max_urls=50 https://apurvmishra.xyz
```

### TODO

* [ ] Package the script
* [ ] Convert to async
* [X] Add command line option to just generate the sitemap

### Tested On

```
Pop!_OS 20.04 LTS
Python v3.7.6
```
