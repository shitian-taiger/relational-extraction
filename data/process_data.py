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

def process_db(instance_file):
    """
    Retrieves the positive and negative instances for each sentence, generates IOB2 tags for positive instances and saves to file
    """
    connection = sqlite3.connect(str(db_file_path))
    sentence_cursor = connection.cursor()
    instance_cursor = connection.cursor()

    iob_file = open(instance_file, "a+")

    NUM_PROCESSED = 0
    # Select only processed sentence instances
    sentence_cursor.execute('SELECT * FROM {} WHERE processed=1 AND LENGTH(valid_keys) > 0'.format(SENTENCE_TABLE))
    for row in sentence_cursor:
        sentence = row[0]
        valid_keys = [row[1]] if isinstance(row[1], int) else [int(x) for x in row[1].split(',')]
        invalid_keys = [row[2]] if isinstance(row[2], int) else [int(x) for x in row[2].split(',')]
        for key in valid_keys:
            instance_cursor.execute("SELECT * FROM PositiveInstance WHERE rowid={}".format(key))
            instance = instance_to_iob(sentence, instance_cursor.fetchone())
            if not instance == "":
                NUM_PROCESSED += 1
                iob_file.write(instance)
        for key in invalid_keys:
            instance_cursor.execute("SELECT * FROM NegativeInstance WHERE rowid={}".format(key))

    print(NUM_PROCESSED)
    iob_file.close()


def process_nhb(instance_file):

    df = pd.read_csv('../data/ExtractedRelations.csv', sep=',')

    # Currently processed till 87000
    df = df[200000:] # Chinese characters
    num_tagged = 0
    with open(instances_file, "a+") as iob_file:
        for index, row in df.iterrows():

            if num_tagged % 1000 == 0:
                print("{} instances saved".format(num_tagged))

            sentence = row["Sentence"]
            ent1 = row["Entity 1"]
            rel = row["Relation"]
            ent2 = row["Entity 2"]

            ent1_span = row["Entity 1 Span"]
            rel_span = row["Relation Span"]
            ent2_span = row["Entity 2 Span"]
            instance_tuple = (ent1, rel, ent2)

            tagged = instance_to_iob(sentence, instance_tuple)
            if not tagged == "":
                iob_file.write(tagged)
                num_tagged += 1

    print("Total: {}".format(num_tagged))


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
    Given an instance of a relational tuple, performs IOB tagging with ("ENT1" / "REL" / "ENT2")
    FIXME Improve robustness
    -- Assumptions:
       - Singular instance of entity and relation within sentence

    Arguments:
        sentence: Entire sentence as string
        instance: Tuple of strings of < ent1, rel, ent2 >
    Returns:
        iob_instance: `\n` separated tokens with each row: <word_index>, <token>, <IOB-2 tag>
    """

    nlp = spacy.load('en_core_web_sm')
    pos_tags = [token.pos_ for token in nlp(sentence)]

    ent1, rel, ent2 = instance[0], instance[1], instance[2]
    args = [{"phrase": ent1, "tag": "ENT1", "idxs": (sentence.find(ent1), sentence.find(ent1) + len(ent1)) }, \
            {"phrase": rel, "tag": "REL", "idxs": (sentence.find(rel), sentence.find(rel) + len(rel))}, \
            {"phrase": ent2, "tag": "ENT2", "idxs": (sentence.find(ent2), sentence.find(ent2) + len(ent2))}]
    args.sort(key=lambda arg: arg["idxs"][0]) # Sort arguments by start index to facilitate tagging

    # Separate sentence into phrases separated by `args`, tokenize and tag with `tag_phrase()`
    curr_sentence_index = 0
    instance = ""
    for arg in args:
        # TEMP FIXME Arg not in sentence, fix in front-end
        if arg["idxs"][0] == -1:
            return ""

        if not arg["idxs"][0] == curr_sentence_index:
            non_arg_phrase = sentence[curr_sentence_index: arg["idxs"][0]]
            instance = "".join([instance, tag_phrase(non_arg_phrase, "O")])
        instance = "".join([instance, tag_phrase(arg["phrase"], arg["tag"])])
        curr_sentence_index = arg["idxs"][1]
    # Append last phrase
    non_arg_phrase = sentence[curr_sentence_index: len(sentence) - 1]
    instance = "".join([instance, tag_phrase(non_arg_phrase, "O")])

    # Add word_index and pos tag per token, skip the first element ""
    iob_instance = []
    try:
        for i, row, in enumerate(instance.split("\n")[1:]):
            iob_instance.append("\t".join([str(i), row, pos_tags[i]]))
        return "\n".join(["\n".join(iob_instance), "", ""])
    except:
        return ""


if __name__ == "__main__":
    instances_file = Path.joinpath(Path(__file__).parent, "generated_instances_validation.txt")
    # process_nhb(instances_file)
    # process_db(instances_file)



