## Data Generation

### Introduction
Works in conjunction with data tagging UI considering the lack of data with respect to open relational extraction. Aid in extraction of relations between entities for validation.\
All auxiliary models used for data generation are from AllenNLP.

### NER-OIE generate
Makes use of OIE and NER models in combination to detect predicate relations between named entities within the model.\
Trivially takes the resultant subj-rel-obj tuples of OIE and creates relational tuples with if subject and object contains

### Generation with Dependency Parsing
Extract relations from processed dependencies as specified in Universal Dependencies: (https://universaldependencies.org/), together with corresponding POS tags, note the accuracy of processing is also affected by the upstream task of dependency parsing.

For a reference of parse results: https://demo.allennlp.org/dependency-parsing

The processing of the dependency structure is broken down into:
- Determination of General SUBJ/ROOT/OBJ structure `generate/dependency_parse/main.py`
- Processing of common patterns within determined structured `generate/dependency_parse/evaluator.py`

For a more comprehensive overview, refer to: https://taiger.atlassian.net/wiki/spaces/NLP/pages/704905231/OpenRE+Data+Generation

#### Common parse structures
The following represent common structures of parsed sentences, which can be classified into the following forms. (List is not non-exhaustive).

_Bracketed represent POS tags_

##### Nominal Subject attached to root (Most common)
```
SUBJ ------- ROOT(NN/VB)
                  |
```
Most sentences fall within the above case

##### Direct Subject and Object attached to root verb
```
SUBJ ------- ROOT(VB) -------- OBJ
                |
```
##### Root proper-noun is passive subject, relations might still exist in predicate objects
```
NONE ------ ROOT (NNP)----- NONE
                |
```

#### Common rules for extraction of relations:

Below are a few examples of the implemented logic for relational extraction conditional on the dependency parse.\
For full list of implemented extraction logic, refer to `generate/dependency_parse/evaluator.py` and `generate/dependency_parse/general.py`.

- Verb root direct relation between Subject and Object
    - E.g. Bob promoted Charlie ...

- Verb root relating subject to prepositionally-linked predicate object
    - E.g. Stapledon worked in shipping offices in Liverpool

- Possessive noun of Named Entity as relation to subject
    - E.g. Annacone was hired as Federer's coach.

- Appositional relation giving rise to same relations for Mark and Duke of Arkansas
    - E.g. Mark, Duke of Arkansas, ...
