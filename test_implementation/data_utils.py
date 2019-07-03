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


def get_tokens_oie(file_path: str):
    df = pd.read_csv(file_path, sep="\t")
    tokens, tags = [], []
    for _, row in df.iterrows():
        token = row['word']
        tag = format_label(row['label'])
        if row["word_id"] == 0:
            yield tokens, tags
            tokens, tags = [token], [tag]
        else:
            tokens.append(token)
            tags.append(tag)
