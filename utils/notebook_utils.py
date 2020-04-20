import wget
import os.path

# check if file has already been downloaded 
def download_source(url: str, filename: str):
    """This function downloads data file from the given url to the working directory (cwd).

    Args:
        cwd: current working directory.
        url: url for the source file
        filename: filename of the downloaded file
    """
    cwd = os.getcwd()
    if os.path.isfile(cwd + "/" + filename):
        print(filename + ' already downloaded.')
    else:
        wget.download(url, out=cwd)