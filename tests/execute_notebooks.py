import os
import nbformat
import logging

from nbconvert.preprocessors import ExecutePreprocessor
from pathlib import Path

_MAIN = "main.ipynb"

NOTEBOOKS_DIRECTORY = Path("notebooks")
DATA_PREPROCESSING_NOTEBOOKS = [
    # Financial notebooks
    # credit-risk
    "ifrs9/data-generation.ipynb",
    # operation risk notebooks
    "credit-card-fraud-detection/01-Synthetic-data-generation.ipynb",
    "credit-card-fraud-detection/02-AutoML-PyCaret-anomaly.ipynb",
    "credit-card-fraud-detection/03-AutoML-PyCaret-classification.ipynb",
    # Portfolio management
    "cvar-optimizer/01_data_generation.ipynb",
    # insurance notebooks
    "customer360/01-Dataupload-to-Vertica.ipynb",
    # other industries
    "ca-solar/01-nrel-data-sourcing.ipynb",
    "ca-solar/02-fire-data-sourcing.ipynb",
    "customer-churn/0_prepare_data.ipynb",
    "customer-churn/1_create_models.ipynb",
    "twitter/01_tweets_mining.ipynb",
    "twitter/02_sentiment.ipynb",
    "twitter/03_cryptocurrency_mining.ipynb",
    "influencers-analysis/notebooks/0_prepare_data.ipynb",
    "object-detection/main.ipynb",
    "object-detection/main_demo.ipynb",
    "object-detection/main_generate_csv.ipynb",
    "influencers-analysis/notebooks/1_create_topics.ipynb",
    "influencers-analysis/notebooks/2_analyze_topics.ipynb",
    # tech tutorials
    "var-benchmark/data_generator.ipynb",  # Timeout
]
NOTEBOOKS_WTIH_ALT_CONNECTORS = [
    "customer360/02-main-vertica-db.ipynb",
    f"real-time-risk/{_MAIN}",
    f"auto-cube/{_MAIN}",
    f"reddit/{_MAIN}",  # http 401 error TO FIX
    f"var-benchmark/{_MAIN}",  # data generation timeout TO FIX
]
ATOTI_PLUS_NOTEBOOKS = [
    "security-implementation/01-Basic-authentication.ipynb",
    "security-implementation/02-OIDC-Auth0.ipynb",
    "security-implementation/03-OIDC-Google.ipynb",
    "security-implementation/04-LDAP.ipynb",
    f"security-implementation/{_MAIN}",
    f"internationalization/{_MAIN}",
]
NON_ATOTI_NOTEBOOKS = [
    # financial - treasury
    "collateral-shortfall-forecast/notebooks/0-download-stock-prices-data.ipynb",
    "collateral-shortfall-forecast/notebooks/1-data-preparation.ipynb",
    "collateral-shortfall-forecast/notebooks/2-data-exploration-decompose-time-series.ipynb",
    "collateral-shortfall-forecast/notebooks/3-data-exploration-partial-autocorrelations.ipynb",
    "collateral-shortfall-forecast/notebooks/4-create-machine-learning-pipeline.ipynb",
    # other industries
    "wildfire-prediction/notebooks/0-prepare-the-datasets.ipynb",
    "wildfire-prediction/notebooks/1-roll-the-datasets.ipynb",
    "wildfire-prediction/notebooks/2-extract-the-features-test.ipynb",
    "wildfire-prediction/notebooks/2-extract-the-features-train.ipynb",
    "wildfire-prediction/notebooks/2-extract-the-features-val.ipynb",
    "wildfire-prediction/notebooks/3-classification-with-OPLS.ipynb",
]
NOTEBOOKS_WITH_ERRORS = [
    "credit-card-fraud-detection/main.ipynb",  # pycaret dependency conflict with atoti 0.6.5 (numpy)
    "sbm/main.ipynb",  # broken in 0.6.3 https://github.com/atoti/atoti/issues/413
    f"geopricing/{_MAIN}",  # https://github.com/atoti/notebooks/runs/2829010222 TO FIX,
    # f"collateral-shortfall-forecast/notebooks/{_MAIN}",  # removed tsfresh due to conflict with protobuf
]
NOTEBOOKS_TO_SKIP = sorted(
    DATA_PREPROCESSING_NOTEBOOKS
    + NOTEBOOKS_WITH_ERRORS
    + NOTEBOOKS_WTIH_ALT_CONNECTORS
    + NON_ATOTI_NOTEBOOKS
    + ATOTI_PLUS_NOTEBOOKS
)


def execute_notebooks():
    notebooks_path = sorted(
        [
            notebook_path
            for notebook_path in NOTEBOOKS_DIRECTORY.glob("**/*.ipynb")
            if "ipynb_checkpoints" not in str(notebook_path)
            and not any(
                str(notebook_path).endswith(os.path.normpath(exclude_nb))
                for exclude_nb in NOTEBOOKS_TO_SKIP
            )
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
