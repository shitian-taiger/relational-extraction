import logging
import re
import os
import urllib
from allennlp.predictors.predictor import Predictor
from allennlp.models.archival import Archive, load_archive

class OpenIE:

    def __init__(self):
        self.model_name = "open-information-extraction"
        self.model_path = "./archived_models/openie-model.2018-08-20.tar.gz"
        self.model_url = "https://s3-us-west-2.amazonaws.com/allennlp/models/openie-model.2018-08-20.tar.gz"
        self.predictor = self._load_predictor()


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
            parsed (List): list of Tuples of form <arg1, rel, arg2>
        """
        sentence_json = { "sentence": sentence }
        pred_out = self.predictor.predict_json(sentence_json)
        return self._parse_results(pred_out)


    def _load_predictor(self):
        """ Downloads trained model as defined in:
        https://www.semanticscholar.org/paper/Supervised-Open-Information-Extraction-Stanovsky-Michael/6fc991dbc1714b425d11b4de3d9d247d21d77c0b

        Returns:
            predictor : Open IE Predictor from in allennlp.predictors
        """
        if not os.path.isdir("./archived_models"):
            os.mkdir("./archived_models")
        if not os.path.isfile(self.model_path):
            print("Downloading archived model for Supervised OIE")
            urllib.request.urlretrieve(self.model_url, self.model_path)

        archived_model = load_archive(self.model_path)
        predictor = Predictor.from_archive(archived_model)
        return predictor


    def _parse_results(self, pred_out):
        """ Given raw tagged sentence, outputs all relations in whole sentences

        Args:
            pred_out (json): Tagged from raw sentence
        Returns:
            rel_tuples: Tuples of form <arg1, rel, arg2>
        """
        rel_tuples = []
        for entry in pred_out["verbs"]:

            verb_idx = None # Retrieve sentence word index of verb for relation tuple
            for i in range(len(entry["tags"])):
                if entry["tags"][i] == 'B-V':
                    verb_idx = i

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


def main(sentence: str):
    ''' Test
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

























