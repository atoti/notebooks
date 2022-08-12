import nbformat
import logging

from nbconvert.preprocessors import ExecutePreprocessor
from pathlib import Path

_MAIN = "main.ipynb"

DIR_FIN_RM_CR = Path("notebooks" / "01-use-cases" / "finance"/ "risk-management" / "credit-risk")
DIR_FIN_RM_LR = Path("notebooks" / "01-use-cases" / "finance"/ "risk-management" / "liquidity-risk")
DIR_FIN_RM_MR = Path("notebooks" / "01-use-cases" / "finance"/ "risk-management" / "market-risk")
DIR_FIN_RM_OR = Path("notebooks" / "01-use-cases" / "finance"/ "risk-management" / "operational-risk")
DIR_FIN_FO = Path("notebooks" / "01-use-cases" / "finance"/ "front-offices")
DIR_FIN_IN = Path("notebooks" / "01-use-cases" / "finance"/ "insurance")
DIR_FIN_PM = Path("notebooks" / "01-use-cases" / "finance"/ "portfolio-management")
DIR_FIN_TR = Path("notebooks" / "01-use-cases" / "finance"/ "treasury")
DIR_OTHERS_IND = Path("notebooks" / "01-use-cases" / "other-industries")
DIR_TECH_TUTORIAL = Path("notebooks" / "02-technical-tutorials")

DATA_PREPROCESSING_NOTEBOOKS = [
# Financial notebooks

	# credit-risk 
	DIR_FIN_RM_CR / "ifrs9" / "data-generation.ipynb",

	# operation risk notebooks
    DIR_FIN_RM_OR
    / "credit-card-fraud-detection"
    / "01-Synthetic-data-generation.ipynb",
    DIR_FIN_RM_OR
    / "credit-card-fraud-detection"
    / "02-AutoML-PyCaret-anomaly.ipynb",
    DIR_FIN_RM_OR
    / "credit-card-fraud-detection"
    / "03-AutoML-PyCaret-classification.ipynb",

    
	# insurance notebooks
    DIR_FIN_IN / "customer360" / "01-Dataupload-to-Vertica.ipynb",

	# other industries
    DIR_OTHERS_IND / "ca-solar" / "01-nrel-data-sourcing.ipynb",
    DIR_OTHERS_IND / "ca-solar" / "02-fire-data-sourcing.ipynb",
    DIR_OTHERS_IND / "customer-churn" / "0_prepare_data.ipynb",
    DIR_OTHERS_IND / "customer-churn" / "1_create_models.ipynb",
    DIR_OTHERS_IND / "twitter" / "01_tweets_mining.ipynb",
    DIR_OTHERS_IND / "twitter" / "02_sentiment.ipynb",
    DIR_OTHERS_IND / "twitter" / "03_cryptocurrency_mining.ipynb",
    DIR_OTHERS_IND / "influencers-analysis" / "notebooks" / "0_prepare_data.ipynb",
    DIR_OTHERS_IND / "object-detection" / "main.ipynb",
    DIR_OTHERS_IND / "object-detection" / "main_demo.ipynb",
    DIR_OTHERS_IND / "object-detection" / "main_generate_csv.ipynb",
    DIR_OTHERS_IND
    / "influencers-analysis"
    / "notebooks"
    / "1_create_topics.ipynb",
    DIR_OTHERS_IND
    / "influencers-analysis"
    / "notebooks"
    / "2_analyze_topics.ipynb",
	
	# tech tutorials
    DIR_TECH_TUTORIAL / "var-benchmark" / "data_generator.ipynb",  # Timeout
]
NOTEBOOKS_WTIH_ALT_CONNECTORS = [
    DIR_FIN_IN / "customer360" / "02-main-vertica-db.ipynb",
	DIR_FIN_FO
    / "real-time-risk"
    / _MAIN,  
    DIR_OTHERS_IND / "auto-cube" / _MAIN,	
	DIR_OTHERS_IND / "reddit" / _MAIN,  # http 401 error TO FIX
    DIR_TECH_TUTORIAL / "var-benchmark" / _MAIN,  # data generation timeout TO FIX
]
ATOTI_PLUS_NOTEBOOKS = [
    DIR_TECH_TUTORIAL / "security-implementation" / "01-Basic-authentication.ipynb",
    DIR_TECH_TUTORIAL / "security-implementation" / "02-OIDC-Auth0.ipynb",
    DIR_TECH_TUTORIAL / "security-implementation" / "03-OIDC-Google.ipynb",
    DIR_TECH_TUTORIAL / "security-implementation" / "04-LDAP.ipynb",
    DIR_TECH_TUTORIAL / "security-implementation" / _MAIN,
]
NON_ATOTI_NOTEBOOKS = [
	# financial - treasury
    DIR_FIN_TR
    / "collateral-shortfall-forecast"
    / "notebooks"
    / "0-download-stock-prices-data.ipynb",
    DIR_FIN_TR
    / "collateral-shortfall-forecast"
    / "notebooks"
    / "1-data-preparation.ipynb",
    DIR_FIN_TR
    / "collateral-shortfall-forecast"
    / "notebooks"
    / "2-data-exploration-decompose-time-series.ipynb",
    DIR_FIN_TR
    / "collateral-shortfall-forecast"
    / "notebooks"
    / "3-data-exploration-partial-autocorrelations.ipynb",
    DIR_FIN_TR
    / "collateral-shortfall-forecast"
    / "notebooks"
    / "4-create-machine-learning-pipeline.ipynb",
	
	# other industries
    DIR_OTHERS_IND
    / "wildfire-prediction"
    / "notebooks"
    / "0-prepare-the-datasets.ipynb",
    DIR_OTHERS_IND
    / "wildfire-prediction"
    / "notebooks"
    / "1-roll-the-datasets.ipynb",
    DIR_OTHERS_IND
    / "wildfire-prediction"
    / "notebooks"
    / "2-extract-the-features-test.ipynb",
    DIR_OTHERS_IND
    / "wildfire-prediction"
    / "notebooks"
    / "2-extract-the-features-train.ipynb",
    DIR_OTHERS_IND
    / "wildfire-prediction"
    / "notebooks"
    / "2-extract-the-features-val.ipynb",
    DIR_OTHERS_IND
    / "wildfire-prediction"
    / "notebooks"
    / "3-classification-with-OPLS.ipynb",
]
NOTEBOOKS_WITH_ERRORS = [
    DIR_FIN_RM_OR
    / "credit-card-fraud-detection"
    / "main.ipynb",  # pycaret dependency conflict with atoti 0.6.5 (numpy)
    DIR_FIN_RM_MR
    / "sbm"
    / "main.ipynb",  # broken in 0.6.3 https://github.com/atoti/atoti/issues/413   
    DIR_OTHERS_IND
    / "geopricing"
    / _MAIN,  # https://github.com/atoti/notebooks/runs/2829010222 TO FIX,

]
NOTEBOOKS_TO_SKIP = (
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
