import re
import os
import numpy as np
import torch
import os

from torch.nn import Embedding

class Pretrained_Embeddings:

    def __init__(self, file_dir: str, file_name: str, num_dim: int):
        """ Loads word embeddings

        Args:
            file_dir: Word embedding file directory
            file_name: Word embedding file name
            num_dim: Number of dimensions of embedding
        """
        self.file_dir = file_dir
        self.file_name = file_name
        self.num_dim = num_dim # Addition of UNK
        self.word_index, self.embeddings, self.vocab_size = self.load_embeddings()


    def load_embeddings(self):
        """ Retrieve d_dimensional word GLOVE embeddings with n word vectors, with addition of UNK symbol,
        Instantiate mapping of word -> index -> embedding to facilitate one-hot encoding

        Returns:
            word_index (Dict<String, List<float>>): Dictionary mapping word to index within embeddings
            embeddings (List<List<float>>): Embeddings for each word index
            vocab_size (int): Size of vocabulary
        """
        word_index = {"UNK": 0}
        embeddings = []
        embeddings.append(np.zeros(shape=self.num_dim, dtype='float32'))

        f = open(os.path.abspath(os.path.join(self.file_dir, self.file_name)))
        for line in f:
            values = line.split()
            word = values[0]
            coeffs = np.asarray(values[1:], dtype='float32')
            word_index[word] = len(word_index)
            embeddings.append(coeffs)
        f.close()
        vocab_size = len(embeddings)
        print(vocab_size)

        return word_index, embeddings, vocab_size


    def get_word_index(self, word: str):
        """ Gets lowered word_index within word_index dictionary, assumes word in lower case

        Returns:
            index (int)
        """
        return self.word_index[word] if word in self.word_index else 0


    def get_word_embedding(self, word: str):
        """ Gets embedding of word, assuming lower case

        Returns:
            Embedding (List<float>)
        """
        word_index = self.get_word_index(word)
        return self.embeddings[word_index]


    def get_keras_embedding(self):
        """ Load keras embedding layer

        Returns:
            embedding: Keras embedding layer with embeddings loaded
        """
        embedding_layer = Embedding(
            num_embeddings=self.vocab_size,
            embedding_dim=self.num_dim
        )
        embedding_layer.load_state_dict({ 'weight': self.embeddings })
        embedding_layer.weight.requires_grad = False # Non-trainable
        return embedding_layer


def create_pretrained_embeddings(FILE_DIR, FILE_NAME):
    NUM_DIM = int(re.search("[0-9]+d", FILE_NAME).group()[:-1])
    return Pretrained_Embeddings(FILE_DIR, FILE_NAME, NUM_DIM)

if __name__ == "__main__":
    create_pretrained_embeddings("../glove.6B", "glove.6B.100d.txt")
