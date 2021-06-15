"""Scrip to execute all the notebooks."""
import nbformat
import glob
import logging

from nbconvert.preprocessors import ExecutePreprocessor
from pathlib import Path

NOTEBOOKS_FOLDER = "notebooks/"
# List of notebooks failing in the CI for different reasons
NOTEBOOKS_TO_SKIP = [
    "notebooks/real-time-risk/main.ipynb",  # SyntaxError: invalid syntax (simple.py, line 54) TO FIX
    "notebooks/customer-churn/0_prepare_data.ipynb",  # data
    "notebooks/customer-churn/1_create_models.ipynb",  # data
    "notebooks/ifrs9/data-generation.ipynb",  # data
    "notebooks/reddit/main.ipynb",  # http 401 error TO FIX
    "notebooks/twitter/01_tweets_mining.ipynb",  # data
    "notebooks/twitter/02_sentiment.ipynb",  # data
    "notebooks/twitter/03_cryptocurrency_mining.ipynb",  # data
    "notebooks/var-benchmark/data_generator.ipynb",  # Timeout
    "notebooks/var-benchmark/main.ipynb",  # data generation timeout TO FIX
    "notebooks/geopricing/main.ipynb",  # https://github.com/atoti/notebooks/runs/2829010222 TO FIX
]

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)
notebooks_path = sorted(
    [
        notebook_path.replace(NOTEBOOKS_FOLDER, "")
        for notebook_path in glob.glob("notebooks/**/*.ipynb")
        if notebook_path not in NOTEBOOKS_TO_SKIP
    ]
)


for notebook_path in notebooks_path:
    notebook_path = Path(NOTEBOOKS_FOLDER + notebook_path)
    logging.info(f"Starting execution of {notebook_path}")
    notebook = nbformat.read(notebook_path, as_version=4)
    ep = ExecutePreprocessor(timeout=300, kernel_name="python3")
    ep.preprocess(notebook, {"metadata": {"path": notebook_path.parent}})
    logging.info(f"Execution of {notebook_path} succeed")
