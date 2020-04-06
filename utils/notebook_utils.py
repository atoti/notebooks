import wget
import os.path

# check if file is download before
def download_source(cwd: str, url: str, filename: str):
    """This function downloads data file from the given url to the working directory (cwd).

    Args:
        cwd (string): current working directory.
        url (string): url for the source file
        filename (string): filename of the downloaded file

    Examples:
        In the notebook's working directory, if the data does not exists:
        
        >>> cwd = os.getcwd()
        >>> download_source(
                cwd, 
                'http://data.atoti.io/notebooks/collateral-shortfall-monitoring/assets_positions.csv', 
                "assets_positions.csv"
            )
        100% [..................................................................................] 142 / 142
        
        If the data is already downloaded to the working directory: 
        
        >>> cwd = os.getcwd()
        >>> download_source(
                cwd, 
                'http://data.atoti.io/notebooks/collateral-shortfall-monitoring/assets_positions.csv', 
                "assets_positions.csv"
            )
        assets_positions.csv already downloaded.
    """
    if os.path.isfile(cwd + "/" + filename):
        print(filename + ' already downloaded.')
    else:
        wget.download(url, out=cwd)