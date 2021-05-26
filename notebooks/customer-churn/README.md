### Understanding Telco Customer Churn

3 notebooks are available for this analysis:
- 0_prepare_data.ipynb
- 1_create_models.ipynb
- main.ipynb


__Note on data:__
These notebooks uses [Customer chur data](https://www.kaggle.com/lava18/google-play-store-apps) from xxxx.

__Notebooks:__ 
The description of the notebooks are the following:
- 0_prepare_data.ipynb:
  Prepare the data by operating various transformations: columns encoding or normalization, dimension reduction using partial least square followed by latent variables selection
- 1_create_models.ipynb
  Create and train the different predictive models on transformed data, for later comparison
- main.ipynb:
  Performs the comparison of the models (in trems of business impact) using atoti