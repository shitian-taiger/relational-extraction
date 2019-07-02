import torch
from torch.nn.utils.rnn import pack_padded_sequence

from model.decoder import Decoder
from model.model import REModel
from model.utils import *

from data_utils import get_tokens_oie

config = {
    "input_size": 200,
    "hidden_size": 300,
    "highway": True,
    "dropout": 0.2,
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
             "lengths": lens, "mask": mask, "tags_vec": tags }

if __name__ == "__main__":

    sentences = [
        "Harry is a random dude.",
        # "Linguistics is extremely interesting while being highly relevant.",
        # "These reports were later denied by a high Brazilian official, who said Brazil wasn't involved in any coffee discussions on quotas, the analyst said.",
        ]

    tokens = [
        [ "Harry", "is", "a", "random", "dude", "." ],
        [ "Linguistics", "is", "extremely", "interesting", "while", "being", "highly", "relevant", "." ],
        [ "Linguistics", "is", "extremely", "interesting", "while", "being", "highly", "relevant", "." ],
        ]
    tags = [
        ['B-ARG0', 'B-V', 'O', 'O', 'O', 'O'],
        ['B-ARG0', 'B-V', 'B-ARG1', 'O', 'B-ARG2', 'O', 'I-ARG2', 'O', 'O'],
        ['O', 'O', 'O', 'O', 'O', 'B-V', 'B-ARG1', 'I-ARG1', 'O'],
        ]

    # Initialize
    vocab = Vocabulary()
    vocab.load_from_dir()
    config["num_embeddings"] = vocab.vocab_len
    labels = Labels()
    re_model = REModel(config)

    prec = Preprocessor(vocab, labels)

    decoder = Decoder(vocab, labels)

    # model_input = preprocess_batch_tagless(sentences, prec)
    re_model.train = True
    # decoder_output = decoder.decode(output)

    optimizer = torch.optim.Adam(re_model.parameters())


    for i in range(0):
        model_input = preprocess_batch(tokens, tags, prec)
        output = re_model(model_input)
        loss = output["loss"]

        optimizer.zero_grad() # Clear optimizer gradients

        loss.backward()
        optimizer.step()

    p = Path(__file__).parent.resolve()
    file_dir = Path.joinpath(p.parent, "data/OIE/train.oie.conll")

    i = 0
    batch_tokens = []
    batch_tags = []
    for tokens, tags in get_tokens_oie(file_dir):

        i += 1

        if i == 50:
            if batch_tokens and batch_tags:
                optimizer.zero_grad() # Clear optimizer gradients

                model_input = preprocess_batch(batch_tokens, batch_tags, prec)
                output = re_model(model_input)
                loss = output["loss"]
                print(loss)
                loss.backward()
                optimizer.step()
                # print(decoder.decode(output)["tags"])
            i = 0
            batch_tokens, batch_tags = [], []

        if tokens and tags:
            batch_tokens.append(tokens)
            batch_tags.append(tags)

