import torch
from torch.nn.utils.rnn import pack_padded_sequence

from model.model import REModel
from model.utils import *
from model.h_d_lstm import CustomLSTM
from model.decoder import Decoder

config = {
    "input_size": 200,
    "hidden_size": 300,
    "highway": True,
    "dropout": 0.2,
    "direction": LSTM_Direction.forward,
    "embedding_dim": 100,
    "layers": 8,
    "num_classes": 62
}

def preprocess_batch_tagless(tokens_list: List[List], prec: Preprocessor):
    # Vectorize pairs to: {'sent_vec': [index of word in vocab], 'pred_vec': [binarized]}
    vectorized_pairs: List[Dict] = []
    for i, sentence in enumerate(sentences):
        vectorized_pair = prec.vectorize_sentence(sentence)
        vectorized_pairs += vectorized_pair
    sents, preds, lens, mask = prec.pad_batch(vectorized_pairs)
    return { "sent_vec": sents.long(), "pred_vec": preds.long(), "lengths": lens, "mask": mask }


def preprocess_batch(tokens_list: List[List], tags_list: List[List], prec: Preprocessor):
    # Vectorize pairs to: {'sent_vec': [index of word in vocab], 'pred_vec': [binarized]}
    vectorized_list: List[Dict] = []
    for i, tokens in enumerate(tokens_list):
        tags = tags_list[i]
        vectorized: List[Dict] = prec.vectorize_tokens(tokens, tags)
        vectorized_list += vectorized
    sents, preds, lens, mask, tags = prec.pad_batch(vectorized_list)
    return { "sent_vec": sents.long(), "pred_vec": preds.long(),
             "lengths": lens, "mask": mask, "tags": tags }


if __name__ == "__main__":

    sentences = [
        "Harry is a random dude.",
        "Linguistics is extremely interesting while being highly relevant.",
        ]

    vocab = Vocabulary()
    vocab.load_from_dir()
    config["num_embeddings"] = vocab.vocab_len


    prec = Preprocessor()
    vectorized_pairs: List[Dict] = []
    """
    Vectorize pairs to: {'sent_vec': [index of word in vocab], 'pred_vec': [binarized]}
    """
    for sentence in sentences:
        vectorized_pairs += prec.vectorize_sentence(sentence, vocab)

    sents, preds, lens, mask = prec.pad_batch(vectorized_pairs)

    model_input = { "sent_vec": sents.long(), "pred_vec": preds.long(),
                    "lengths": lens, "mask": mask }

    re_model = REModel(config)
    output = re_model(model_input)

    decoder = Decoder(vocab)
    output_tags = decoder.decode(output)
    print(output_tags['tags'])

