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
  --max_urls INTEGER  The max number of urls to collect. Use 0 to set it as
                      infinite.

  --help              Show this message and exit.
```
### Example

```console 
$ python archive.py --max_urls=50 https://apurvmishra.xyz
```

### TODO

* [ ] Package the script
* [ ] Convert to async
* [ ] Add command line option to just generate the sitemap

### Tested On

```
Pop!_OS 20.04 LTS
Python v3.7.6
```
