# Collateral Shortfall Forecast

This project demonstrates how to use machine learning to forecast future prices of several stock market asests.

This analysis is derived from a previous one around [Collateral optimization](https://github.com/atoti/notebooks/tree/master/notebooks/collateral-shortfall-monitoring), performed by Hui [Fang Yeo](https://www.linkedin.com/in/huifang-yeo/), and available on our website. For context, the two analyses start diverging at the ‘What-If’ (scenario) stage to integrate predictive machine learning algorithms.

Check out [this article](https://www.atoti.io/articles/rapid-collateral-modelling-and-simulation-with-atoti/) to know more about wildfires in California.







The analysis we conduct in this project is based on a previous one that aimed at understanding how wildfires impact everything from air quality to solar irradiance in California.

Check out [this article](https://www.atoti.io/articles/california-wildfires-and-solar-irradiance) to know more about wildfires in California. 

Here, we try to go further by focusing on predicting what will be the criticality of ongoing wildfires in order to better anticipate their impact on the environment.

All the data required for this project are available our [AWS s3 bucket](https://s3.eu-west-3.amazonaws.com/data.atoti.io/notebooks/ca-solar/) and are directly loaded when running the notebooks.

In this analysis, we demonstrate how to:

- Pre-process the data before performing machine learning
- Extract features from the times series data
- Build a classifier to predict the category of the fires: critical or non-critical

The steps mentioned here above are sequential so the corresponding notebooks should be run sequentially.
