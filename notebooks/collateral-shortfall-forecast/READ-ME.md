# Collateral Shortfall Forecast

This project demonstrates how to use machine learning to forecast future prices of several stock market asests.

This analysis is derived from a previous one around [Collateral optimization](https://github.com/atoti/notebooks/tree/master/notebooks/collateral-shortfall-monitoring), performed by Hui [Fang Yeo](https://www.linkedin.com/in/huifang-yeo/), and available on our website. For context, the two analyses start diverging at the ‘What-If’ (scenario) stage to integrate predictive machine learning algorithms.

All the data required for this project are available our [AWS s3 bucket](https://s3.eu-west-3.amazonaws.com/data.atoti.io/notebooks/collateral-shortfall-forecast/) and are directly loaded when running the notebooks.

In this analysis, we demonstrate how to:

- Download assets prices using a Python library (corresponding notebook: *0-download-stock-prices-data.ipynb*)
- Process and cleanse the data (corresponding notebook: *1-data-preparation.ipynb*)
- Extract features from the times series data before performing machine learning (corresponding notebook: *4-create-machine-learning-pipeline.ipynb*)
- Build models to forecast the assets prices at different time horizons (corresponding notebook: *4-create-machine-learning-pipeline.ipynb*)
- Simulate projections of Collateral Shortfall at different time horizons using atoti 'what-if' scenarios (corresponding notebook: *main.ipynb*)

The steps mentioned here above are sequential so the corresponding notebooks should be run sequentially.

The following additional notebooks are not mandatory to be run to achieve the preceding steps, but they are necessary for exploring and understanding the data:

- Notebook *2-data-exploration-decompose-time-series.ipynb*: 
