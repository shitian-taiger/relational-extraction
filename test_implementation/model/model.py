import torch
from torch import Tensor
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
from pathlib import Path
from .utils import *
from .h_d_lstm import CustomLSTM


class REModel(torch.nn.Module):

    def __init__(self, config):
        super().__init__()
        self.config = config
        self._load_embeddings(config["num_embeddings"], config["embedding_dim"])
        self.bdlstm = self._instantiate_bdlstm()


    def _load_embeddings(self, num_embeddings, embedding_dim):
        cwd = Path().resolve()
        token_emb_weights = torch.load(Path.joinpath(cwd, "weights/token_embedder"))
        verb_emb_weights = torch.load(Path.joinpath(cwd, "weights/verb_embedder"))
        self.token_embedding = torch.nn.Embedding(num_embeddings, embedding_dim,
                                            constants.PAD_INDEX, _weight=token_emb_weights)
        self.verb_embedding = torch.nn.Embedding(2, embedding_dim, _weight=verb_emb_weights)


    def _instantiate_bdlstm(self):
        input_size = self.config["input_size"]
        hidden_size = self.config["hidden_size"]
        layers = self.config["layers"]
        self.lstm_layers = []

        for layer_index in range(layers):
            direction = LSTM_Direction.forward if layer_index % 2 == 0 else LSTM_Direction.backward
            self.config["direction"] = direction
            layer = CustomLSTM(self.config) # Pass configuration to LSTM
            self._load_layer_weights(layer, layer_index) # Load in custom weights for layers
            self.lstm_layers.append(layer)
            self.config["input_size"] = hidden_size # Change input size of layers 2 - 8


    def _load_layer_weights(self, layer: CustomLSTM, layer_num: int):
        cwd = Path().resolve()
        input_weights: Tensor = torch.load(Path.joinpath(cwd, "weights/layer{}_input_weight".format(layer_num)))
        input_bias: Tensor = torch.load(Path.joinpath(cwd, "weights/layer{}_input_bias".format(layer_num)))
        state_weights: Tensor = torch.load(Path.joinpath(cwd, "weights/layer{}_state_weight".format(layer_num)))
        state_bias: Tensor = torch.load(Path.joinpath(cwd, "weights/layer{}_state_bias".format(layer_num)))
        layer.load_weights(input_weights,
                           input_bias,
                           state_weights,
                           state_bias)

    def sort_and_pack_embeddings(self, full_embeddings: Tensor, lengths: List):
        """
        Sorts instances of sentences, predicates based on length (Longest --> Shortest)
        Returns a packed sequence (batch first)
        """
        zipped_embeddings_lengths = zip(full_embeddings, lengths)
        sorted_embeddings_lengths = sorted(zipped_embeddings_lengths, key=lambda x: x[1], reverse=True)
        sorted_embeddings, sorted_lengths = [list(t) for t in zip(*sorted_embeddings_lengths)]
        sorted_embeddings = torch.stack(sorted_embeddings)
        return pack_padded_sequence(sorted_embeddings, sorted_lengths, batch_first=True)


    def forward(self, input_dict: Dict):
        """
        Takes as input dictionary of { "sent_vec": Tensor, "pred_vec": Tensor }
        Concatenates the embedded sentence and its corresponding verb
        """
        sent_vec, pred_vec = input_dict["sent_vec"], input_dict["pred_vec"]
        embedded_sentences = self.token_embedding(sent_vec)
        embedded_verbs = self.verb_embedding(pred_vec)
        full_embeddings = torch.cat([embedded_sentences, embedded_verbs], dim=-1)

        # Sort and pack padded sequence
        packed = self.sort_and_pack_embeddings(full_embeddings, input_dict["lengths"])

        # TODO Why do we need to store final states (For training?)
        final_states = []

        hidden_states = [None] * len(self.lstm_layers)
        output_sequence: PackedSequence = packed
        for i, state in enumerate(hidden_states):
            layer = self.lstm_layers[i]
            output_sequence, final_state = layer(output_sequence, state)
            final_states.append(final_state)

        # TODO Why do we need to store final states
        final_hidden_state, final_cell_state = tuple(torch.cat(state_list, 0) for state_list in zip(*final_states))

         = pad_packed_sequence(output_sequence, batch_first=True)
        # return output_sequence, (final_hidden_state, final_cell_state)



