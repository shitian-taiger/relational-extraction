import torch
from .utils import *


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


    def forward(self, input: Dict):
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
        """
        Takes as input dictionary of { "sent_vec": Tensor, "pred_vec": Tensor }
        """


