import torch
import torch.nn as nn
import numpy as np

from torch import Tensor
from torch.nn.utils.rnn import pad_packed_sequence, pack_padded_sequence, PackedSequence
from .utils import *
from typing import Dict, Optional, Tuple

class CustomLSTM(torch.nn.Module):

    # TODO Highway Connections
    # TODO Variational Dropout
    # TODO PackedSequence/PaddedSequence
    # TODO Bidirectional

    def __init__(self, config: Dict):
        super().__init__()
        self.input_size = config["input_size"]
        self.hidden_size = config["hidden_size"]
        self.highway = config["highway"]
        self.dropout = config["dropout"] # Ignore this for now
        self.direction = config["direction"]

        # Optimize with singular matrix computation
        # In the case of Highway networks, 2 additional input gates and 1 additional state gate are required
        if self.highway:
            self.input_linearity = torch.nn.Linear(self.input_size, 6 * self.hidden_size)
            self.state_linearity = torch.nn.Linear(self.hidden_size, 5 * self.hidden_size, bias=True)
        else:
            self.input_linearity = torch.nn.Linear(self.input_size, 4 * self.hidden_size)
            self.state_linearity = torch.nn.Linear(self.hidden_size, 4 * self.hidden_size, bias=True)

        # Reinitialize
        self.input_linearity.reset_parameters()
        self.state_linearity.reset_parameters()


    def forward(self, inputs: PackedSequence,
                initial_states: Optional[Tuple[torch.Tensor]]=None) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        assert(isinstance(inputs, PackedSequence))
        print(inputs)


if __name__ == "__main__":

    batch_size = 50
    seq_length = 20
    feature_length = 200
    input_arr = np.random.rand(batch_size, seq_length, feature_length)
    input_tensor = Tensor(input_arr)

    sentence = "Linguistics is the best."
    words = ["Words", "best", "are", "great", "Linguistics"]
    vocab = Vocabulary(words)
    embedding_dimension = 10
    padding_idx = 0
    embedding = nn.Embedding(
        num_embeddings=vocab.vocab_len,
        embedding_dim=embedding_dimension,
        padding_idx=padding_idx
        )

    prec = Preprocessor()
    paired = prec.pair_sentence_pred(sentence)
    for pair in paired:
        print(prec.vectorize_sentence(pair, vocab))


