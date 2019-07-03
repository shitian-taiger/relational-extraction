import torch
from typing import Dict, List, Optional
from model.utils import *

class Decoder:
    """
    As implemented in ALLEN:
    Viterbi Decoding (HMM) of tags, disallowing stray I-tags without prior B-tags
    Purely used for prediction purposes, is not applicable to loss calculation and model training
    """

    def __init__(self, vocab: Vocabulary, labels: Labels):
        self.labels = labels
        self.vocab = vocab


    def decode(self, output_dict: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        all_predictions = output_dict['class_probabilities']
        sequence_lengths = self.get_lengths_from_binary_sequence_mask(output_dict["mask"]).data.tolist()

        if all_predictions.dim() == 3:
            predictions_list = [all_predictions[i].detach().cpu() for i in range(all_predictions.size(0))]
        else:
            predictions_list = [all_predictions]
        all_tags = []
        transition_matrix = self.get_viterbi_pairwise_potentials()
        for predictions, length in zip(predictions_list, sequence_lengths):
            max_likelihood_sequence, _ = self.viterbi_decode(predictions[:length], transition_matrix)
            tags = [self.labels.get_word_from_index(x) for x in max_likelihood_sequence]
            all_tags.append(tags)
        output_dict['tags'] = all_tags
        return output_dict


    def get_viterbi_pairwise_potentials(self):
        """
        Generate a matrix of pairwise transition potentials for the BIO labels.
        The only constraint implemented here is that I-XXX labels must be preceded
        by either an identical I-XXX tag or a B-XXX tag. In order to achieve this
        constraint, pairs of labels which do not satisfy this constraint have a
        pairwise potential of -inf.

        Returns
        -------
        transition_matrix : torch.Tensor
            A (num_labels, num_labels) matrix of pairwise potentials.
        """
        all_labels = self.labels.idx_to_tag
        num_labels = len(all_labels)
        transition_matrix = torch.zeros([num_labels, num_labels])

        for i, previous_label in all_labels.items():
            for j, label in all_labels.items():
                # I labels can only be preceded by themselves or
                # their corresponding B tag.
                if i != j and label[0] == 'I' and not previous_label == 'B' + label[1:]:
                    transition_matrix[i, j] = float("-inf")
        return transition_matrix

    def viterbi_decode(self, tag_sequence: torch.Tensor,
                    transition_matrix: torch.Tensor,
                    tag_observations: Optional[List[int]] = None):
        """
        Perform Viterbi decoding in log space over a sequence given a transition matrix
        specifying pairwise (transition) potentials between tags and a matrix of shape
        (sequence_length, num_tags) specifying unary potentials for possible tags per
        timestep.

        Parameters
        ----------
        tag_sequence : torch.Tensor, required.
            A tensor of shape (sequence_length, num_tags) representing scores for
            a set of tags over a given sequence.
        transition_matrix : torch.Tensor, required.
            A tensor of shape (num_tags, num_tags) representing the binary potentials
            for transitioning between a given pair of tags.
        tag_observations : Optional[List[int]], optional, (default = None)
            A list of length ``sequence_length`` containing the class ids of observed
            elements in the sequence, with unobserved elements being set to -1. Note that
            it is possible to provide evidence which results in degenerate labelings if
            the sequences of tags you provide as evidence cannot transition between each
            other, or those transitions are extremely unlikely. In this situation we log a
            warning, but the responsibility for providing self-consistent evidence ultimately
            lies with the user.

        Returns
        -------
        viterbi_path : List[int]
            The tag indices of the maximum likelihood tag sequence.
        viterbi_score : torch.Tensor
            The score of the viterbi path.
        """
        sequence_length, num_tags = list(tag_sequence.size())
        if tag_observations:
            if len(tag_observations) != sequence_length:
                raise ConfigurationError("Observations were provided, but they were not the same length "
                                        "as the sequence. Found sequence of length: {} and evidence: {}"
                                        .format(sequence_length, tag_observations))
        else:
            tag_observations = [-1 for _ in range(sequence_length)]

        path_scores = []
        path_indices = []

        if tag_observations[0] != -1:
            one_hot = torch.zeros(num_tags)
            one_hot[tag_observations[0]] = 100000.
            path_scores.append(one_hot)
        else:
            path_scores.append(tag_sequence[0, :])

        # Evaluate the scores for all possible paths.
        for timestep in range(1, sequence_length):
            # Add pairwise potentials to current scores.
            summed_potentials = path_scores[timestep - 1].unsqueeze(-1) + transition_matrix
            scores, paths = torch.max(summed_potentials, 0)

            # If we have an observation for this timestep, use it
            # instead of the distribution over tags.
            observation = tag_observations[timestep]
            # Warn the user if they have passed
            # invalid/extremely unlikely evidence.
            if tag_observations[timestep - 1] != -1:
                if transition_matrix[tag_observations[timestep - 1], observation] < -10000:
                    logger.warning("The pairwise potential between tags you have passed as "
                                "observations is extremely unlikely. Double check your evidence "
                                "or transition potentials!")
            if observation != -1:
                one_hot = torch.zeros(num_tags)
                one_hot[observation] = 100000.
                path_scores.append(one_hot)
            else:
                path_scores.append(tag_sequence[timestep, :] + scores.squeeze())
            path_indices.append(paths.squeeze())

        # Construct the most likely sequence backwards.
        viterbi_score, best_path = torch.max(path_scores[-1], 0)
        viterbi_path = [int(best_path.numpy())]
        for backward_timestep in reversed(path_indices):
            viterbi_path.append(int(backward_timestep[viterbi_path[-1]]))
        # Reverse the backward path.
        viterbi_path.reverse()
        return viterbi_path, viterbi_score

    def get_lengths_from_binary_sequence_mask(self, mask: torch.Tensor):
        """
        Compute sequence lengths for each batch element in a tensor using a
        binary mask.

        Parameters
        ----------
        mask : torch.Tensor, required.
            A 2D binary mask of shape (batch_size, sequence_length) to
            calculate the per-batch sequence lengths from.

        Returns
        -------
        A torch.LongTensor of shape (batch_size,) representing the lengths
        of the sequences in the batch.
        """
        return mask.long().sum(-1)


