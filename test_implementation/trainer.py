import torch
from torch.nn.utils.rnn import pack_padded_sequence

from model.decoder import Decoder
from model.model import REModel
from model.utils import *

from data_utils import get_tokens_oie

class Trainer:

    def __init__(self, model_config: Dict, training_config=None):

        self.vocab = Vocabulary()
        self.vocab.load_from_dir()
        model_config["num_embeddings"] = self.vocab.vocab_len
        self.labels = Labels()
        self.model = REModel(model_config)
        self.preprocessor = Preprocessor(self.vocab, self.labels)
        self.decoder = Decoder(self.vocab, self.labels)

        if training_config:
            self.training_config = training_config
            self.optimizer = torch.optim.Adam(self.model.parameters())
            self.model.train = True


    def train(self):

        if not self.training_config:
            raise("No training configuration given")

        epochs = self.training_config["epochs"]
        batch_size = self.training_config["batch_size"]

        p = Path(__file__).parent.resolve()
        file_dir = Path.joinpath(p.parent, "data/OIE/train.oie.conll")
        for i in range(epochs):
            i, batch_tokens, batch_tags = 0, [], []
            for tokens, tags in get_tokens_oie(file_dir):
                i += 1
                if i == batch_size and batch_tokens and batch_tags:
                    self.optimizer.zero_grad() # Clear optimizer gradients

                    model_input = self.preprocess_batch(batch_tokens, batch_tags)
                    output = self.model(model_input)
                    loss = output["loss"]
                    loss.backward()
                    self.optimizer.step()

                    print("Batch loss: {}".format(loss))
                    i, batch_tokens, batch_tags = 0, [], []

                if tokens and tags: # Omit cases where there are empty sentences
                    batch_tokens.append(tokens)
                    batch_tags.append(tags)


    def preprocess_batch_tagless(self, tokens_list: List[List]):
        # Vectorize pairs to: {'sent_vec': [index of word in vocab], 'pred_vec': [binarized]}
        vectorized_pairs: List[Dict] = []
        for i, sentence in enumerate(sentences):
            vectorized_pair = self.preprocessor.vectorize_sentence(sentence)
            vectorized_pairs += vectorized_pair
        sents, preds, lens, mask = self.preprocessor.pad_batch(vectorized_pairs)
        return { "sent_vec": sents.long(), "pred_vec": preds.long(), "lengths": lens, "mask": mask }


    def preprocess_batch(self, tokens_list: List[List], tags_list: List[List]):
        # Vectorize pairs to: {'sent_vec': [index of word in vocab], 'pred_vec': [binarized]}
        vectorized_list: List[Dict] = []
        for i, tokens in enumerate(tokens_list):
            tags = tags_list[i]
            vectorized: List[Dict] = self.preprocessor.vectorize_tokens(tokens, tags)
            vectorized_list += vectorized
        sents, preds, lens, mask, tags = self.preprocessor.pad_batch(vectorized_list)
        return { "sent_vec": sents.long(), "pred_vec": preds.long(),
                "lengths": lens, "mask": mask, "tags_vec": tags }

