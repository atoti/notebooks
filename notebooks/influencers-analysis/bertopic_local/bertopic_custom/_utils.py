import numpy as np
import logging
from collections.abc import Iterable
from scipy.sparse.csr import csr_matrix
import os
import sys
import re
import string


class MyLogger:
    def __init__(self, level):
        self.logger = logging.getLogger("BERTopic")
        self.set_level(level)
        self._add_handler()
        self.logger.propagate = False

    def info(self, message):
        self.logger.info("{}".format(message))

    def set_level(self, level):
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level in levels:
            self.logger.setLevel(level)

    def _add_handler(self):
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(message)s"))
        self.logger.addHandler(sh)

        # Remove duplicate handlers
        if len(self.logger.handlers) > 1:
            self.logger.handlers = [self.logger.handlers[0]]


def check_documents_type(documents):
    """Check whether the input documents are indeed a list of strings"""
    if isinstance(documents, Iterable) and not isinstance(documents, str):
        if not any([isinstance(doc, str) for doc in documents]):
            raise TypeError("Make sure that the iterable only contains strings.")

    else:
        raise TypeError(
            "Make sure that the documents variable is an iterable containing strings only."
        )


def check_embeddings_shape(embeddings, docs):
    """Check if the embeddings have the correct shape"""
    if embeddings is not None:
        if not any(
            [isinstance(embeddings, np.ndarray), isinstance(embeddings, csr_matrix)]
        ):
            raise ValueError(
                "Make sure to input embeddings as a numpy array or scipy.sparse.csr.csr_matrix. "
            )
        else:
            if embeddings.shape[0] != len(docs):
                raise ValueError(
                    "Make sure that the embeddings are a numpy array with shape: "
                    "(len(docs), vector_dim) where vector_dim is the dimensionality "
                    "of the vector embeddings. "
                )


def check_is_fitted(model):
    """Checks if the model was fitted by verifying the presence of self.matches
    Arguments:
        model: BERTopic instance for which the check is performed.
    Returns:
        None
    Raises:
        ValueError: If the matches were not found.
    """
    msg = (
        "This %(name)s instance is not fitted yet. Call 'fit' with "
        "appropriate arguments before using this estimator."
    )

    if not model.topics:
        raise ValueError(msg % {"name": type(model).__name__})


# Added by Ariel Ibaba on April 7 2021

# Remove web links
def remove_links(text):
    link_regex = re.compile(
        "((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)", re.DOTALL
    )
    links = re.findall(link_regex, text)
    for link in links:
        text = text.replace(link[0], " , ")
    return text


# Remove: email adresses, and all hashtags but the first one
def remove_emails_hashtags(text):
    entity_prefixes = ["@", "#", "_"]
    for separator in string.punctuation:
        if separator not in entity_prefixes:
            text = text.replace(separator, " ")
    words = []
    hastag_counts = 0
    for word in text.split():
        word = word.strip()
        if "#" in word:
            hastag_counts += 1
        if word:
            if "#" in word and hastag_counts < 2 or word[0] not in entity_prefixes:
                words.append(word)

    return " ".join(words)


# Doing all at the at the same time
def cleanse_text(text):
    return remove_emails_hashtags(remove_links(text))


def remove_stopwords(text, stop_words):
    for sw in stop_words:
        reg = r"\b" + sw + r"\b"
        text = re.sub(reg, " ", text, flags=re.IGNORECASE)
        text = " ".join(text.split())
    return text


def replace_words(text, words_dic):
    for k, v in words_dic.items():
        reg = r"\b" + k + r"\b"
        text = re.sub(reg, v, text, flags=re.IGNORECASE)
    return text
