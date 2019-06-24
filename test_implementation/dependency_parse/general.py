from typing import Dict, List
from .constants import Relations, POS

# ========================================= General Methods =================================================


def recursive_prep_search(verb: Dict, pobj: Dict):
    """
    VARIABLE ------------- ROOT(VB) ---------------- VARIABLE
                              |
                            CONJ(VB) ----- POBJ (Can also be DOBJ)
                                            |
                                            PREP ---- POBJ
                                                        .
                                                        .
                                                        .

    Conjunctive verbs for Subj of sentence, recursively search for nested prepositional phrases,
    if DOBJ one level up is noun and POBJ of PREP at lower level is NNP, establish relation with root subj
    """
    if DPHelper.is_proper_noun(pobj): # Base case
        obj = get_noun_phrase(pobj, proper_noun=True)
        relation = get_noun_phrase(verb)
        print("Obj: %s" % [obj], "\nRelation: %s" % [relation])
    elif DPHelper.is_noun(pobj): # Represents relation between root subj and pobj
        prep = DPHelper.get_child_type(pobj, Relations.PREPOSITION)
        if prep:
            pobj_at_next_level = get_predicate_object(prep[0])
            recursive_prep_search(pobj, pobj_at_next_level) # pobj at current level now represents possible relation
    else:
        return



def get_predicate_object(prep: Dict) -> Dict:
    # Gets pobj or dobj of prep, assumes only 1 such object
    pred_objs = DPHelper.get_child_type(prep, Relations.PREDICATE_OBJECT)
    direct_objs = DPHelper.get_child_type(prep, Relations.DIRECT_OBJECT) # Possibility nonwithstanding
    assert( (len(pred_objs) + len(direct_objs)) == 1)
    return pred_objs[0] if pred_objs else direct_objs[0]


def get_all_nouns(noun: Dict) -> List[str]:
    # Finds all noun phrases with given word as root, also look for conjunctions
    nouns = []
    nouns.append(get_noun_phrase(noun))
    for conj in DPHelper.get_child_type(noun, Relations.CONJUNCTION): # Conjuncting predicate objects are also relations
        nouns.append(get_noun_phrase(conj))

    for appos in DPHelper.get_child_type(noun, Relations.APPOSITION): # Appositional nouns
        nouns.append(get_noun_phrase(appos))

    return nouns


def get_all_proper_nouns(noun: Dict) -> List[str]:
    # Finds all proper noun phrases with given word as root, also look for conjunctions
    proper_nouns = []
    proper_nouns.append(get_noun_phrase(noun, True)) # Assume root noun is proper noun
    for conj in DPHelper.get_child_type(noun, Relations.CONJUNCTION): # Conjuncting predicate objects are also relations
        if DPHelper.is_proper_noun(conj):
            proper_nouns.append(get_noun_phrase(conj, True))

    for appos in DPHelper.get_child_type(noun, Relations.APPOSITION): # Conjuncting predicate objects are also relations
        if DPHelper.is_proper_noun(appos):
            proper_nouns.append(get_noun_phrase(appos, True))

    return proper_nouns


def get_temporal(word: Dict) -> str:
    """
    Given word of temporal nature, get full phrase
    - Note positional information of root word given punctuation
    """
    if not word.get("children"):
        return word["word"]
    else:
        full = ""
        root_added = False
        for child in word["children"]:
            if child["link"] == Relations.PUNCTUATION:
                if not root_added:
                    full = "".join([full, word["word"]]) if not full else " ".join([full, word["word"]])
                    root_added = True
                full = "".join([full, child["word"]])
            else:
                full = "".join([full, child["word"]]) if not full else " ".join([full, word["word"]])
        return full



def get_noun_phrase(noun: Dict, proper_noun=False) -> str:
    """
    Given a noun, include all modifier NN to get full noun phrase

    Arguments:
        proper_noun : If noun is proper (Named Entity), don't include ADJMOD
    """
    if not noun.get("children"):
        return noun["word"]
    else:
        full = ""
        for child in noun["children"]:
            if child["link"] == Relations.PREPOSITION and proper_noun: # Special cases such as University of X
                pobj = get_predicate_object(child)
                return "{} {} {}".format(noun["word"], child["word"], pobj["word"])
            elif not DPHelper.is_leaf(child):
                continue
            elif child["link"] == Relations.ADJECTIVAL_MODIFIER and not proper_noun:
                full = child["word"] # FIXME Assume singular adjectival modifiers for now
            elif child["link"] == Relations.NOUN:
                full = "".join([full, child["word"]]) if not full else " ".join([full, child["word"]])
            else:
                continue
        return "".join([full, noun["word"]]) if not full else " ".join([full, noun["word"]])


"""
=========================== DPHelper ====================================
"""


class DPHelper:

    @staticmethod
    def is_noun(word: Dict) -> bool:
        # TODO Find out why there can be multiple attributes
        return DPHelper.is_proper_noun(word) or \
        word["attributes"][0] == POS.NOUN or \
        word["attributes"][0] == POS.NOUN_PLURAL

    @staticmethod
    def is_proper_noun(word: Dict) -> bool:
        return word["attributes"][0] == POS.PROPER_NOUN # TODO Find out why there can be multiple attributes

    def is_verb(word: Dict) -> bool:
        verb_forms = [
            POS.VERB_BASE,
            POS.VERB_PAST,
            POS.VERB_GERUND,
            POS.VERB_PAST_PARTICIPLE,
            POS.VERB_3SP,
            POS.VERB_NON_3SP
            ]
        return word["attributes"][0] in verb_forms

    @staticmethod
    def has_possession_by(word: Dict) -> bool:
        return len(DPHelper.get_child_type(word, Relations.POSSESSION_BY)) > 0

    @staticmethod
    def get_possessor(word: Dict) -> bool:
        assert(DPHelper.is_noun(word))
        return DPHelper.get_child_type(word, Relations.POSSESSION_BY)[0]

    @staticmethod
    def get_subject(root: Dict) -> Dict:
        # Nominal subject or clausal subject (Assume 1)
        for child in root["children"]:
            if child["link"] == Relations.NOMINAL_SUBJECT or \
               child["link"] == Relations.CLAUSAL_SUBJECT or \
               child["link"] == Relations.PASSIVE_NOM_SUBJECT:
                return child

    @staticmethod
    def get_object(root: Dict) -> Dict:
        for child in root["children"]:
            if child["link"] == Relations.DIRECT_OBJECT or \
               child["link"] == Relations.PREDICATE_OBJECT or \
               child["link"] == Relations.INDIRECT_OBJECT:
                return child

    @staticmethod
    def get_child_type(word: Dict, child_type: Relations) -> List[Dict]:
        if not word.get("children"):
            return[]
        else:
            return list(filter(lambda child: child["link"] == child_type, word["children"]))


    @staticmethod
    def is_leaf(word: Dict) -> bool:
        return "children" not in word
