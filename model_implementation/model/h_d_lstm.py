import torch
import torch.nn as nn
import numpy as np

from torch import Tensor
from torch.nn.utils.rnn import pad_packed_sequence, pack_padded_sequence, PackedSequence
from .utils import *
from typing import Dict, Optional, Tuple

class CustomLSTM(torch.nn.Module):

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


    def load_weights(self, input_weights, input_bias, state_weights, state_bias):
        self.input_linearity.weight = input_weights
        self.input_linearity.bias = input_bias
        self.state_linearity.weight = state_weights
        self.state_linearity.bias = state_bias


    def forward(self, inputs: PackedSequence, initial_state: Optional[Tuple[torch.Tensor, torch.Tensor]] = None):

        sequence_tensor, batch_lengths = pad_packed_sequence(inputs, batch_first=True)

        batch_size = sequence_tensor.size()[0]
        total_timesteps = sequence_tensor.size()[1]

        # For the accumulation time-step outputs to pass to the next layer
        output_accumulator = sequence_tensor.new_zeros(batch_size, total_timesteps, self.hidden_size)

        # Considering variable length inputs, we can omit calculations for when, at the current
        # time-step, the sequence at `timestep_end_index` has already exhausted all time-steps
        # Note that the sequence is sorted in decreasing order, hence:
        # For the forward direction, this index starts at the end since we consider all sequences
        # at timestep = 0
        # For the backward direction, we increase the number of sequences to consider as we progress
        # backward
        timestep_end_index = batch_size - 1 if self.direction == LSTM_Direction.forward else 0

        # The naming of our hidden states is to accommodate the above optimization, since not all
        # hidden states in the batch are required at every time-step
        # We assume no input initial states (Zero initialization)
        complete_batch_previous_memory = sequence_tensor.new_zeros(batch_size, self.hidden_size)
        complete_batch_previous_state = sequence_tensor.new_zeros(batch_size, self.hidden_size)

        timesteps = range(total_timesteps) if self.direction == LSTM_Direction.forward else \
            reversed(range(total_timesteps)) # Reverse timestep indexing for backward direction

        for timestep in timesteps:

            # (FORWARD) Omit if the shorter sequences have been exhausted
            if self.direction == LSTM_Direction.forward:
                while batch_lengths[timestep_end_index] <= timestep:
                    timestep_end_index -= 1
            # (BACKWARD) Check if we are already at the maximal index, otherwise include sequences
            # which need to be included as timestep index decreases
            else:
                while timestep_end_index < (len(batch_lengths) - 1) and \
                                batch_lengths[timestep_end_index + 1] > timestep:
                    timestep_end_index += 1
            # print("Timestep End Index: {}".format(timestep_end_index))

            # Get the hidden states for those sequences that require computation
            previous_memory = complete_batch_previous_memory[0: timestep_end_index + 1].clone()
            previous_state = complete_batch_previous_state[0: timestep_end_index + 1].clone()

            # Calculations
            timestep_input = sequence_tensor[0: timestep_end_index + 1, timestep]

            projected_input = self.input_linearity(timestep_input)
            projected_state = self.state_linearity(previous_state)

            # Main LSTM equations using relevant chunks of the big linear
            # projections of the hidden state and inputs.
            input_gate = torch.sigmoid(projected_input[:, 0 * self.hidden_size:1 * self.hidden_size] +
                                       projected_state[:, 0 * self.hidden_size:1 * self.hidden_size])
            forget_gate = torch.sigmoid(projected_input[:, 1 * self.hidden_size:2 * self.hidden_size] +
                                        projected_state[:, 1 * self.hidden_size:2 * self.hidden_size])
            memory_init = torch.tanh(projected_input[:, 2 * self.hidden_size:3 * self.hidden_size] +
                                     projected_state[:, 2 * self.hidden_size:3 * self.hidden_size])
            output_gate = torch.sigmoid(projected_input[:, 3 * self.hidden_size:4 * self.hidden_size] +
                                        projected_state[:, 3 * self.hidden_size:4 * self.hidden_size])
            memory = input_gate * memory_init + forget_gate * previous_memory
            timestep_output = output_gate * torch.tanh(memory)

            if self.highway:
                highway_gate = torch.sigmoid(projected_input[:, 4 * self.hidden_size:5 * self.hidden_size] +
                                             projected_state[:, 4 * self.hidden_size:5 * self.hidden_size])
                highway_input_projection = projected_input[:, 5 * self.hidden_size:6 * self.hidden_size]
                timestep_output = highway_gate * timestep_output + (1 - highway_gate) * highway_input_projection

            # We retain the batch dimensions by including the new computed hidden states to the
            # previously calculated hidden states
            complete_batch_previous_memory = complete_batch_previous_memory.clone()
            complete_batch_previous_state = complete_batch_previous_state.clone()
            complete_batch_previous_memory[0:timestep_end_index + 1] = memory
            complete_batch_previous_state[0:timestep_end_index + 1] = timestep_output
            output_accumulator[0:timestep_end_index + 1, timestep] = timestep_output

        output_accumulator = pack_padded_sequence(output_accumulator, batch_lengths, batch_first=True)

        # Mimic the pytorch API by returning state in the following shape:
        # (num_layers * num_directions, batch_size, hidden_size). As this
        # LSTM cannot be stacked, the first dimension here is just 1.
        final_state = (complete_batch_previous_state.unsqueeze(0),
                       complete_batch_previous_memory.unsqueeze(0))

        return output_accumulator, final_state














