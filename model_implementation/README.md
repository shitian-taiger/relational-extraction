# Relational Extraction Model

## Setup

Downloading of GLOVE Embeddings to `glove.6B/` and Allen-OIE model tokens, labels and weights to `AllenOIE/`\
`python download.py`

### Configuration
For customized tokens, embeddings and labels, Ensure folder structure similar to `model_implementation/AllenOIE/`
```
--- <Custom Folder Name>
    |
    | - labels
        |
        | - labels.txt
        | - tag_layer_bias
        | - tag_layer_weights
        |
    | - tokens
        |
        | - token_embedder
        | - tokens.txt
        |
    | - weights
        |
        | - layer<i>_input_bias
        | - layer<i>_input_weight
        | - layer<i>_state_bias
        | - layer<i>_state_weight
        |    .
        |    .
        |    .
```

## Model Implementation

Base Model implementation:
Supervised OIE:
https://gabrielstanovsky.github.io/assets/papers/naacl18long/paper.pdf \
For demo verification: http://demo.allennlp.org/open-information-extraction

Note actual implementation in AllenNLP differs from stated implementation in OIE paper, rather utilized SRL model draws heavily from:\
https://kentonl.com/pub/hllz-acl.2017.pdf \

Implemented model structure is largely drawn from AllenNLP.\
(*Variational dropout of LSTM not implemented)\
(Viterbi Decoding of BIO tags as implemented in allennlp)


### Model Changes
Switched one-hot encoded predicate vector:\
`[1 if idx == B-pred_index else 0 for idx in len(tokens)]`\
to Entity tagging vector:\
`[1 if "ENT1" in label else 2 if "ENT2" in label else 0 for label in tags]`

***[Under Construction]***
- Add token POS-tagging vector
- Integration of word2vecf token embedding: https://levyomer.files.wordpress.com/2014/04/dependency-based-word-embeddings-acl-2014.pdf


## Training and Prediction

Command Line utility not yet implemented.\
Entry point: `main.py`
