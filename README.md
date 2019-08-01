# Open Relational Extraction

![Relational Extraction Intro](https://raw.githubusercontent.com/shitian-taiger/relational-extraction/master/images/re_info.png)

_For more information on please refer to the FAQ section on the front-end UI as well as documentation found at_ https://taiger.atlassian.net/wiki/spaces/NLP/pages/703791197/OpenRE+Overview

## Setup

_Python version: 3.6_

Installation of packages:
`pip install -r requirements.txt`

Downloading of GLOVE Embeddings and extraction of vocab into `model_implementation/Custom`:\
`python ./model_implementation/download.py`

Training/Prediction on model:\
`python main.py`

***For information on model, please refer to model_implementation README***

## User Interface for Data Tagging

### Front End
Dependency Installations:\
`npm install` within `./frontend-app`\
Start server:\
`npm start` within `./frontend-app`

***Refer to front-end README for more info***

### Back End
Start server:\
`python server.py`

***Downloads Allen NER, OIE, DP models to:*** `./generation/archived_models/`

sqlite3 database is saved in `data/store.db`\
DB Structure:
```
Sentence

| sentence | valid_keys | invalid_keys | processed |
|----------|------------|--------------|-----------|
|----------|------------|--------------|-----------|


PositiveInstance

| entity1 | rel | entity2 |
|---------|-----|---------|
|---------|-----|---------|


NegativeInstance

| entity1 | rel | entity2 |
|---------|-----|---------|
|---------|-----|---------|
```

For generation of data after tagging, run `process_db()` in `data/process_data.py`\
Generated data will be producted in folder `data/generated/`

## Data Generation Helper

### NER-OIE Processing:
Takes result of OIE and NER, and simply retrieves relevant instances of Named Entities with predicate as relation

### DP Processing:
Processes results of:\
https://arxiv.org/pdf/1611.01734.pdf \
based on Universal Dependencies:\
https://universaldependencies.org/

***For information on model, please refer to generation README***

## Processing of Database

The output data format post-processing of data is of:

```
| word_id | word   | label                                             | pos                    |
|---------|--------|---------------------------------------------------|------------------------|
| INTEGER | STRING | (B/I - ENT1) or (B/I - REL) or (B/I - ENT2) or O) | Spacy POS Tag for word |
```

## BRAT Preprocessing
For data tagged using BRAT Annotation tool, `./brat_preprocessing/preprocess.py` will produce `./brat_preprocessing/annotated/tagged.txt` with format as in https://github.com/gabrielStanovsky/supervised-oie/blob/master/data/train.oie.conll


