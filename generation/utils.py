import re
import json
import pandas as pd
from string import punctuation
from typing import Dict, List, Tuple

def get_sentences_oie(file_path: str):
    # Generator for sentences from `train.oie.conll` format

    df = pd.read_csv(file_path, sep="\t")
    prev_sentence = ""
    sentence = ""
    hyphen_dollar = False
    for _, row in df.iterrows():
        word = row['word']
        if row['word_id'] == 0:
            if prev_sentence == sentence:
                sentence = row['word']
                continue
            else:
                prev_sentence = sentence
                yield sentence
                sentence = row['word']
        else:
            if hyphen_dollar or word in punctuation or re.match("'.", word) or re.match("n't", word):
                if word == '$':
                    sentence = " ".join([sentence, word])
                    hyphen_dollar = True
                elif word == '-':
                    hyphen_dollar = True
                    sentence = "".join([sentence, word])
                else:
                    hyphen_dollar = False
                    sentence = "".join([sentence, word])
            else:
                sentence = " ".join([sentence, word])


def get_phrase(words: List[str]):
    phrase = ""
    hyphen_dollar = False
    for word in words:
        if hyphen_dollar or word in punctuation or re.match("'.", word) or re.match("n't", word):
            if word == '$':
                phrase = " ".join([phrase, word])
                hyphen_dollar = True
            elif word == '-':
                hyphen_dollar = True
                phrase = "".join([phrase, word])
            else:
                hyphen_dollar = False
                phrase = "".join([phrase, word])
        else:
            phrase = " ".join([phrase, word]) if phrase else "".join([phrase, word])
    return phrase


def get_sentences_ent_rel(file_path: str):
    with open(file_path, "r") as f:
        for line in f:
            try:
                parsed = json.loads(line)
                yield parsed["evidences"][0]["snippet"]
            except:
                continue


