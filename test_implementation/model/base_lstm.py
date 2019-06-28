import torch
import numpy as np
from torch import Tensor
from torch.nn import Module, Parameter

from typing import Dict, Optional, Tuple


config = {
    "input_size": 200,
    "hidden_size": 300
}

class LSTM(torch.nn.Module):

    def __init__(self, config: Dict):

        super().__init__()
        self.input_size = config["input_size"]
        self.hidden_size = config["hidden_size"]
        self.weight_ih = Parameter(Tensor(self.input_size, self.hidden_size * 4))
        self.weight_hh = Parameter(Tensor(self.hidden_size, self.hidden_size * 4))
        self.bias = Parameter(Tensor(self.hidden_size * 4))
        self.initialize_weights()


    def initialize_weights(self):
        for parameter in self.parameters():
            if parameter.data.ndimension() >= 2:
                torch.nn.init.xavier_uniform_(parameter.data) # Initialization of weights
            else:
                torch.nn.init.zeros_(parameter.data) # Initialization of bias


    def initialize_states(self) -> Tuple[Tensor]:
        return [torch.zeros(self.hidden_size), torch.zeros(self.hidden_size)]


    def forward(self, x: torch.Tensor, initial_states: Optional[Tuple[torch.Tensor]]=None) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        ''' Forward instance

        Arguments:
            x : Assumes input of format (batch-size, sequence-length, feature-dimensions)
            initial_states : Optional initial cell and hidden states

        Returns:
            hidden_sequence : Output of hidden states at every time-step
            (h_t, c_t) : Hidden and Cell states at last time-step (Imitate pytorch output format)
        '''

        batch_size, sequence_size, _ = x.size()

        if initial_states is None:
            h_t, c_t = self.initialize_states()
        else:
            h_t, c_t = initial_states

        # Sequence computation
        hidden_sequence = Tensor([])
        for t in range(sequence_size):
            x_t = x[:, t, :]
            # Optimize singular matrix computation
            gates = x_t @ self.weight_ih + h_t @ self.weight_hh + self.bias
            i_t, f_t, g_t, o_t = (
                torch.sigmoid(gates[:,                      : self.hidden_size    ]),
                torch.sigmoid(gates[:, self.hidden_size     : self.hidden_size * 2]),
                torch.tanh(   gates[:, self.hidden_size * 2 : self.hidden_size * 3]),
                torch.sigmoid(gates[:, self.hidden_size * 3 :                     ]),
            )
            c_t = f_t * c_t + i_t * g_t
            h_t = o_t * torch.tanh(c_t)
            # h_t represents batch output for time_step [batch_size, output_size]
            # unsqueeze -> [1, batch_size, output_size]
            hidden_sequence = torch.cat([hidden_sequence, h_t.unsqueeze(0)], 0)

        # [seq_len, batch_size, output_size] -> [batch_size, seq_len, output_size]
        hidden_sequence.transpose_(0, 1)

        return hidden_sequence, (h_t, c_t)


optimized = LSTM(config)
batch_size = 50
seq_length = 20
feature_length = 200

input_arr = np.random.rand(batch_size, seq_length, feature_length)
input_tensor = Tensor(input_arr)
hidden_sequence, (ht, ct) = optimized.forward(input_tensor)
