### Forecasting Cryptocurrency prices with Twitter sentiment
4 notebooks are created for this purpose:
- [01_tweets_mining.ipynb](01_tweets_mining.ipynb)
- [02_sentiment.ipynb](02_sentiment.ipynb)
- [03_cryptocurrency_mining.ipynb](03_cryptocurrency_mining.ipynb)
- [main.ipynb](main.ipynb)


__Note on data gathering:__

<ins>Tweets mining</ins>
Before mining Tweet data, ensure that you have a [Twitter developer account](https://developer.twitter.com/en/apply-for-access) and obtain the [API access token](https://developer.twitter.com/en/docs/twitter-api/tweets/hide-replies/quick-start). We do not supply these the keys.

Refer to [01_tweets_mining.ipynb](01_tweets_mining.ipynb) on how to mine Tweets.
The ids of the Tweets used in this notebook can be downloaded [here](https://s3.eu-west-3.amazonaws.com/data.atoti.io/notebooks/twitter/tweets_sentiments.csv).

<ins>Tweet sentiments</ins>
Tweet sentiment is computed in [02_sentiment.ipynb](02_sentiment.ipynb) using TextBlob.

<ins>Cryptocurrency mining</ins>
- refer to [03_cryptocurrency_mining.ipynb](03_cryptocurrency_mining.ipynb) on how to mine Cryptocurrency returns from CoinGecko using [pycoingecko](https://github.com/man-c/pycoingecko).


__Time series analysis with atoti:__

Refer to [main.ipynb](main.ipynb) on how we perform time-series analysis on the data gathered above, using atoti to analysis the machine learning output.