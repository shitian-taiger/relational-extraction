from typing import List, Dict, Tuple
from logging import log, WARN, INFO
from utils import AnnHeader, BRATHelper
from sentencesplit import sentencebreaks_to_newlines
import pandas as pd
import logging
import os
import re

logging.basicConfig(level=logging.CRITICAL)

def get_entity_rel(en_rel: str, rel_en: str):
    '''
    Extract arguments from (en_rel, rel_en)
    '''
    ent1 = re.search(r'Arg1:(.*)\s', en_rel).groups()[0]
    rel = re.search(r'Arg2:(.*)', en_rel).groups()[0]
    assert(rel == re.search(r'Arg1:(.*)\s', rel_en).groups()[0])
    ent2 = re.search(r'Arg2:(.*)', rel_en).groups()[0]
    return ent1, rel, ent2


def process_rels(terms_dict: Dict, text: str, rels: List):
    sentences = sentencebreaks_to_newlines(text)
    sent_stops = [m.start() for m in re.finditer('\n', sentences)] # Find sentence breaks
    assert(len(sentences) == len(text)) # Assume BRAT sent processing replaces spaces with \n

    sent_bounds: List = []

    for ent1, relation, ent2 in rels:
        arg1_bounds: List = BRATHelper.get_ent_bounds(ent1)
        rel_bounds: List = BRATHelper.get_ent_bounds(relation)
        arg2_bounds: List = BRATHelper.get_ent_bounds(ent2)

        sent_min  = min(arg1_bounds + rel_bounds + arg2_bounds)
        sent_max = max(arg1_bounds + rel_bounds + arg2_bounds)
        sent_min, sent_max = BRATHelper.get_sent_bounds(sent_stops, sent_min, sent_max) # Get bounds of sentence

        sent_bounds.append((sent_min, sent_max))

    return sent_bounds


def process_file(full_dir: str, ann_file: str):
    try:
        ann = open(os.path.join(full_dir, ann_file))
        txt = open(os.path.join(full_dir, re.sub("ann", "txt", ann_file)))
    except:
        log(WARN, "Could not open file %s" % txt)

    text = txt.readline()
    ann_text = ann.readline()

    try:
        df = pd.read_csv(ann, sep="\t", header=None)
    except:
        log(WARN, "No annotated data in file: %s" % ann_text)
        return -1, ""

    terms_dict = {}
    df_terms = df[lambda x: x[0].str.contains("T")]
    df_rels = df[lambda x: x[0].str.contains("R") & x[1].str.contains("REL")]

    # Add entities to dictionary
    for _, row in df_terms.iterrows():
        terms_dict[row[0]] = {
            "text": row[2],
            "bounds": row[1].split(" ")[1:]
        }

    # Process relationship tuples
    rels = []
    for i in range(len(df_rels) - 1): # Iterate 2 at a time, omit last index
        en_rel: str = df_rels.iloc[i][AnnHeader.desc]
        rel_en: str = df_rels.iloc[i+1][AnnHeader.desc]
        try: # Valid (en_rel, rel_en) pair
            arg1, rel, arg2 = get_entity_rel(en_rel, rel_en) # arg1, rel, arg2 are string keys for terms_dict

            ent1: Dict = terms_dict[arg1]
            relation: Dict = terms_dict[rel]
            ent2: Dict = terms_dict[arg2]

            rels.append((ent1, relation, ent2))
            i += 1
        except:
            pass

    sentence_bounds = process_rels(terms_dict, text, rels)
    tagged: str = BRATHelper.get_tagged_sentences(text, rels, sentence_bounds)

    ann.close()
    txt.close()

    return len(rels), tagged


def process_all():
    annotated_dir: str = os.path.join(os.getcwd(), "annotated")
    nhb_dir: str = os.path.join(annotated_dir, "nhb")
    process_dir = nhb_dir

    num_files = 0
    num_files_no_data = 0
    total_instances = 0

    for dir_name in os.listdir(process_dir):
        if not os.path.isdir(os.path.join(process_dir, dir_name)):
            continue
        for filename in os.listdir(os.path.join(process_dir, dir_name)):
            if filename.endswith(".ann"):
                log(INFO, "Extracting relationships from %s/%s" % (dir_name, filename))
                num_instance_tagged, tagged = process_file(os.path.join(process_dir, dir_name), filename)

                num_files += 1
                if num_instance_tagged == -1:
                    num_files_no_data += 1
                else:
                    total_instances += num_instance_tagged
                    with open(os.path.join(annotated_dir, "tagged.txt"), "a+") as tag_file: # Append to file
                        tag_file.write(tagged)

    print("NUMBER OF INSTANCES: %s" % total_instances)
    print("NUMBER OF FILES PROCESSED: %s" % (num_files - num_files_no_data))
    print("TOTAL NUMBER OF FILES: %s" % num_files)
    print("NUMBER OF FILES NOT ANNOTATED: %s" % num_files_no_data)

process_all()
