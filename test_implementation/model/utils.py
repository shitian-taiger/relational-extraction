import logging
import numpy as np
import spacy
from typing import Dict, List
from enum import Enum


class constants:
    PAD_INDEX = 0
    UNK_INDEX = 1
    PADDING = "<PAD>"
    UNKNOWN = "<UNK>"

class LSTM_Direction(Enum):
    forward = 0


class Vocabulary:

    def __init__(self, words: List):
        # Bidirectional mapping of words of indexes
        self.word_to_idx, self.idx_to_word = self.instantiate(words)
        self.vocab_len = len(self.idx_to_word)


    def instantiate(self, words: List):
        word_idx_map: Dict = {}
        idx_word_map: List = []

        # Add Padding and Unknown to vocabulary
        word_idx_map[constants.PADDING] = constants.PAD_INDEX
        idx_word_map.append(constants.PADDING)
        word_idx_map[constants.UNKNOWN] = constants.UNK_INDEX
        idx_word_map.append(constants.UNKNOWN)

        # Add words to vocab
        for i in range(len(words)):
            word = words[i]
            word_idx_map[word] = i + 2
            idx_word_map.append(word)

        return word_idx_map, idx_word_map


    def add_word(self, word: str):
        """
        Facilitates dynamic addition, for loading from file use load_from_file
        """
        if word in self.word_to_idx:
            logging.log(logging.WARN, "Word: [%s] already in vocab" % word)
        else:
            self.idx_to_word[self.vocab_len] = word
            self.word_to_idx[word] = self.vocab_len
            self.vocab_len = self.vocab_len + 1


    def load_from_file(self, file_dir: str):
        # TODO Implement
        return


    def get_word_from_index(self, index: int):
        assert(index < self.vocab_len)
        return self.idx_to_word[index]


    def get_index_from_word(self, word: str):
        assert(isinstance(word, str))
        return self.word_to_idx[word] if word in self.word_to_idx else \
            self.word_to_idx[constants.UNKNOWN]


class Preprocessor:

    def __init__(self):
        self.spacy_nlp = spacy.load("en_core_web_sm")


    def vectorize_sentence(self, sentence: str, vocab: Vocabulary) -> List[Dict]:
        """
        Indexes sentence with given vocab to produce sentence vector (np.array)
        Binarized vector indicating position of predicate (np.array)
        """

        paired = self._pair_sentence_pred(sentence)
        vectorized_instances: List[Dict] = []
        for sent_pred_pair in paired:
            tokens, pred_index = sent_pred_pair["tokens"], sent_pred_pair["pred_index"]
            sent_vec = []
            for token in tokens:
                sent_vec.append(vocab.get_index_from_word(token.text))

            pred_vec = [1 if i == pred_index else 0 for i in range(len((tokens)))]
            vectorized_instances.append({ "sent_vec": np.asarray(sent_vec), "pred_vec": np.asarray(pred_vec)})

        return vectorized_instances


    def pad_batch(self, batch_instances: List[Dict]):
        """
        Pads all sentences to the maximum length of the batch to facilitate padding packed sequence
        """
        batch_size = len(batch_instances)
        max_len = max([len(instance["sent_vec"]) for instance in batch_instances]) # Get max length of sequence

        # Instantiate numpy array of shape (batch size, max length) with all padding indexes
        padded_batch_sentences = np.full((batch_size, max_len), constants.PAD_INDEX)
        padded_batch_preds = np.full((batch_size, max_len), constants.PAD_INDEX)
        instance_lengths = [] # This is required for pack_padded_sequence

        for i, instance in enumerate(batch_instances): # Fill batch with actual values
            sent_vec, pred_vec = instance["sent_vec"], instance["pred_vec"]
            instance_len = len(sent_vec)
            padded_batch_sentences[i, 0:instance_len] = sent_vec[:]
            padded_batch_preds[i, 0:instance_len] = pred_vec[:]
            instance_lengths.append(instance_len)

        return padded_batch_sentences, padded_batch_preds, instance_lengths


    def _pair_sentence_pred(self, sentence: str) -> List[Dict]:
        """
        Tokenizes sentence, giving multiple instances of paired sentence with predicate index
        Returns: List[{ "tokens": <Spacy Tokens>, "pred_index": int }]
        """
        tokens = self._tokenize(sentence)
        predicate_indexes = [i for (i, t) in enumerate(tokens) if t.pos_ == "VERB"] # Get all indexes with predicates
        return [ {"tokens": tokens, "pred_index": idx } for idx in predicate_indexes ]


    def _tokenize(self, sentence: str):
        # Tokenize sentence to spacy Tokens including POS tags (pos_)
        return self.spacy_nlp(sentence)

