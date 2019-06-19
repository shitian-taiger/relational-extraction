import torch
import numpy as np
from torch import Tensor
from torch.nn import Parameter
from utils import Input_Dim, LSTM_Direction

from typing import Dict, Optional, Tuple

config = {
    "input_size": 200,
    "hidden_size": 300,
    "highway": True,
    "dropout": 0.2,
    "direction": LSTM_Direction.forward

}

class CustomLSTM(torch.nn.Module):

    def __init__(self, config: Dict):

        super(HDLstm).__init__()
        self.input_size = config["input_size"]
        self.hidden_size = config["hidden_size"]
        self.highway = config["highway"]
        self.dropout = config["dropout"]
        self.direction = config["direction"]

        self.weight_ih = Parameter(Tensor(self.input_size, self.hidden_size * 4))
        self.weight_hh = Parameter(Tensor(self.hidden_size, self.hidden_size * 4))
        self.bias = Parameter(Tensor(self.hidden_size * 4))
        self.initialize_weights()


    def forward():
        # TODO Highway Connections
        # TODO Variational Dropout
        # TODO PackedSequence/PaddedSequence
        # TODO Bidirectional
