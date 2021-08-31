import nbformat
import logging

from nbconvert.preprocessors import ExecutePreprocessor
from pathlib import Path

_MAIN = "main.ipynb"

NOTEBOOKS_DIRECTORY = Path("notebooks")
DATA_PREPROCESSING_NOTEBOOKS = [
    NOTEBOOKS_DIRECTORY / "customer-churn" / "0_prepare_data.ipynb",
    NOTEBOOKS_DIRECTORY / "customer-churn" / "1_create_models.ipynb",
    NOTEBOOKS_DIRECTORY / "ifrs9" / "data-generation.ipynb",
    NOTEBOOKS_DIRECTORY / "twitter" / "01_tweets_mining.ipynb",
    NOTEBOOKS_DIRECTORY / "twitter" / "02_sentiment.ipynb",
    NOTEBOOKS_DIRECTORY / "twitter" / "03_cryptocurrency_mining.ipynb",
    NOTEBOOKS_DIRECTORY / "influencers-analysis" / "notebooks" / "0_prepare_data.ipynb",
    NOTEBOOKS_DIRECTORY
    / "influencers-analysis"
    / "notebooks"
    / "1_create_topics.ipynb",
    NOTEBOOKS_DIRECTORY
    / "influencers-analysis"
    / "notebooks"
    / "2_analyze_topics.ipynb",
]
NOTEBOOKS_WITH_ERRORS = [
    NOTEBOOKS_DIRECTORY
    / "real-time-risk"
    / _MAIN,  # SyntaxError: invalid syntax (simple.py, line 54) TO FIX
    NOTEBOOKS_DIRECTORY / "reddit" / _MAIN,  # http 401 error TO FIX
    NOTEBOOKS_DIRECTORY / "var-benchmark" / "data_generator.ipynb",  # Timeout
    NOTEBOOKS_DIRECTORY / "var-benchmark" / _MAIN,  # data generation timeout TO FIX
    NOTEBOOKS_DIRECTORY
    / "geopricing"
    / _MAIN,  # https://github.com/atoti/notebooks/runs/2829010222 TO FIX,
]
NOTEBOOKS_TO_BE_UPDATED = [
    NOTEBOOKS_DIRECTORY / "formula-one" / _MAIN,
]
NOTEBOOKS_TO_SKIP = (
    DATA_PREPROCESSING_NOTEBOOKS + NOTEBOOKS_WITH_ERRORS + NOTEBOOKS_TO_BE_UPDATED
)


def execute_notebooks():
    notebooks_path = sorted(
        [
            notebook_path
            for notebook_path in NOTEBOOKS_DIRECTORY.glob("**/*.ipynb")
            if notebook_path not in NOTEBOOKS_TO_SKIP
            and not "ipynb_checkpoints" in str(notebook_path)
        ]
    )
    for notebook_path in notebooks_path:
        logging.info(f"Starting execution of {notebook_path}")
        notebook = nbformat.read(notebook_path, as_version=4)
        ep = ExecutePreprocessor(timeout=300, kernel_name="python3")
        ep.preprocess(notebook, {"metadata": {"path": notebook_path.parent}})
        logging.info(f"Execution of {notebook_path} succeed")


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)
    execute_notebooks()
