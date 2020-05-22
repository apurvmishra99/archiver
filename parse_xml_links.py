import re
from path import Path

p = Path("/home/apurv/Downloads/Persepolis/Others/")


def clean_link(url: str):
    url = re.sub(r"<loc>|<\/loc>", "", url)
    return url


for f in p.walkfiles():
    if f.ext == ".xml":
        text = ""
        with open(f, "r+") as fil:
            text = fil.read()
            matches = re.findall(r"<loc>.*?<\/loc>", text, re.MULTILINE)
            matches_clean = list(map(clean_link, matches))
            with open(f.name.split(".")[0] + "_.txt", "a+") as ofile:
                for link in matches_clean:
                    print(link, file=ofile)
