from constants import Relations, POS
from utils import DPHelper
from typing import Dict, List
from allen_models import DepParse


def generate(sentence: str):
    dep_parse = DepParse()
    root : Dict = dep_parse.get_tree(sentence)

    # Is this applicable only to root?
    subj = DPHelper.get_subject(root)
    obj = DPHelper.get_object(root)

    if subj == None:
        print("No nominal subject")
    else:
        if DPHelper.is_proper_noun(subj) and DPHelper.is_proper_noun(obj): # NE subject and object
            relations = []
            '''
            NSUBJ ------- ROOT -------- DOBJ
                            |
            '''
            for prep in DPHelper.get_child_type(root, Relations.PREPOSITION):
                '''             |
                               PREP ----
                                |
                '''
                pred_objs = DPHelper.get_child_type(prep, Relations.PREDICATE_OBJECT)
                for pred_obj in pred_objs: # There should only be one pobj per preposition, though conjuncting objs are possible
                    '''                   ------ POBJ '''
                    nouns = pobj_nouns(pred_obj)
                    print(nouns)
                conjunctions = DPHelper.get_child_type(prep, Relations.CONJUNCTION)
                for conj in conjunctions:
                    '''         |
                               CONJ
                    '''
                    # print(conj)


def pobj_nouns(pobj) -> List[str]:
    print(pobj)
    """ Finds pobjs with pobjs as root, also look for conjunctions """
    nouns = []
    nouns.append(full_noun(pobj))
    for conj in DPHelper.get_child_type(pobj, Relations.CONJUNCTION): # Conjuncting predicate objects are also relations
        nouns.append(full_noun(conj))
    return nouns

def full_noun(noun) -> str:
    full = ""
    print(noun["children"])
    for child in noun["children"]:
        if not DPHelper.is_leaf(child):
            continue
        elif child["link"] == Relations.ADJECTIVAL_MODIFIER:
            full = child["word"] # FIXME Assume singular adjectival modifiers for now
        elif child["link"] == Relations.NOUN:
            full = " ".join(full, child["word"])
        else:
            continue
    return "".join([full, noun["word"]]) if not full else " ".join([full, noun["word"]])




# sentence = "Federer hired Annacone as his coach."
# generate(sentence)
sentence = "Federer hired Annacone as his coach and business partner and as a permanent friend."
generate(sentence)
# sentence = "Annacone was hired as Federer's coach."
# generate(sentence)
# sentence = "Hired, was Annacone as Federer's coach."
# generate(sentence)
