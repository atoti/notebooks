import wget
import os.path

# check if file is download before
def download_source(cwd: str, url: str, filename: str):
    """This function downloads data file from the given url to the working directory.
    
    Parameters
    ----------
    cwd : string
        current work directory
    url : string
        url for the source file
    filename : string
        filename for the downloaded file
        
    Returns
    -------
    
    """
    if os.path.isfile(cwd + "/" + filename):
        print(filename + ' already downloaded.')
    else:
        wget.download(url, out=cwd)