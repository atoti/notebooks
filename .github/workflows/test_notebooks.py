import nbformat
import glob
import logging
import os

from nbconvert.preprocessors import ExecutePreprocessor

NOTEBOOKS_TO_SKIP = [
    "notebooks/sub-population-analysis/main.ipynb",
    "notebooks/real-time-risk/main.ipynb",
]

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
notebooks_path = [notebook_path for notebook_path in glob.glob("notebooks/**/*.ipynb") if notebook_path not in NOTEBOOKS_TO_SKIP]


for notebook_path in notebooks_path:
    # Cleaning content of temp folder for the next test
    for temp_files in glob.glob("temp/"):
        if temp_files != "temp/":
            os.remove(temp_files)
    logging.info(f"Start execution of {notebook_path}")
    notebook = nbformat.read(notebook_path, as_version=4)
    ep = ExecutePreprocessor(timeout=6000, kernel_name='python3')
    ep.preprocess(notebook, {'metadata': {'path': 'temp/'}})
    logging.info(f"Execution of {notebook_path} succeed")