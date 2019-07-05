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
        nouns = get_all_nouns(get_predicate_object(prep))
        relations = relations + nouns

        # Conjuncting relations for subj and obj
        for conj in DPHelper.get_child_type(prep, Relations.CONJUNCTION):
            nouns = get_all_nouns(get_predicate_object(conj)) # Assume here that conjunction is also prepositional
            relations = relations + nouns

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
        relations = relations + [get_noun_phrase(open_comp)]
        dir_obj = get_predicate_object(open_comp)
        objs = objs + get_all_nouns(dir_obj, proper_noun=True)

    return objs, relations

def subjpass(root: Dict):
    '''
    Assumed nominal subject, otherwise non-named entity
    Valid only if pobj has a possessive

    NSUBJPASS ------- ROOT(VB)
                       |
    '''
    relations, objs, appos_rels = [], [], []

    for appos in DPHelper.get_appositional_phrases(DPHelper.get_subject(root)):
        appos_objs, appos_relations = pobj_appositional_relations(appos)
        appos_rels.append({"relation": appos_relations, "obj": appos_objs})

    root_relations = False # True if predicate has NNP within preposition
    for prep in DPHelper.get_child_type(root, Relations.PREPOSITION):
        pred_obj = get_predicate_object(prep)

        if DPHelper.has_possessor(pred_obj) and \
           DPHelper.is_proper_noun(DPHelper.get_possessor(pred_obj)): # Possessive should be named entity
            objs = objs + [get_noun_phrase(DPHelper.get_possessor(pred_obj), proper_noun=True)]
            relations = relations + get_all_nouns(pred_obj)

        elif DPHelper.is_proper_noun(pred_obj):
            objs = objs + get_all_nouns(pred_obj, proper_noun=True)
            root_relations = True
            for appos in DPHelper.get_appositional_phrases(pred_obj):
                # Getting all proper nouns takes care of appositional nouns, deal with appos phrases (non NNP appos) here
                appos_objs, appos_relations = pobj_appositional_relations(appos)
                appos_rels.append({"relation": appos_relations, "obj": appos_objs})
        else:
            continue
    relations = relations + [get_noun_phrase(root)] if root_relations else relations

    for tmod in DPHelper.get_child_type(root, Relations.TEMPORAL_MODIFIER): # Temporal modifier directly by root verb
        relations = relations + [get_noun_phrase(root)]
        objs = objs + [get_temporal(tmod)]

    return objs, relations, appos_rels


def nnroot_subj(root: Dict):
    '''
    Noun root with only nominal subject, find entity in prepositions
    - Differs from above in terms of nominality of object

    NSUBJ ------- ROOT(NN)
                       |
    '''
    relations = [get_noun_phrase(root)]

    objs = []
    # Direct possessor relation between nominal subject root noun possessor
    if DPHelper.is_noun(root) and DPHelper.has_possessor(root):
        objs = objs + get_all_nouns(DPHelper.get_possessor(root), proper_noun=True)

    for prep in DPHelper.get_child_type(root, Relations.PREPOSITION):
        pred_obj = get_predicate_object(prep)
        objs: List[Dict] = [] # Actual Named entity to find (Assume no root noun possessor)

        if DPHelper.is_proper_noun(pred_obj):
            objs = objs + get_all_nouns(pred_obj, proper_noun=True) # Possibility of multiple conjuncting proper
        else:
            continue
    return objs, relations


def vbroot_subj_xobj(root: Dict):
    '''
    Direct object present with verb root, presume dobj represents relation
    - Most relevant to cases with basic prepositions such `in / from etc.`

    NSUBJ(NNP) ------- ROOT(VB) ---------- DOBJ(NN)
                          |
    '''
    relations = get_all_nouns(DPHelper.get_object(root))
    objs = []
    for prep in DPHelper.get_child_type(root, Relations.PREPOSITION):
        pred_obj = get_predicate_object(prep)
        if prep["word"] == "in": # We handle this separately due to possibility of nested `in`s
            objs = objs + get_nested_in_pobjs(pred_obj)
        elif DPHelper.is_proper_noun(pred_obj):
            objs = objs + [get_noun_phrase(pred_obj)]

    if objs:
        return objs, relations
    else:
        return [], []


def vbroot_subj(root: Dict):
    '''
    Non passive subject and verb root but still valid relation

    NSUBJ ------- ROOT(VB)
                       |
    '''
    objs, aux_relations = [], []
    for prep in DPHelper.get_child_type(root, Relations.PREPOSITION):
        pred_obj = get_predicate_object(prep)

        # Possessive object can be part of proper noun such as XXX Hospital
        if DPHelper.has_possessor(pred_obj):
            aux_relations.append([root["word"]])
            objs.append([get_noun_phrase(pred_obj, proper_noun=True)])
            # Find nested `in` predicate objects referring to the same subj-rel
            pobj_objs = get_nested_in_pobjs(pred_obj)
            if pobj_objs:
                objs.append(pobj_objs)
                aux_relations.append([root["word"]])


        if prep["word"].istitle(): # We assume this phrase came before subject, nonetheless referring to root subject FIXME Hacky, please verify
            nested_prep_relation = recursive_prep_search(pred_obj)
            if nested_prep_relation:
                aux_relations.append([nested_prep_relation["relation"]])
                objs.append([nested_prep_relation["obj"]])

        if DPHelper.is_proper_noun(pred_obj):
            aux_relations.append([get_noun_phrase(root)])
            objs.append(get_all_nouns(pred_obj, proper_noun=True))
        elif DPHelper.get_prepositional_comp(prep): # Prepositional complement (pred_obj handles returning of pcomp)
            nested_prep_relation = recursive_prep_search(pred_obj)
            if nested_prep_relation:
                aux_relations.append([nested_prep_relation["relation"]])
                objs.append([nested_prep_relation["obj"]])

    for conj in DPHelper.get_child_type(root, Relations.CONJUNCTION):
        conj_prep: List[Dict] = DPHelper.get_child_type(conj, Relations.PREPOSITION)
        conj_obj: Dict = DPHelper.get_object(conj)

        if conj_prep and conj_obj: # Conjunction object represents relation to object of conj_preposition
            conj_prep_obj = get_predicate_object(conj_prep[0])
            nnp_prep_obj = get_all_nouns(conj_prep_obj, proper_noun=True)
            if nnp_prep_obj: # Relation only valid
                objs.append(nnp_prep_obj)
                aux_relations.append([get_noun_phrase(conj_obj)])

        elif conj_prep: # Assume here non nested prepositions in conjunction
            conj_prep_comp = DPHelper.get_prepositional_comp(conj_prep[0])
            if conj_prep_comp: # Prepositional Complement
                # TODO Do we ignore this considering prepositional complements usually don't contain concrete relations
                continue
            else:
                conj_prep_obj = get_predicate_object(conj_prep[0])
                if DPHelper.is_proper_noun(conj_prep_obj):
                    objs.append(get_all_nouns(conj_prep_obj, proper_noun=True))
                    aux_relations.append([get_noun_phrase(conj)])

        # FIXME We assume for now that this case is mutually exclusive with first
        if not conj_prep:
            nested_prep_relation = recursive_prep_search(conj_obj)
            if nested_prep_relation:
                aux_relations.append([nested_prep_relation["relation"]])
                objs.append([nested_prep_relation["obj"]])

    return objs, aux_relations


def nnproot(root: Dict):
    '''
    NONE ------ ROOT ----- NONE
                 |

    Root proper noun is passive subject, attempt finding active obj in predicate object of preposition
    '''
    relations = []
    objs = []
    subj = get_noun_phrase(root, proper_noun=True)
    for prep in DPHelper.get_child_type(root, Relations.PREPOSITION):
        pred_obj = get_predicate_object(prep)
        if DPHelper.is_noun(pred_obj):
            objs.append(get_noun_phrase(DPHelper.get_possessor(pred_obj), proper_noun=True))
            relations = relations + [get_noun_phrase(pred_obj)]
        else:
            continue
    return subj, relations, objs


def subjpass_poss(subjpass: Dict):
    '''
    NSUBJPASS(NN) ---------- ROOT
         |

    Consider cases where there is direct possessor or nested possessor in prepositional object
    '''
    subjs = []
    if DPHelper.has_possessor(subjpass):
        return DPHelper.get_child_type(subjpass, Relations.POSSESSION_BY)
    else: # Find subjects in predicate objects
        for prep in DPHelper.get_child_type(subjpass, Relations.PREPOSITION):
            pred_objs = DPHelper.get_child_type(prep, Relations.PREDICATE_OBJECT)
            subjs_raw : List[Dict] = list(map(lambda pred_obj: pred_obj if DPHelper.is_proper_noun(pred_obj) else \
                                              DPHelper.get_possessor(pred_obj), pred_objs))
            subjs = subjs + list(map(lambda nnp: get_noun_phrase(nnp, proper_noun=True), subjs_raw))
        return subjs


def subj_rcmod(root: Dict):
    '''
    SUBJ(NN) ------------- ROOT
                             |
                           RCMOD
    '''
    assert(DPHelper.has_rc_modifier(root))
    subj = DPHelper.get_subject(root)
    obj = DPHelper.get_object(root)
    subjs, relations, objs = [], [], []
    if DPHelper.is_proper_noun(subj): # Assume there is a subject
        subjs = get_noun_phrase(subj, proper_noun=True)
    elif subj["attributes"][0] == POS.WH_PRONOUN and DPHelper.is_proper_noun(root):
        # If subject is not directly known, refer to direct parent of modifier
        subjs = get_noun_phrase(root, proper_noun=True)
    else: # Pass if unable to find subject
        return subjs, relations, objs

    for prep in DPHelper.get_child_type(rcmod, Relations.PREPOSITION):
        for conj in DPHelper.get_child_type(prep, Relations.CONJUNCTION):
            relations = recursive_prep_search()

    for conj in DPHelper.get_child_type(prep, Relations.CONJUNCTION):
        return subjs, relations, objs


