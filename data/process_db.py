import pandas as pd
# Database
import sqlite3
import spacy
from typing import Tuple, List, Dict
from pathlib import Path
from spacy.lang.en import English

SENTENCE_TABLE = "Sentence"
VALID_INSTANCES_TABLE = "PositiveInstance"
INVALID_INSTANCES_TABLE = "NegativeInstance"

db_file_path = Path.joinpath(Path(__file__).parent, "store.db")

# Spacy
nlp = English()
tokenizer = nlp.Defaults.create_tokenizer(nlp)

def process_db(filename):
    """
    Retrieves the positive and negative instances for each sentence, generates IOB2 tags for positive instances
    """
    connection = sqlite3.connect(str(db_file_path))
    sentence_cursor = connection.cursor()
    instance_cursor = connection.cursor()

    iob_file = open(filename, "a+")
    sentence_cursor.execute('SELECT * FROM {} WHERE processed=1'.format(SENTENCE_TABLE)) # Select only processed sentence instances
    for row in sentence_cursor:
        sentence = row[0]
        valid_keys = [row[1]] if isinstance(row[1], int) else [int(x) for x in row[1].split(',')]
        invalid_keys = [row[2]] if isinstance(row[2], int) else [int(x) for x in row[2].split(',')]
        for key in valid_keys:
            instance_cursor.execute("SELECT * FROM PositiveInstance WHERE rowid={}".format(key))
            instance = instance_to_iob(sentence, instance_cursor.fetchone())
            iob_file.write(instance)
        for key in invalid_keys:
            instance_cursor.execute("SELECT * FROM NegativeInstance WHERE rowid={}".format(key))

    iob_file.close()


def tag_phrase(phrase: str, tag: str):
    """
    Given word(s), tokenizes and tags correspondingly
    For each token: <token> \t <B-tag|I-tag|O>, line separated
    """
    tagged = ""
    beginning_tag = True
    for token in tokenizer(phrase):
        if token.text == " ":
            pass
        elif tag == "O":
            tagged = "\n".join([tagged, "{}\t{}".format(token, tag)])
        elif beginning_tag:
            tagged = "\n".join([tagged, "{}\t{}".format(token, "B-" + tag)])
            beginning_tag = False
        else:
            tagged = "\n".join([tagged, "{}\t{}".format(token, "I-" + tag)])
    return tagged


def instance_to_iob(sentence: str, instance: Tuple):
    """
    Given an instance of a relational tuple, performs IOB-2 tagging with ("ENT1" / "REL" / "ENT2")
    FIXME Improve robustness
    -- Assumptions:
       - Singular instance of entity and relation within sentence

    Returns:
       iob_instance: `\n` separated tokens with each row: <word_index>, <token>, <IOB-2 tag>
    """
    ent1, rel, ent2 = instance[0], instance[1], instance[2]
    args = [{"phrase": ent1, "tag": "ENT1", "idxs": (sentence.find(ent1), sentence.find(ent1) + len(ent1)) }, \
            {"phrase": rel, "tag": "REL", "idxs": (sentence.find(rel), sentence.find(rel) + len(rel))}, \
            {"phrase": ent2, "tag": "ENT2", "idxs": (sentence.find(ent2), sentence.find(ent2) + len(ent2))}]
    args.sort(key=lambda arg: arg["idxs"][0]) # Sort arguments by start index to facilitate tagging

    # Separate sentence into phrases separated by `args`, tokenize and tag with `tag_phrase`
    start_index = 0
    instance = ""
    for arg in args:
        if not arg["idxs"][0] == 0:
            out_phrase = sentence[start_index: arg["idxs"][0]]
            instance = "".join([instance, tag_phrase(out_phrase, "O")])
        instance = "".join([instance, tag_phrase(arg["phrase"], arg["tag"])])
        start_index = arg["idxs"][1]
    # Append last phrase
    out_phrase = sentence[start_index: len(sentence) - 1]
    instance = "".join([instance, tag_phrase(out_phrase, "O")])

    # Add word_index per token, skip the first element ""
    iob_instance = []
    for i, row, in enumerate(instance.split("\n")[1:]):
        iob_instance.append("\t".join([str(i), row]))
    return "\n".join(["\n".join(iob_instance), "", ""])


if __name__ == "__main__":
    file_name = Path.joinpath(Path(__file__).parent, "generated_instances.txt")
    process_db(file_name)
