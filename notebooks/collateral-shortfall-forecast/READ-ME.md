# Forecasting Collateral Shortfalls

This project shows how to use machine learning to predict future prices of several stocks.

This analysis is derived from a previous analysis on [collateral optimisation](https://github.com/atoti/notebooks/blob/master/notebooks/collateral-shortfall-monitoring/main.ipynb) by Hui [Fang Yeo](https://www.linkedin.com/in/huifang-yeo/), which is available on our website. For contextual reasons, the two analyses start to diverge at the simulation (scenario) stage to incorporate predictive machine learning algorithms.

All the data required for this project is available in our [AWS s3 bucket](https://s3.eu-west-3.amazonaws.com/data.atoti.io/notebooks/collateral-shortfall-monitoring/) and is loaded directly when running the notebooks.

In this analysis, we demonstrate how to:

- Download asset prices using a Python library (corresponding notebook: *0-download-stock-prices-data.ipynb*).
- Process and clean the data (corresponding notebook: *1-data-preparation.ipynb*).
- Extract features from the time series data before performing machine learning (corresponding notebook: *4-create-machine-learning-pipeline.ipynb*).
- Build models to forecast asset prices at different time horizons (corresponding notebook: *4-create-machine-learning-pipeline.ipynb*).

The above steps are sequential, so the corresponding notebooks must be run sequentially.

The following additional notebooks are not mandatory to perform the above steps, but they are necessary to explore and understand the data further:

- *2-data-exploration-decompose-time-series.ipynb*: We decompose the time series and plot the resulting time subseries to isolate their trends, seasonality and residuals.
- 3-data-exploration-partial-autocorrelations.ipynb*: We analyse partial autocorrelations in time series.

These last two notebooks will allow us to make the relevant assumptions when building forecasting models, for instance in terms of: assessing the existence of a predictive signal in the time series, and defining the rolling windows to be taken into account for feature extraction.

Finally, all the necessary explanations are provided in each notebook to understand what is going on and to execute it correctly.