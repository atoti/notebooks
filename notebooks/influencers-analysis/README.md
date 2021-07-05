# Twitter influencers analysis


In this project, we perform an analysis of top Twitter AI influencers.
We:

- Perform topics extraction from AI influencers tweets
- Perform a ranking of influencers based on the popularity of their tweets, according to specific metrics that we define

To perform topics extraction in this project, we use our custom implemention of BERTopic, a topic modeling technique that leverages hugs transformers and c-TF-IDF to create dense clusters allowing for easily interpretable topics whilst keeping important words in the topic descriptions. You can find details on our custom implementation in this [medium post](https://medium.com/atoti/topic-modeling-on-twitter-using-sentence-bert-8acdad958eb1).


Note that you can use the original implementation of BERTopic instead if you prefer, that you can find [here](https://maartengr.github.io/BERTopic/). If you do so, you should not use the following notebooks:

- 1_create_topics.ipynb
- 2_analyze_topics.ipynb

You should perform your topics extraction following the tutorial in the BERTopic repository instead.


## Installation of our custom BERTopic

To perform the topics extraction, we use our custom implementation of BERTopic library.
To achieve this, we can use a local installation as our custom package is not published.

You can find the detail of our custom

Follow these steps to install a local package(Custom BERTopic):
```
git clone https://github.com/atoti/notebooks.git
cd ../gitclonedirectory/notebooks/influencers-analysis/bertopic_local
pip install -e .
```