import logging
import re
import os
import urllib
from functools import reduce
from typing import Tuple, Dict, List
from allennlp.predictors.predictor import Predictor
from allennlp.models.archival import Archive, load_archive

model_configs = {
    "open-information-extraction": {
        "reference": "https://www.semanticscholar.org/paper/Supervised-Open-Information-Extraction-Stanovsky-Michael/6fc991dbc1714b425d11b4de3d9d247d21d77c0b",
        "model_path": "./archived_models/openie-model.2018-08-20.tar.gz",
        "model_url": "https://s3-us-west-2.amazonaws.com/allennlp/models/openie-model.2018-08-20.tar.gz"
    },
    "named-entity-recognition": {
        "model_path": "./archived_models/ner-model.2018-12-18.tar.gz",
        "model_url": "https://s3-us-west-2.amazonaws.com/allennlp/models/ner-model-2018.12.18.tar.gz"
    },
    "dependency-parsing": {
        "model_path": "./archived_models/biaffine-dependency-parser-ptb-2018.08.23.tar.gz",
        "model_url": "https://s3-us-west-2.amazonaws.com/allennlp/models/biaffine-dependency-parser-ptb-2018.08.23.tar.gz"
    },
}



class AllenModels:

    def __init__(self, name: str, model_config: Dict):
        """ Facilitates loading of pre-trained predictors from allennlp

        Args:
            model_name:
        Returns:
            tagged (List): list of Tuples of form <word, BIO_tag>
        """
        self.model_name = name
        self.model_path = model_config["model_path"]
        self.model_url = model_config["model_url"]
        self.predictor = self._load_predictor()
        return


    def _load_predictor(self):
        """ Attempts loading of model locally, otherwise downloads file

        Returns:
            predictor : Dependent on type of model
        """
        if not os.path.isdir("./archived_models"):
            os.mkdir("./archived_models")
        if not os.path.isfile(self.model_path):
            print("Downloading archived model for %s" % self.model_name)
            urllib.request.urlretrieve(self.model_url, self.model_path)

        archived_model = load_archive(self.model_path)
        if self.model_name == "open-information-extraction":
            predictor = Predictor.from_archive(archived_model, self.model_name) # Reverts to SRL otherwise
        else:
            predictor = Predictor.from_archive(archived_model)
        return predictor


class OpenIE(AllenModels):

    def __init__(self):
        super().__init__("open-information-extraction", model_configs["open-information-extraction"])


    def get_tagged_sentence(self, sentence: str):
        """ Gets zipped sentence with BIO tag

        Args:
            sentence: raw sentence
        Returns:
            tagged (List): list of Tuples of form <word, BIO_tag>
        """
        sentence_json = { "sentence": sentence }
        pred_out = self.predictor.predict_json(sentence_json)
        words = sentence.split(" ")
        tagged = []
        for instance in pred_out["verbs"]:
            tagged.append(list(zip(words, instance["tags"]))) # Convert to list for reuse
        return tagged


    def get_tuples(self, sentence):
        """ Gets the all relationship tuples present in the sentence

        Args:
            sentence (str): raw sentence
        Returns:
            parsed (List): list of Tuples of form <arg1, rel, arg2, verb_idx>
        """
        sentence_json = { "sentence": sentence }
        pred_out = self.predictor.predict_json(sentence_json)
        return self._parse_results(pred_out)


    def _parse_results(self, pred_out):
        """ Given raw tagged sentence, outputs all relations in whole sentences

        Args:
            pred_out (json): Tagged from raw sentence
        Returns:
            rel_tuples: Tuples of form <arg1, rel, arg2, verb_idx>
        """
        rel_tuples = []
        for entry in pred_out["verbs"]:
            verb_idx : Tuple = (0, 0) # Retrieve sentence word index of verb for relation tuple
            for i in range(len(entry["tags"])):
                if entry["tags"][i] == 'B-V':
                    verb_idx = (i, i) # In case singular word verb
                elif entry["tags"][i] == 'I-V':
                    verb_idx = (verb_idx[0], i)
                else:
                    continue
            phrases = re.findall(r"\[(.*?)\]", entry["description"])
            rel, pre_args, post_args = self._retrieve_tuples(phrases)
            relation = " ".join([word.split(": ")[1] for word in rel])
            tuples = [(pre.split(": ")[1], relation, post.split(": ")[1], verb_idx) \
                        for pre in pre_args for post in post_args] # Permutate pre_args and post_args
            rel_tuples += tuples
        return rel_tuples


    def _retrieve_tuples(self, phrases):
        """ Given BIO tagged phrases in a sentence, split into args and relationship

        Args:
            phrases (list): BIO tagged phrases
        Returns:
            rel, pre_args, post_args (list): separated phrases
        """
        rel, pre_args, post_args = [], [], []
        rel_found = False
        for phrase in phrases:
            if "V:" in phrase:
                rel.append(phrase)
                rel_found = True
            elif not rel_found:
                pre_args.append(phrase)
            else:
                post_args.append(phrase)
        return rel, pre_args, post_args


class NER(AllenModels):

    def __init__(self):
        super().__init__("named-entity-recognition", model_configs["named-entity-recognition"])


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


class DepParse(AllenModels):

    def __init__(self):
        super().__init__("dependency-parsing", model_configs["dependency-parsing"])


    def get_tree(self, sentence):

        predicted = self.predictor.predict_json({"sentence" : sentence})
        predicted_heads = predicted["predicted_heads"] # Level of word
        tree = predicted["hierplane_tree"]["root"]
        return tree


def main(sentence: str):
    ''' Test OIE
    '''
    open_ie = OpenIE() # Load SupervisedOIE model
    str_relations = open_ie.get_tuples(sentence)
    tagged_sents = open_ie.get_tagged_sentence(sentence)
    for i in range(len(str_relations)):
        print(str_relations[i])
        for zip_obj in tagged_sents[i]:
            for word_pair in zip_obj:
                print(word_pair, end=" ")
        print()

sentence = "The Trump Administration is dumb, and has just started a trade war."
if __name__ == "__main__":
    main(sentence)

























