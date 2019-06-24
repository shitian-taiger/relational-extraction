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
        nouns = get_all_nouns(get_predicate_object(prep))
        relations = relations + nouns

        '''
        Conjunctions of preposition, referring to the same subj/obj pair
        '''
        conjunctions = DPHelper.get_child_type(prep, Relations.CONJUNCTION)
        for conj in conjunctions:
            nouns = get_all_nouns(get_predicate_object(prep))
            relations = relations + nouns

    # Conjuncting relations for subj and obj
    for conj in DPHelper.get_child_type(root, Relations.CONJUNCTION):
        if conj["attributes"][0] == POS.NOUN:
            relations = relations + get_all_nouns(conj)

    return relations


def c_comp(open_comp: Dict):
    '''
    '''

def x_comp(open_comp: Dict):
    '''
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

    root_relations = False # True if predicate has NNP

    for prep in DPHelper.get_child_type(root, Relations.PREPOSITION):
        pred_obj = get_predicate_object(prep)

        if DPHelper.has_possession_by(pred_obj) and \
           DPHelper.is_proper_noun(DPHelper.get_possessor(pred_obj)): # Possessive should be named entity
            obj = DPHelper.get_possessor(pred_obj)["word"]
            relations = relations + get_all_nouns(pred_obj)

        elif DPHelper.is_proper_noun(pred_obj):
            obj = obj + get_all_proper_nouns(pred_obj)
            root_relations = True
            for appos in DPHelper.get_appositional_phrases(pred_obj):
                # Getting all proper nouns takes care of appositional nouns, deal with appos phrases (non NNP appos) here
                appos_objs, appos_relations = appositional_relations(appos)
                print("Appositional Objs: {}\nAppositional Relations: {}".format(appos_objs, appos_relations))
        else:
            continue
    relations = relations + [root["word"]] if root_relations else relations

    for tmod in DPHelper.get_child_type(root, Relations.TEMPORAL_MODIFIER): # Temporal modifier directly by root verb
        relations = relations + [root["word"]]
        obj = obj + [get_temporal(tmod)]

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
        pred_obj = get_predicate_object(prep)
        objs: List[Dict] = [] # Actual Named entity to find

        if DPHelper.is_proper_noun(pred_obj):
            objs = objs + get_all_proper_nouns(pred_obj) # Possibility of multiple conjuncting proper
        else:
            continue
    return objs, relations


def vbroot_subj(root: Dict):
    '''
    Non passive subject and verb root but still valid relation

    NSUBJ ------- ROOT(VB)
                       |
    '''
    objs, aux_relations = [], []
    for prep in DPHelper.get_child_type(root, Relations.PREPOSITION):
        pred_obj = get_predicate_object(prep)
        if DPHelper.is_proper_noun(pred_obj):
            aux_relations = aux_relations + [root["word"]]
            objs = objs + get_all_proper_nouns(pred_obj)

    for conj in DPHelper.get_child_type(root, Relations.CONJUNCTION):
        conj_prep: List[Dict] = DPHelper.get_child_type(conj, Relations.PREPOSITION)
        conj_obj: Dict = DPHelper.get_object(conj)

        if conj_prep and conj_obj: # Conjunction object represents relation to object of conj_preposition
            conj_prep_obj = get_predicate_object(conj_prep[0])
            nnp_prep_obj = get_all_proper_nouns(conj_prep_obj)
            if nnp_prep_obj: # Relation only valid
                objs = objs + nnp_prep_obj
                aux_relations = aux_relations + [get_noun_phrase(conj_obj)]

        elif conj_prep: # Assume here non nested prepositions in conjunction
            prep_comp = DPHelper.get_prepositional_comp(conj_prep[0])
            if prep_comp: # Prepositional Complement
                # TODO Do we ignore this considering prepositional complements usually don't contain concrete relations
                continue
            else:
                conj_prep_obj = get_predicate_object(conj_prep[0])
                if DPHelper.is_proper_noun(conj_prep_obj):
                    objs = objs + get_all_proper_nouns(conj_prep_obj)
                    aux_relations = aux_relations + [conj["word"]]

        # TODO We assume for now that this case is mutually exclusive with first
        if not conj_prep:
            recursive_prep_search(root, conj_obj) # TODO This usage technically doesn't conform to function definition

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
        pred_obj = get_predicate_object(prep)
        if DPHelper.is_noun(pred_obj):
            obj = DPHelper.get_possessor(pred_obj)["word"]
            relations = relations + [get_noun_phrase(pred_obj)]
        else:
            continue
    return subj, relations, obj


