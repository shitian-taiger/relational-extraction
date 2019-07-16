import logging
import numpy as np
import spacy
from torch import Tensor
from pathlib import Path
from typing import Dict, List
from enum import Enum

class constants:
    PAD_INDEX = 0
    UNK_INDEX = 1
    PADDING = "<PAD>"
    UNKNOWN = "<UNK>"


class LSTM_Direction(Enum):
    forward = 0
    backward = 1


class Vocabulary:

    def __init__(self, vocab_dir: str, words=[]):
        # Bidirectional mapping of words of indexes
        self.word_to_idx, self.idx_to_word = self._instantiate(words)
        self.vocab_len = len(self.idx_to_word)
        self.load_from_dir(vocab_dir)


    def _instantiate(self, words: List):
        word_idx_map: Dict = {}
        idx_word_map: List = []

        # Add Padding and Unknown to vocabulary
        word_idx_map[constants.PADDING] = constants.PAD_INDEX
        idx_word_map.append(constants.PADDING)
        word_idx_map[constants.UNKNOWN] = constants.UNK_INDEX
        idx_word_map.append(constants.UNKNOWN)

        # Add words to vocab
        for i, word in enumerate(words):
            word_idx_map[word] = i + 2
            idx_word_map.append(word)
        return word_idx_map, idx_word_map


    def add_word(self, word: str):
        if word in self.word_to_idx:
            logging.log(logging.WARN, "Word: [%s] already in vocab" % word)
        else:
            self.idx_to_word.append(word)
            self.word_to_idx[word] = self.vocab_len
            self.vocab_len = self.vocab_len + 1


    def load_from_dir(self, vocab_dir):
        """
        Reads tokens from tokens file with 1 token for each line
        Considering GLOVE embedding tokens and vectors are contained in one file, we preprocess it first
        """
        tokens = "tokens.txt"
        with open(Path.joinpath(vocab_dir, tokens)) as v:
            for line in v:
                if "@@UNKNOWN" in line: # Ignore UNK tag from Allen, already present in constants
                    continue
                self.add_word(line.split("\n")[0])


    def get_word_from_index(self, index: int):
        assert(index < self.vocab_len)
        return self.idx_to_word[index]


    def get_index_from_word(self, word: str):
        assert(isinstance(word, str))
        return self.word_to_idx[word] if word in self.word_to_idx else \
            self.word_to_idx[constants.UNKNOWN]


class Labels:
    # Mirror of Vocabulary for Labels
    def __init__(self, labels_dir: str):
        self.labels_len = 0
        self.tag_to_idx: Dict = {}
        self.idx_to_tag = {}
        self.load_from_dir(labels_dir)

    def load_from_dir(self, labels_dir):
        # Loads vocabulary tokens directly from file
        labels = "labels.txt"
        with open(Path.joinpath(labels_dir, labels)) as l:
            for line in l:
                self.add_word(line.split("\n")[0])

    def add_word(self, word: str):
        if word in self.tag_to_idx:
            logging.log(logging.WARN, "Tag: [%s] already in tags" % word)
        else:
            self.idx_to_tag[self.labels_len] = word
            self.tag_to_idx[word] = self.labels_len
            self.labels_len = self.labels_len + 1

    def get_word_from_index(self, index: int):
        assert(index < self.labels_len)
        return self.idx_to_tag[index]


    def get_index_from_word(self, word: str):
        assert(isinstance(word, str))
        return self.tag_to_idx[word] if word in self.tag_to_idx else \
            self.tag_to_idx["O"]


class Preprocessor:

    def __init__(self, vocab: Vocabulary, labels: Labels):
        self.spacy_nlp = spacy.load("en_core_web_sm")
        self.vocab = vocab
        self.labels = labels

    def vectorize_sentence(self, sentence: str) -> List[Dict]:
        """
        Tokenizes and indexes sentences based on given vocabulary
        Returns:
            Dictionary of sent_vec (token indexes) and pred_vec (one-hot encoded)
        """
        paired = self._pair_sentence_pred(sentence)
        vectorized_instances: List[Dict] = []
        for sent_pred_pair in paired:
            tokens, pred_index = sent_pred_pair["tokens"], sent_pred_pair["pred_index"]
            sent_vec = [self.vocab.get_index_from_word(token.text) for token in tokens] # Tokens are spacy tokens
            pred_vec = [1 if i == pred_index else 0 for i in range(len((tokens)))]
            vectorized_instances.append({ "sent_vec": np.asarray(sent_vec),
                                          "pred_vec": np.asarray(pred_vec)})
        return vectorized_instances


    def vectorize_token_tags(self, tokens: List, tags: List) -> List[Dict]:
        """
        For training purposes, tokenization is ommitted: assume training data has
        to have tagged tokenized input
        Returns:
            Dictionary of sent_vec (token indexes), pred_vec (one-hot encoded)
            and tags_vec (tag indexes)
        """
        assert(len(tokens) == len(tags))
        pred_index = tags.index("B-V") # Take Beginning of verb as predicate index
        sent_vec = [self.vocab.get_index_from_word(token) for token in tokens] # Tokens are strings
        pred_vec = [1 if i == pred_index else 0 for i in range(len((tokens)))]
        tags_vec = [self.labels.get_index_from_word(tag) for tag in tags]
        return [({ "sent_vec": np.asarray(sent_vec),
                   "pred_vec": np.asarray(pred_vec),
                   "tags_vec": np.asarray(tags_vec)})]


    def pad_batch(self, batch_instances: List[Dict]):
        """
        Pads all sentences to the maximum length of the batch to facilitate padding packed sequence
        During training, tags are likewise padded
        Arguments:
            batch_instances: List of (Dict containing indexes of tokens, one-hot encoded predicate,
                                       tags_vector [Optional])
        Returns:
            Tensors of input Dict values
        """
        tags_present = "tags_vec" in batch_instances[0]
        batch_size = len(batch_instances)
        max_len = max([len(instance["sent_vec"]) for instance in batch_instances]) # Get max length of sequence

        # Instantiate numpy array of shape (batch size, max length) with all padding indexes
        padded_batch_sentences = np.full((batch_size, max_len), constants.PAD_INDEX)
        padded_batch_preds = np.full((batch_size, max_len), constants.PAD_INDEX)
        padded_batch_tags = np.full((batch_size, max_len), constants.PAD_INDEX) # Use this only for training
        instance_lengths = [] # This is required for pack_padded_sequence
        mask = np.full((batch_size, max_len), 0) # 1 if index is valid for sentence else 0

        for i, instance in enumerate(batch_instances): # Fill batch with actual values
            sent_vec, pred_vec = instance["sent_vec"], instance["pred_vec"]
            instance_len = len(sent_vec)
            padded_batch_sentences[i, 0:instance_len] = sent_vec[:]
            padded_batch_preds[i, 0:instance_len] = pred_vec[:]

            if tags_present: # Only for training
                padded_batch_tags[i, 0:instance_len] = instance["tags_vec"][:]

            mask[i, 0:instance_len] = 1
            instance_lengths.append(instance_len)

        if tags_present:
            return (Tensor(padded_batch_sentences), Tensor(padded_batch_preds),
                    instance_lengths, Tensor(mask), Tensor(padded_batch_tags))
        else:
            return (Tensor(padded_batch_sentences), Tensor(padded_batch_preds),
                    instance_lengths, Tensor(mask))


    def tokenize(self, sentence: str):
        # Tokenize sentence to spacy Tokens including POS tags (pos_)
        return self.spacy_nlp(sentence)


    def _pair_sentence_pred(self, sentence: str) -> List[Dict]:
        """
        Tokenizes sentence, giving multiple instances of paired sentence with predicate index
        Returns: List[{ "tokens": <Spacy Tokens>, "pred_index": int }]
        """
        tokens = self.tokenize(sentence)
        predicate_indexes = [i for (i, t) in enumerate(tokens) if t.pos_ == "VERB"] # Get all indexes with predicates
        return [ {"tokens": tokens, "pred_index": idx } for idx in predicate_indexes ]



