from typing import Dict, List
import re
import pandas as pd
from string import punctuation

def format_label(label: str):
    # Reformat to IOB-2
    if label == 'O':
        return label
    else:
        swapped = []
        swapped.append(label.split("-")[1]) # BIO Tag
        if 'P' in label: # Semantic Role Labeler using B-V instead of B-P
            swapped.append("V")
        else: # SRL BIO-ARGX
            swapped.append(label.split("-")[0][0] + "RG" + label.split("-")[0][1:])
        return "-".join(swapped)


def reorder_argtags(tags: List[str]):
    """
    Reorder ARG-<NUM> for tags since the OIE dataset argument sequence may not be in order,
    e.g. [B-ARG1, I-ARG1, B-V, B-ARG0, B-ARG0] --> [B-ARG0, I-ARG0, B-V, B-ARG1, I-ARG1]
    """
    tag_num, curr_index = 0, 0
    tags_iter = iter(tags)
    reordered_tags: List[str] = []
    for tag in tags_iter:
        if re.search("B-", tag) and not tag == "B-V": # Find only ARG tag
            curr_tag_num = tag_num
            curr_index += 1 # Advance to the next tag index
            tag_num += 1 # Advance tag number since we found an ARG
            if re.search(str(curr_tag_num), tag): # Skip instance if the ARG tag number already matches
                reordered_tags.append(tag)
                continue

            # Replace all ARG-X with ARG-<curr_tag_num>
            reordered_tags.append(tag.replace(str(tag[-1]), str(curr_tag_num)))
            next_tag = tags[curr_index]
            while re.search("I-", next_tag): # Search for trailing I-ARG tags
                next(tags_iter) # Advance iterator
                reordered_tags.append(next_tag.replace(str(tag[-1]), str(curr_tag_num)))
                if curr_index + 1 < len(tags):
                    curr_index += 1
                    next_tag = tags[curr_index]
                else:
                    break
        else:
            reordered_tags.append(tag)
            curr_index += 1
    return reordered_tags


def get_tokens_oie(file_path: str):
    df = pd.read_csv(file_path, sep="\t")
    tokens, tags = [], []
    for _, row in df.iterrows():
        token = row['word']
        tag = format_label(row['label'])
        if row["word_id"] == 0:
            yield tokens, reorder_argtags(tags)
            tokens, tags = [token], [tag]
        else:
            tokens.append(token)
            tags.append(tag)
