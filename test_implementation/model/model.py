import torch
from torch import Tensor
from torch.nn.utils.rnn import PackedSequence, pack_padded_sequence, pad_packed_sequence
from pathlib import Path
from .utils import *
from .h_d_lstm import CustomLSTM


class REModel(torch.nn.Module):

    def __init__(self, config):
        super().__init__()
        self.config = config
        self._load_embeddings(config["num_embeddings"], config["embedding_dim"])
        self.bdlstm = self._instantiate_bdlstm()
        self._load_tag_layer()
        self.train = False # Turn this on for training


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


    def _load_tag_layer(self):
        cwd = Path().resolve()
        tag_layer_weights: Tensor = torch.load(Path.joinpath(cwd, "weights/tag_layer_weights"))
        tag_layer_bias: Tensor = torch.load(Path.joinpath(cwd, "weights/tag_layer_bias"))
        self.tag_layer = torch.nn.Linear(self.config["hidden_size"], self.config["num_classes"])
        self.tag_layer.weight = tag_layer_weights
        self.tag_layer.bias = tag_layer_bias


    def sort_and_pack_embeddings(self, full_embeddings: Tensor, lengths: List):
        """
        Sorts instances of sentences, predicates based on length (Longest --> Shortest)
        Returns:
            Packed sequence (batch first)
            Indices to restore the original order of the sequences
        """

        assert(len(full_embeddings) == len(lengths))

        # Zip list of numbering indices for restoration purposes
        zipped_embeddings_lengths = zip(full_embeddings, lengths, range(len(lengths)))
        sorted_embeddings_lengths = sorted(zipped_embeddings_lengths, key=lambda x: x[1], reverse=True)
        sorted_embeddings, sorted_lengths, original_order = [list(t) for t in zip(*sorted_embeddings_lengths)]
        sorted_embeddings = torch.stack(sorted_embeddings)
        return pack_padded_sequence(sorted_embeddings, sorted_lengths, batch_first=True), original_order


    def unpack_and_reorder(self, packed_output: PackedSequence, original_order: List[int]):
        """
        Unpacks packed sequence and reorders according to original index
        """
        unpacked = pad_packed_sequence(packed_output, batch_first=True)
        unpacked_tensors = unpacked[0]
        zipped_tensors = zip(unpacked_tensors, original_order)
        sorted_zipped_tensors = sorted(zipped_tensors, key=lambda x: x[1])
        sorted_tensors, _ = [list(t) for t in zip(*sorted_zipped_tensors)]
        return torch.stack(sorted_tensors)


    def get_output_dict(self, output_tensors: Tensor, mask: Tensor):
        """
        For each time step of the output, apply tag_layer to obtain logits for tag classification
            - `TimeDistributed` class not available in Pytorch, imitate functionality
        Softmax for retrieval of class probabilities
        """
        batch_size, time_steps, output_dim = output_tensors.shape
        output_tensor_flattened = output_tensors.view(batch_size * time_steps, output_dim)
        logits_flattened = self.tag_layer(output_tensor_flattened)
        logits = logits_flattened.view(batch_size, time_steps, self.config["num_classes"])

        # Get class probabilities directly
        class_probs_flattened = torch.nn.functional.softmax(logits_flattened, dim=-1)
        class_probs = class_probs_flattened.view([batch_size, time_steps, self.config["num_classes"]])

        return { "logits": logits, "class_probabilities": class_probs, "mask": mask }


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
        packed, original_order = self.sort_and_pack_embeddings(full_embeddings, input_dict["lengths"])

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

        output_tensors = self.unpack_and_reorder(output_sequence, original_order)
        output_dict = self.get_output_dict(output_tensors, input_dict["mask"]) # Class probabilities to be decoded

        if self.train:
            self.compute_loss(output_dict["logits"], input_dict["tags_vec"], input_dict["mask"])

        return output_dict


    def compute_loss(self, logits: Tensor, tags: Tensor, mask: Tensor):
        """
        Custom loss computation
        """
        # shape : (batch * sequence_length, num_classes)
        logits_flat = logits.view(-1, logits.size(-1))
        # shape : (batch * sequence_length, num_classes)
        log_probs_flat = torch.nn.functional.log_softmax(logits_flat, dim=-1)
        # shape : (batch * max_len, 1)
        tags_flat = tags.view(-1, 1).long()

        negative_log_likelihood_flat = - torch.gather(log_probs_flat, dim=1, index=tags_flat)
        negative_log_likelihood = negative_log_likelihood_flat.view(*tags.size())
        negative_log_likelihood = negative_log_likelihood * mask.float()

        # shape : (batch_size,)
        per_batch_loss = negative_log_likelihood.sum(1) / (mask.sum(1).float() + 1e-13)
        num_non_empty_sequences = ((mask.sum(1) > 0).float().sum() + 1e-13)
        loss = per_batch_loss.sum() / num_non_empty_sequences
        print(loss)

