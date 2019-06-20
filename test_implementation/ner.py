import logging
import re
import os
import urllib
from functools import reduce
from typing import List, Dict, Tuple
from allennlp.predictors.predictor import Predictor
from allennlp.models.archival import Archive, load_archive


class NER:

    def __init__(self):
        self.model_name = "named-entity-recognition"
        self.model_path = "./archived_models/ner-model.2018-12-18.tar.gz"
        self.model_url = "https://s3-us-west-2.amazonaws.com/allennlp/models/ner-model-2018.12.18.tar.gz"
        self.predictor = self._load_predictor()


    def get_tagged_tokens(self, sentence: str):
        predicted = self.predictor.predict_json({"sentence": sentence})
        words = []
        for i in range(len(predicted["tags"])):
            words.append({
                "text": predicted["words"][i],
                "ent_type": predicted["tags"][i]
            })
        return words


    def get_entities(self, words: List[Dict]):

        entities = []
        ent_idx_map = {}

        beg_idx = 0 # Keep track of beginning index
        curr_entity = ""
        for i in range(len(words)):
            word = words[i]
            ent_type, text = word["ent_type"], word["text"]
            if text == '`': # FIXME Why is this appearing as an entity in the allen NER model
                continue
            elif re.search("U-", ent_type): # Unary
                entities.append(text)
                ent_idx_map[text] = (i, i)
            elif reduce(lambda x, y: y in ent_type or x, ["B-", "I-", "L-"], False): # Check for pre-tags
                curr_entity = " ".join([curr_entity, text])
                if re.search("B-", ent_type):
                    beg_idx = i
                elif re.search("I-", ent_type):
                    continue
                elif re.search("L-", ent_type): # Last
                    entities.append(curr_entity)
                    assert (beg_idx < i)
                    ent_idx_map[curr_entity] = (beg_idx, i)
                    curr_entity = ""
            elif ent_type == "O": # Non-entity
                continue
            else:
                raise Exception("Unknown tag for NER labelling")
        return entities, ent_idx_map


    def _load_predictor(self):
        """ Downloads trained model as defined in: https://arxiv.org/pdf/1802.05365.pdf

        Returns:
            predictor : NER Predictor from in allennlp.predictors
        """
        if not os.path.isdir("./archived_models"):
            os.mkdir("./archived_models")
        if not os.path.isfile(self.model_path):
            print("Downloading archived model for NER")
            urllib.request.urlretrieve(self.model_url, self.model_path)

        archived_model = load_archive(self.model_path)
        predictor = Predictor.from_archive(archived_model)
        return predictor
