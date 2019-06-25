from typing import Dict, List
from .constants import Relations, POS

# ========================================= General Methods =================================================


def appositional_relations(appos: Dict):
    '''
    -------------------POBJ
                        |
                       APPOS
    Assumed pobj is NNP and subj is pre-determined, this hence represents external appositional relation
    '''
    objs, relations = [], []
    for prep in DPHelper.get_child_type(appos, Relations.PREPOSITION):
        pred_obj = get_predicate_object(prep)
        if DPHelper.is_proper_noun(pred_obj):
            relations = relations + [get_noun_phrase(appos)]
            objs = get_all_nouns(pred_obj, proper_noun=True)
    return objs, relations


def recursive_prep_search(verb: Dict, pobj: Dict):
    '''
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
    '''
    if DPHelper.is_proper_noun(pobj): # Base case
        obj = get_noun_phrase(pobj, proper_noun=True)
        relation = get_noun_phrase(verb)
        print("++++++++++++ Recursive Prepositional Search +++++++++++++")
        print("Obj: %s" % [obj], "\nRelation: %s" % [relation])
    elif DPHelper.is_noun(pobj): # Represents relation between root subj and pobj
        prep = DPHelper.get_child_type(pobj, Relations.PREPOSITION)
        if prep:
            pobj_at_next_level = get_predicate_object(prep[0])
            recursive_prep_search(pobj, pobj_at_next_level) # pobj at current level now represents possible relation
    else:
        return


def get_nested_in_pobjs(pobj: Dict) -> List[str]:
    '''
    PREP ---------------- POBJ
                            |
                         PREP(IN)

    The `in` preposition is a frequent enough appositional relation to warrant this
    '''
    subjs = []
    if DPHelper.is_proper_noun(pobj):
        subjs = subjs + get_all_nouns(pobj, proper_noun=True)
    in_preps = list(filter(lambda prep: prep["word"] == "in", DPHelper.get_child_type(pobj, Relations.PREPOSITION)))
    for in_prep in in_preps:
        nested_pobj = get_predicate_object(in_prep)
        subjs = subjs + get_nested_in_pobjs(nested_pobj)
    return subjs



def get_predicate_object(prep: Dict, assertion=True) -> Dict:
    # Gets pobj or dobj of prep, assumes only 1 such object (Special cases do exist, in which case not using this for now)
    pred_objs = DPHelper.get_child_type(prep, Relations.PREDICATE_OBJECT)
    direct_objs = DPHelper.get_child_type(prep, Relations.DIRECT_OBJECT) # Possibility nonwithstanding
    assert( (len(pred_objs) + len(direct_objs)) == 1)
    return pred_objs[0] if pred_objs else direct_objs[0]


def get_all_nouns(noun: Dict, proper_noun=False) -> List[str]:
    # Finds all noun phrases with given word as root, also look for conjunctions
    nouns = []
    nouns.append(get_noun_phrase(noun, proper_noun))
    for conj in DPHelper.get_child_type(noun, Relations.CONJUNCTION): # Conjuncting predicate objects are also relations
        nouns.append(get_noun_phrase(conj, proper_noun))

    for appos in DPHelper.get_child_type(noun, Relations.APPOSITION): # Appositional nouns
        nouns.append(get_noun_phrase(appos, proper_noun))

    for noun_child in list(filter(lambda noun: not DPHelper.is_leaf(noun),
                                  DPHelper.get_child_type(noun, Relations.NOUN))): # Conjuncting nouns with `and` linked with NN
        nouns.append(get_noun_phrase(noun_child, proper_noun))
    return nouns


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
                    full = word_join(full, word)
                    root_added = True
                full = "".join([full, child["word"]])
            else:
                full = word_join(full, child)
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
            elif not DPHelper.is_leaf(child): # Works to remove concatenation of conjunctive nouns
                continue
            elif child["link"] == Relations.ADJECTIVAL_MODIFIER and not proper_noun:
                full = child["word"] # FIXME Assume singular adjectival modifiers for now
            elif child["link"] == Relations.NOUN:
                full = word_join(full, child)
            else:
                continue
        return word_join(full, noun)


def word_join(full: str, word: str):
    # Here because of extensive usage
    return "".join([full, word["word"]]) if not full else " ".join([full, word["word"]])


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
    def has_possessor(word: Dict) -> bool:
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
    def get_prepositional_comp(prep: Dict) -> Dict:
        for child in prep["children"]:
            if child["link"] == Relations.PREPOSITIONAL_COMP:
                return child

    @staticmethod
    def get_appositional_phrases(prep: Dict) -> Dict:
        appos: List[Dict] = DPHelper.get_child_type(prep, Relations.APPOSITION)
        return list(filter(lambda word: not DPHelper.is_proper_noun(word), appos))


    @staticmethod
    def get_child_type(word: Dict, child_type: Relations) -> List[Dict]:
        if not word.get("children"):
            return[]
        else:
            return list(filter(lambda child: child["link"] == child_type, word["children"]))


    @staticmethod
    def is_leaf(word: Dict) -> bool:
        return "children" not in word
