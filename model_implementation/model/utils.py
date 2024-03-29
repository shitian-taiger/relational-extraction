import logging
import numpy as np
import spacy
from torch import Tensor
from pathlib import Path
from typing import Dict, List
from enum import Enum


class Constants:
    PAD_INDEX = 0
    UNK_INDEX = 1
    PADDING = "<PAD>"
    UNKNOWN = "<UNK>"


class LSTM_Direction(Enum):
    forward = 0
    backward = 1


class POS:
    """
    Bidirectional mapping of POS of indexes
    """
    def __init__(self, pos_dir: str):
        self.pos_to_idx, self.idx_to_pos = {}, {}
        self.pos_len = 0
        self.load_from_dir(pos_dir)


    def load_from_dir(self, pos_dir):
        """
        Reads pos tags from file and map to dictionaries
        """
        with open(Path.joinpath(pos_dir, "pos.txt")) as p:
            for line in p:
                pos_tag = line.split("\n")[0]
                self.pos_to_idx[pos_tag] = self.pos_len
                self.idx_to_pos[self.pos_len] = pos_tag
                self.pos_len += 1


    def get_pos_from_index(self, index: int):
        return self.idx_to_pos[index]


    def get_index_from_pos(self, pos: str):
        return self.pos_to_idx[pos]


class Vocabulary:
    """
    Bidirectional mapping of words of indexes
    """
    def __init__(self, vocab_dir: str, words=[]):
        self.word_to_idx, self.idx_to_word = self._instantiate(words)
        self.vocab_len = len(self.idx_to_word)
        self.load_from_dir(vocab_dir)


    def _instantiate(self, words: List):
        word_idx_map: Dict = {}
        idx_word_map: List = []

        # Add Padding and Unknown to vocabulary
        word_idx_map[Constants.PADDING] = Constants.PAD_INDEX
        idx_word_map.append(Constants.PADDING)
        word_idx_map[Constants.UNKNOWN] = Constants.UNK_INDEX
        idx_word_map.append(Constants.UNKNOWN)

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
                if "@@UNKNOWN" in line: # Ignore UNK tag from Allen, already present in Constants
                    continue
                self.add_word(line.split("\n")[0])


    def get_word_from_index(self, index: int):
        assert(index < self.vocab_len)
        return self.idx_to_word[index]


    def get_index_from_word(self, word: str):
        assert(isinstance(word, str))
        return self.word_to_idx[word] if word in self.word_to_idx else \
            self.word_to_idx[Constants.UNKNOWN]


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

    def __init__(self, vocab: Vocabulary, labels: Labels, pos: POS):
        self.spacy_nlp = spacy.load("en_core_web_sm")
        self.vocab = vocab
        self.labels = labels
        self.pos = pos


    def vectorize_sentence(self, sentence: str) -> List[Dict]:
        """
        Purely for prediction purposes, tokenizes and generates vectors for entity and part-of-speech
        Returns:
            Dictionary of sent_vec (token indexes), ent_vec (1 for ENT1, 2 for ENT2, 0 otherwise),
            pos_vec (index of POS tag of each token)
        """
        paired = self._pair_sentence_ent(sentence)
        vectorized_instances: List[Dict] = []
        for sent_pred_pair in paired:
            tokens, ents_index = sent_pred_pair["tokens"], sent_pred_pair["ents_index"]
            sent_vec = [self.vocab.get_index_from_word(token.text) for token in tokens] # Tokens are spacy tokens
            ent_vec = [1 if i in ents_index[0] else 2 if i in ents_index[1] else 0 for i in range(len(tokens))]
            pos_vec = [self.pos.get_index_from_pos(token.pos_) for token in tokens]
            vectorized_instances.append({ "sent_vec": np.asarray(sent_vec),
                                          "ent_vec": np.asarray(ent_vec),
                                          "pos_vec": np.asarray(pos_vec)
                                          })
        return vectorized_instances


    def vectorize_token_tags(self, tokens: List, tags: List, pos: List) -> List[Dict]:
        """
        For training purposes, tokenization is ommitted: assume training data has
        to have tagged tokenized input
          - tags_vec labels ENT labels as O since loss only considers REL tags
        Returns:
            Dictionary of sent_vec (token indexes), ent_vec (1 for ENT1, 2 for ENT2, 0 otherwise),
            pos_vec (index of POS tag of each token) and tags_vec (tag indexes)
        """
        assert(len(tokens) == len(tags))
        sent_vec = [self.vocab.get_index_from_word(token) for token in tokens] # Tokens are strings
        ent_vec = [1 if "ENT1" in label else 2 if "ENT2" in label else 0 for label in tags]
        pos_vec = [self.pos.get_index_from_pos(word_pos) for word_pos in pos]
        tags_vec = [self.labels.get_index_from_word(tag) for tag in tags]
        return [({ "sent_vec": np.asarray(sent_vec),
                   "ent_vec": np.asarray(ent_vec),
                   "tags_vec": np.asarray(tags_vec),
                   "pos_vec": np.asarray(pos_vec)
                   })]


    def pad_batch(self, batch_instances: List[Dict]):
        """
        Pads all sentences to the maximum length of the batch to facilitate padding packed sequence
        During training, tags are likewise padded
        Arguments:
            batch_instances: List of output of vectorize_token_tags -
                             (Dict of token_vector, entity_vector, pos_vector, tags_vector [Optional])
        Returns:
            Tensors of input Dict values
        """
        tags_present = "tags_vec" in batch_instances[0]
        batch_size = len(batch_instances)
        max_len = max([len(instance["sent_vec"]) for instance in batch_instances]) # Get max length of sequence

        # Instantiate numpy array of shape (batch size, max length) with all padding indexes
        padded_batch_sentences = np.full((batch_size, max_len), Constants.PAD_INDEX)
        padded_batch_ents = np.full((batch_size, max_len), Constants.PAD_INDEX)
        padded_batch_pos = np.full((batch_size, max_len), Constants.PAD_INDEX)
        padded_batch_tags = np.full((batch_size, max_len), Constants.PAD_INDEX) # Use this only for training
        instance_lengths = [] # This is required for pack_padded_sequence
        mask = np.full((batch_size, max_len), 0) # 1 if index is valid for sentence else 0

        for i, instance in enumerate(batch_instances): # Fill batch with actual values
            sent_vec, ent_vec, pos_vec = instance["sent_vec"], instance["ent_vec"], instance["pos_vec"]
            instance_len = len(sent_vec)
            padded_batch_sentences[i, 0:instance_len] = sent_vec[:]
            padded_batch_ents[i, 0:instance_len] = ent_vec[:]
            padded_batch_pos[i, 0:instance_len] = pos_vec[:]

            if tags_present: # Only for training
                padded_batch_tags[i, 0:instance_len] = instance["tags_vec"][:]

            mask[i, 0:instance_len] = 1
            instance_lengths.append(instance_len)

        if tags_present:
            return (Tensor(padded_batch_sentences), Tensor(padded_batch_ents), Tensor(padded_batch_pos),
                    instance_lengths, Tensor(mask), Tensor(padded_batch_tags))
        else:
            return (Tensor(padded_batch_sentences), Tensor(padded_batch_ents), Tensor(padded_batch_pos),
                    instance_lengths, Tensor(mask))


    def tokenize(self, sentence: str):
        # Tokenize sentence to spacy Tokens including POS tags (pos_)
        return self.spacy_nlp(sentence)


    def _pair_sentence_ent(self, sentence: str) -> List[Dict]:
        """
        Tokenizes and generates index pairs of entities (external NER detection)
        Returns:
            List of Dict each: { sentence as list of Spacy tokens,
                                 pair of entity indexes as Tuple of 2 lists containing their indexes }
        """
        tokens = self.tokenize(sentence)
        ent_idx_map = self._get_entity_idx_map(tokens)
        ent_idxs = list(ent_idx_map.values())
        ent_pairs = []
        # Create instances for permutations of entities
        # TODO Swapped entity order as well to accomodate directional relation
        for i, ent1_idx in enumerate(ent_idxs):
            ent1_idxs = list(range(ent1_idx[0], ent1_idx[1] + 1))
            ent_pairs = ent_pairs + [(ent1_idxs, list(range(ent2_idx[0], ent2_idx[1] + 1))) for ent2_idx in ent_idxs[i+1:]]
        return [ {"tokens": tokens, "ents_index": idxs } for idxs in ent_pairs ]


    def _get_entity_idx_map(self, tokens: List) -> Dict:
        """
        NER detection using external methods
        TODO Incorporate upstream NER
        Returns:
            Dictionary with key: (Entity: str), value: (Start and End index of entity within sentence: Tuple)
        """

        words : List[Dict] = [ {"text": token.text,
                "ent_type": token.ent_type_ if not token.ent_type_ == "" else None,
                } for token in tokens ]
        noun_chunks = [(ent.start, ent.end - 1) for ent in tokens.noun_chunks]
        named_ents = []
        for chunk in noun_chunks: # Consolidate entity tags to named entity chunks
            if words[chunk[0]]["ent_type"] is not None:
                named_ents.append(chunk)
            elif words[chunk[0]]["text"].lower() == "the": # Allow first word of named entity chunk to be 'the'
                if words[chunk[1]]["ent_type"] is not None:
                    named_ents.append(chunk)
        entities: List[str] = [] # String entities
        ent_idx_map: Dict = {} # Entity index corresponding to entities
        for named_ent in (named_ents):
            start, end = named_ent[0], named_ent[1]
            entity = " ".join([words[i]["text"] for i in range(start, end + 1)])
            entities.append(entity)
            ent_idx_map[entity] = (start, end)

        return ent_idx_map

        # For ALLEN-NER
        # words = self.ner.get_tagged_tokens(sentence)
        # entities, ent_idx_map = self.ner.get_entities(words)
        # return ent_idx_map




