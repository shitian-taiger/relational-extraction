# Relational Extraction Model

## Setup

Downloading and extraction of GLOVE Embeddings: `download.py`\
For replication of Allen OIE model refer to branch: `base` and set `DOWNLOAD_ALLEN_OIE = True` in `download.py`

### Configuration
For customized tokens, embeddings and labels, Ensure `Custom` folder structure as below:
```
--- Custom/
    |
    | - ne_embedding (Optional)
    |
    | - labels/
        |
        | - labels.txt
        | - tag_layer_bias (Optional)
        | - tag_layer_weights (Optional)
        |
    | - tokens/
        |
        | - token_embedder
        | - tokens.txt
        |
    | - pos/
        |
        | - pos_embedder (Optional)
        | - pos.txt
        |
    | - weights/ (Optional)
        |
        | - layer<i>_input_bias
        | - layer<i>_input_weight
        | - layer<i>_state_bias
        | - layer<i>_state_weight
        |    .
        |    .
        |    .
```
- 

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

Reference: https://taiger.atlassian.net/wiki/spaces/NLP/pages/705495046/OpenRE+as+Sequence+Labelling+Task

- Switched one-hot encoded predicate vector:\
`[1 if idx == B-pred_index else 0 for idx in len(tokens)]`\
to Entity tagging vector:\
`[1 if "ENT1" in label else 2 if "ENT2" in label else 0 for label in tags]`

- Add token POS-tagging vector (POS tags are taken from Spacy)\
For reference: https://github.com/explosion/spaCy/blob/master/spacy/lang/en/tag_map.py

***[Under Construction]***
- Integration of word2vecf token embedding: https://levyomer.files.wordpress.com/2014/04/dependency-based-word-embeddings-acl-2014.pdf


## Training and Prediction

Command Line utility not yet implemented.\
Entry point and configurations: `main.py` in root folder

For Prediction purposes, upstream process of NER is required. Currently defaults to spacy NER, for alterations refer to:\
`model_implementation/model/utils.py` function `_get_entity_idx_map`

