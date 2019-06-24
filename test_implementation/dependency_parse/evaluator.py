from typing import Dict, List
from .constants import Relations, POS
from .general import DPHelper
from .general import *

def sub_obj_vbroot(root: Dict) -> List[str]:
    relations = []
    '''
    SUBJ ------- ROOT(VB) -------- OBJ
                    |
    '''
    for prep in DPHelper.get_child_type(root, Relations.PREPOSITION): # Prepositions (eg. as)
        '''
        Predicate objects joined by preposition, representing relation to subj/obj pair
        '''
        pred_objs = DPHelper.get_child_type(prep, Relations.PREDICATE_OBJECT)
        assert(len(pred_objs) == 1) # There should only be one pobj per preposition, though conjuncting objs to this pobj are possible
        nouns = get_all_nouns(pred_objs[0])
        relations = relations + nouns

        '''
        Conjunctions of preposition, referring to the same subj/obj pair
        '''
        conjunctions = DPHelper.get_child_type(prep, Relations.CONJUNCTION)
        for conj in conjunctions:
            pred_objs = DPHelper.get_child_type(conj, Relations.PREDICATE_OBJECT)
            assert(len(pred_objs) == 1) # TODO Similar to above, refactor
            nouns = get_all_nouns(pred_objs[0])
            relations = relations + nouns

    # Conjuncting relations for subj and obj
    for conj in DPHelper.get_child_type(root, Relations.CONJUNCTION):
        if conj["attributes"][0] == POS.NOUN:
            relations = relations + get_all_nouns(conj)

    return relations

def x_comp(open_comp: Dict):
    '''
    ---- XCOMP ---

    Same extraction mechanism as if root were noun, however,
    We should probably allow verbial relations in clausal complements
    '''
    objs, relations = [], []
    if DPHelper.is_noun(open_comp):
        return [], []
    else: # Verb case
        relations = relations + [open_comp["word"]]
        dir_obj = DPHelper.get_child_type(open_comp, Relations.DIRECT_OBJECT)[0]
        objs = objs + get_all_proper_nouns(dir_obj)

    return objs, relations

def subjpass(root: Dict):
    '''
    Assumed nominal subject, otherwise non-named entity
    Valid only if pobj has a possessive

    NSUBJPASS ------- ROOT(VB)
                       |
    '''
    relations = []
    obj = [] # Actual Named entity to find
    for prep in DPHelper.get_child_type(root, Relations.PREPOSITION):
        pred_objs = DPHelper.get_child_type(prep, Relations.PREDICATE_OBJECT)
        assert(len(pred_objs) == 1) # TODO Similar to above, refactor
        pred_obj = pred_objs[0]

        if DPHelper.has_possession_by(pred_obj) and \
           DPHelper.is_proper_noun(DPHelper.get_possessor(pred_obj)): # Possessive should be named entity
            obj = DPHelper.get_possessor(pred_obj)["word"]
            relations = relations + get_all_nouns(pred_obj)
        else:
            continue

    for tmod in DPHelper.get_child_type(root, Relations.TEMPORAL_MODIFIER): # Temporal modifier directly by root verb
        relations = relations + [root["word"]]
        obj = obj + [get_temporal(tmod)]

    for conj in DPHelper.get_child_type(root, Relations.CONJUNCTION):
        pass


    return obj, relations


def nnroot_subj(root: Dict):
    '''
    Noun root with only nominal subject, find entity in prepositions
    - Differs from above in terms of nominality of object

    NSUBJ ------- ROOT(NN)
                       |
    '''
    relations = [root["word"]]
    for prep in DPHelper.get_child_type(root, Relations.PREPOSITION):
        pred_objs = DPHelper.get_child_type(prep, Relations.PREDICATE_OBJECT)
        assert(len(pred_objs) == 1) # TODO Similar to above, refactor
        objs: List[Dict] = [] # Actual Named entity to find
        pred_obj = pred_objs[0]

        if DPHelper.is_proper_noun(pred_obj):
            objs = objs + get_all_proper_nouns(pred_obj) # Possibility of multiple conjuncting proper
        else:
            continue
    return objs, relations


def vbroot_subj(root: Dict):
    '''
    Special case for non passive subject and verb root but still valid relation

    NSUBJ ------- ROOT(VB)
                       |
    '''
    objs, aux_relations = [], []
    for prep in DPHelper.get_child_type(root, Relations.PREPOSITION):
        pred_obj = get_predicate_object(prep)
        if DPHelper.is_proper_noun(pred_obj):
            objs = objs + get_all_proper_nouns(pred_obj)

    for conj in DPHelper.get_child_type(root, Relations.CONJUNCTION):
        aux_relations = aux_relations + [conj["word"]] # TODO May not be legitimate relation
        for prep in DPHelper.get_child_type(conj, Relations.PREPOSITION):
            pred_obj = get_predicate_object(prep)
            objs = objs + get_all_proper_nouns(pred_obj)

    return objs, aux_relations


def nnproot(root: Dict):
    '''
    Root proper noun is passive subject, attempt finding active obj in predicate object of preposition

    NONE ------ ROOT ----- NONE
                 |
    '''
    relations = []
    subj = root["word"]
    for prep in DPHelper.get_child_type(root, Relations.PREPOSITION):
        pred_objs = DPHelper.get_child_type(prep, Relations.PREDICATE_OBJECT)
        assert(len(pred_objs) == 1) # TODO Similar to above, refactor
        pred_obj = pred_objs[0]
        if DPHelper.is_noun(pred_obj):
            obj = DPHelper.get_possessor(pred_obj)["word"]
            relations = relations + [get_noun_phrase(pred_obj)]
        else:
            continue
    return subj, relations, obj


