import re
import json
import pandas as pd
from constants import Relations, POS
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


def get_sentences_ent_rel(file_path: str):
    with open(file_path, "r") as f:
        for line in f:
            try:
                parsed = json.loads(line)
                yield parsed["evidences"][0]["snippet"]
            except:
                continue



class DPHelper:

    @staticmethod
    def is_proper_noun(word: Dict) -> bool:
        return word["attributes"][0] == POS.PROPER_NOUN # TODO Find out why there can be multiple attributes

    @staticmethod
    def is_noun(word: Dict) -> bool:
        return DPHelper.is_proper_noun(word) or \
        word["attributes"][0] == POS.NOUN # TODO Find out why there can be multiple attributes

    @staticmethod
    def has_possession_by(word: Dict) -> bool:
        return len(DPHelper.get_child_type(word, Relations.POSSESSION_BY)) > 0

    @staticmethod
    def get_possessor(word: Dict) -> bool:
        assert(DPHelper.is_noun(word))
        return DPHelper.get_child_type(word, Relations.POSSESSION_BY)[0]

    @staticmethod
    def get_subject(root: Dict) -> Dict:
        # Nominal subject or clausal subject (Assume 1)
        for child in root["children"]:
            if child["link"] == Relations.NOMINAL_SUBJECT or \
               child["link"] == Relations.CLAUSAL_SUBJECT or \
               child["link"] == Relations.PASSIVE_NOM_SUBJECT:
                return child

    @staticmethod
    def get_object(root: Dict) -> Dict:
        for child in root["children"]:
            if child["link"] == Relations.DIRECT_OBJECT or \
               child["link"] == Relations.INDIRECT_OBJECT:
                return child

    @staticmethod
    def get_child_type(word: Dict, child_type: Relations) -> List[Dict]:
        if not word.get("children"):
            return[]
        else:
            return list(filter(lambda child: child["link"] == child_type, word["children"]))


    @staticmethod
    def is_leaf(word: Dict) -> bool:
        return "children" not in word


