import re
import torch
from torch.nn.utils.rnn import pack_padded_sequence
from pathlib import Path
from typing import Tuple, Dict, List
from model.decoder import Decoder
from model.model import REModel
from model.utils import *
from data_utils import parse_generated_instances

class Trainer:

    def __init__(self, model_config: Dict, training_config=None):
        """
        Arguments:
            model_config : Configuration of model to be trained:
                -- input_size: LSTM input
                -- hidden_size: LSTM hidden state
                -- highway: Highway connections in LSTM
                -- layers: Number of LSTM layers
                -- custom_weights: File path to weights
                -- custom_vocab: File path to vocabulary and labels
                -- custom_embedding: File path to embedding
                -- embedding_dim: Dimension of word embedding
                -- num_classes: Corresponds to types of output IOB2 tags

            training_config: Training Configurations including batch_size etc
        """

        self.vocab = Vocabulary(model_config["tokens_dir"])
        model_config["num_tokens"] = self.vocab.vocab_len
        self.labels = Labels(model_config["labels_dir"])
        model_config["num_classes"] = self.labels.labels_len
        self.pos = POS(model_config["pos_dir"])
        model_config["num_pos"] = self.pos.pos_len
        self.preprocessor = Preprocessor(self.vocab, self.labels, self.pos)

        self.model = REModel(model_config)
        self.decoder = Decoder(self.vocab, self.labels)

        if training_config:
            self.training_config: Dict = training_config
            self.optimizer = torch.optim.Adam(self.model.parameters())


    def train(self):
        self.model.train = True

        if not self.training_config:
            raise("No training configuration given")

        epochs = self.training_config["epochs"]
        batch_size = self.training_config["batch_size"]

        for i in range(epochs):
            if i % 10 == 0: # Save trained model
                print("Saving for epoch {}".format(i))
                torch.save(self.model.state_dict(), Path.joinpath(self.training_config["save_path"], "model_epoch{}".format(i)))

            batch_tokens, batch_tags, batch_pos = [], [], []
            for tokens, tags, pos in parse_generated_instances(self.training_config["traindata_file"]):
                if len(batch_tokens) == batch_size and len(batch_tags) == batch_size:
                    self.optimizer.zero_grad() # Clear optimizer gradients

                    model_input = self.preprocess_batch(batch_tokens, batch_tags, batch_pos)
                    output = self.model(model_input)

                    output_tags = self.decoder.decode(output)["tags"]
                    loss = output["loss"]
                    loss.backward()
                    self.optimizer.step()

                    print("Batch loss: {}".format(loss))

                    batch_tokens, batch_tags, batch_pos = [], [], []
                batch_tokens.append(tokens)
                batch_tags.append(tags)
                batch_pos.append(pos)


    def predict(self, sentence: str):
        """
        Prediction for sentence, not applicable for training
        """
        self.model.train = False
        self.model.load_state_dict(torch.load('./saved/model_epoch90'))
        vectorized_sentence = self.preprocessor.vectorize_sentence(sentence)
        model_input = self.preprocess_batch_tagless(vectorized_sentence)
        output = self.model(model_input)
        output_tags = self.decoder.decode(output)["tags"]
        # Tuples of token indexes
        rel_tuples: List[Tuple] = self._parse_tags({
            "tokens": self.preprocessor.tokenize(sentence), # For getting tokens with UNK tag
            "tags_list": output_tags, # Mutiple tag ouputs possible per sentence
            "vectorized_instances": vectorized_sentence
            })
        return rel_tuples


    def _parse_tags(self, output_dict: Dict):
        tokens, tags_list, vectorized_instances = output_dict["tokens"], output_dict["tags_list"], output_dict["vectorized_instances"]
        assert(len(tags_list) == len(vectorized_instances))

        tuples: List[Tuple] = []
        for n, vectorized_instance in enumerate(vectorized_instances):
            ent1, rels, ent2 = "", [], ""
            ent_vector = vectorized_instance['ent_vec']
            tags = tags_list[n]
            rel = ""
            for i, token in enumerate(tokens):
                if ent_vector[i] == 1:
                    ent1 = " ".join([ent1, token.text]) if ent1 else token.text
                elif ent_vector[i] == 2:
                    ent2 = " ".join([ent2, token.text]) if ent2 else token.text
                else:
                    tag = tags[i]
                    if re.search("B-", tag):
                        if not rel == "":
                            rels.append(rel)
                        rel = token.text
                    elif re.search("I-", tag):
                        rel = " ".join([rel, token.text])
                    else: # O tag
                        if not rel == "":
                            rels.append(rel)
                        rel = ""
            tuples.append((ent1, rels, ent2))
        return(tuples)


    def _parse_tags_OIE(self, output_dict: Dict):
        """
        TODO (Deprecate) Parsing for OIE output
        Given a vectorized sentence (vocabulary word indexes) and output tags for the sentence,
        generate tuples of relations
        Arguments:
            Dictionary containing "sent_vec": `sentence vector` and "tags_list": `list of tags`
            Note that tags is a nested list since multiple predicates can be present in the sentence
        Returns:
            tuples: List of < arg, rel, arg > tuples
        """
        tags_list, sentence_vector = output_dict["tags_list"], output_dict["sent_vec"]
        # Double check token and tag lengths
        for tags in tags_list:
            assert(len(tags) == len(sentence_vector))

        tuples: List[Tuple] = []
        for tags in tags_list:
            tags_iter = iter(tags)
            # We store the word_index together with array index for retrieval of the original word in
            # the case of UNK tags
            pre_rel_args, rel, post_rel_args = [], [], []
            rel_found = False
            curr_index = 0
            for tag in tags_iter:
                # Beginning of Verb or verbial modifier, append all tags till we hit `B-V`
                if tag == "B-V" or tag == "B-BV":
                    rel.append((sentence_vector[curr_index], curr_index))
                    curr_index += 1 if (curr_index < len(tags) - 1) else 0
                    next_tag = tags[curr_index]
                    while (not tag == "B-V" and not next_tag == "B-V") and curr_index < (len(tags) - 1):
                        next(tags_iter)
                        rel.append((sentence_vector[curr_index], curr_index))
                        curr_index = curr_index + 1 if curr_index < len(tags) else curr_index
                        next_tag = tags[curr_index]
                    rel_found = True
                # Beginning of ARG, append until next tag is not an I-tag
                elif re.search("B-", tag):
                    arg: List = [(sentence_vector[curr_index], curr_index)]
                    curr_index += 1 if (curr_index < len(tags) - 1) else 0
                    next_tag = tags[curr_index]
                    while re.search("I-", next_tag) and curr_index < (len(tags) - 1):
                        next(tags_iter)
                        arg.append((sentence_vector[curr_index], curr_index))
                        curr_index += 1
                        next_tag = tags[curr_index]
                    if rel_found:
                        post_rel_args.append(arg)
                    else:
                        pre_rel_args.append(arg)
                else:
                    curr_index += 1

            # Translate all tupled word indexes phrases
            for pre_arg in pre_rel_args:
                for post_arg in post_rel_args:
                    tuples.append((self._get_phrase(pre_arg, output_dict["tokens"]),
                                   self._get_phrase(rel, output_dict["tokens"]),
                                   self._get_phrase(post_arg, output_dict["tokens"])))
        return tuples


    def _get_phrase(self, token_indexes: List, sentence_tokens: List):
        # Given list of token indexes, map indexes to dictionary and join them according to punctuation
        phrase = ""
        hyphen = False
        for token_index, arr_index in token_indexes:
            word = self.vocab.idx_to_word[token_index] if token_index > 1 else sentence_tokens[arr_index].text
            if re.search("'", word) or re.search(",", word):
                phrase = "".join([phrase, word])
            elif re.search("-", word):
                phrase = "".join([phrase, word])
            elif hyphen:
                phrase = "".join([phrase, word])
                hyphen = False
            else:
                phrase = " ".join([phrase, word]) if phrase else word
        return phrase


    def preprocess_batch_tagless(self, instances_dict):
        """
        Preprocessing for sentences, purely for prediction purposes, tags not required
        Arguments:
            batch_instances: List of output of vectorize_token_tags -
                             (Dict of token_vector, entity_vector, pos_vector, tags_vector [Optional])
        Returns:
            Dictionary of sentence vector (token indexes), entity vector,
            sequence_lengths and sequence mask and tags vector (tag indexes)
        """
        sents_vec, ents_vec, pos_vec, lens_vec, mask = self.preprocessor.pad_batch(instances_dict)
        return { "sent_vec": sents_vec.long(), "ent_vec": ents_vec.long(), "pos_vec": pos_vec.long(),
                 "lengths": lens_vec, "mask": mask }


    def preprocess_batch(self, tokens_list: List[List], tags_list: List[List], pos_list: List[List]):
        """
        Preprocessing for tokens and tags for training
        Arguments:
            tokens_list: List of (List of string words)
            tags_list: List of (List of string tags)
            pos_list: List of (List of string word POS)
        Returns:
            Dictionary of sentence vector (token indexes), entity vector,
            sequence_lengths and sequence mask and tags vector (tag indexes)
        """
        assert(len(tokens_list) == len(tags_list))
        vectorized_list: List[Dict] = []
        for i, tokens in enumerate(tokens_list):
            tags = tags_list[i]
            pos = pos_list[i]
            vectorized: List[Dict] = self.preprocessor.vectorize_token_tags(tokens, tags, pos)
            vectorized_list += vectorized
        sents_vec, ents_vec, pos_vec, lens_vec, mask, tags_vec = self.preprocessor.pad_batch(vectorized_list)
        return { "sent_vec": sents_vec.long(), "ent_vec": ents_vec.long(), "pos_vec": pos_vec.long(),
                "lengths": lens_vec, "mask": mask, "tags_vec": tags_vec.long() }

