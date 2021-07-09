########################################
# Ulitilty functions
#######################################

import os
import sys
import re
import string
import langdetect
from langdetect import detect


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


def detect_language(sent):
    try:
        return detect(sent)
    except:
        return "unknown"
