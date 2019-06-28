import torch
from torch.nn.utils.rnn import pack_padded_sequence

from model.utils import *
from model.h_d_lstm import CustomLSTM



if __name__ == "__main__":

    config = {
        "input_size": 200,
        "hidden_size": 300,
        "highway": True,
        "dropout": 0.2,
        "direction": LSTM_Direction.forward
    }
    custom = CustomLSTM(config)

    sentences = [
        "Words are great because of Linguistics",
        "Linguistics is the best."
        ]
    words = ["Words", "best", "are", "great", "Linguistics"]
    vocab = Vocabulary(words)

    prec = Preprocessor()
    vectorized_pairs: List[Dict] = []
    for sentence in sentences:
        vectorized_pairs += prec.vectorize_sentence(sentence, vocab)

    sents, preds, lens = prec.pad_batch(vectorized_pairs)
    sents = torch.Tensor(sents)
    preds = torch.Tensor(preds)
    lens = torch.Tensor(lens)

    packed = pack_padded_sequence(sents, lens, batch_first=True)
    print(type(packed))
    # custom.forward(paired[0])


