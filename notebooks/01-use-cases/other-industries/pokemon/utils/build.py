from zipfile import ZipFile

import wget
from IPython.display import clear_output, display


def bar_custom(current, total, width=80):
    clear_output(wait=True)
    print("Downloading: %d%% [%d / %d] bytes" % (current / total * 100, current, total))


def download_dist():
    url = "https://data.atoti.io/notebooks/pokemon/dist.zip"
    filename = wget.download(url, bar=bar_custom)

    with ZipFile("dist.zip", "r") as zipObj:
        zipObj.extractall(path="extensions")
