import wget
import os.path

# check if file has already been downloaded 
def download_source(url: str):
    """This function downloads data file from the given url to the working directory (cwd).

    Args:
        url: url for the source file
    """
    cwd = os.getcwd()
    filename = url.split('/')[-1]
    
    if os.path.isfile(cwd + "/" + filename):
        print(filename + ' already downloaded.')
    else:
        wget.download(url, out=cwd)