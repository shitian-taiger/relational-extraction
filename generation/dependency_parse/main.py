import logging
from logging import INFO
from typing import Dict, List
from .constants import Relations, POS
from .evaluator import *
from .general import DPHelper
from .general import *
from .utils import *

# ========================================= DRIVER =================================================

def generate(root: Dict):

    # {"relation": <>, "subjs": [<>], "objs": [<>]}
    relations: List[Dict] = []

    # Is this applicable only to root?
    subj = DPHelper.get_subject(root)
    obj = DPHelper.get_object(root)


    if subj is not None and DPHelper.is_proper_noun(subj) and \
       obj is not None and DPHelper.is_proper_noun(obj):

        if DPHelper.is_proper_noun(subj) and DPHelper.is_proper_noun(obj):
            logging.log(INFO, "============ Rooted NNP SUBJECT and NNP OBJECT =============")
            subjs = get_all_nouns(subj, proper_noun=True)
            objs = [get_noun_phrase(obj, proper_noun=True)]
            aux_relations = sub_obj_vbroot(root) # Relations between subject and object
            relations = relations + create_relations(subjs, aux_relations, objs)

            # Relations within clausal complements
            open_comp: List[Dict] = DPHelper.get_child_type(root, Relations.OPEN_CLAUSAL_COMPLEMENT)
            comp: List[Dict] = DPHelper.get_child_type(root, Relations.CLAUSAL_COMPLEMENT)
            if open_comp: # Assume for now open_comps all relate to object
                subjs = [get_noun_phrase(obj, proper_noun=True)]
                objs, xcomp_relations = x_comp(open_comp[0]) # TODO Can there be multiple xcomps?
                relations = relations + create_relations(subjs, xcomp_relations, objs)

    elif subj is not None and DPHelper.is_proper_noun(subj):

        # Check for clausal complement for Subj (INDEPENDENT)
        if DPHelper.get_child_type(root, Relations.CLAUSAL_COMPLEMENT):
            pass

        # Passive subject, look into preposition for predicate object with possessive
        if DPHelper.is_proper_noun(subj) and subj["link"] == Relations.PASSIVE_NOM_SUBJECT:
            logging.log(INFO, "============= NNP PASSIVE SUBJECT ===============")
            subjs = get_all_nouns(subj, proper_noun=True)
            objs, aux_relations, appos = subjpass(root)
            for appos_instance in appos:
                relations = relations + create_relations(subjs, appos_instance["relation"], appos_instance["obj"])
            relations = relations + create_relations(subjs, aux_relations, objs)

        # Possible case where root is noun and hence subject is not labeled passive but relation still exists
        elif DPHelper.is_noun(root):
            logging.log(INFO, "============= NNP SUBJECT with NOUN ROOT ===============")
            subjs = get_all_nouns(subj, proper_noun=True)
            objs, aux_relations = nnroot_subj(root)
            relations = relations + create_relations(subjs, aux_relations, objs)

        # Usually the case that the direct obj being non-NNP represents relation
        elif DPHelper.is_verb(root) and obj is not None:
            logging.log(INFO, "============= NNP SUBJECT with VERB ROOT (NON-NNP DOBJ present) ===============")
            subjs = get_all_nouns(subj, proper_noun=True)
            objs, aux_relations = vbroot_subj_xobj(root)
            relations = relations + create_relations(subjs, aux_relations, objs)

        # Root verb without concrete noun form but valid relation (E.g. lives, resides) TODO Do we require `in/from etc.` for preposition?
        elif DPHelper.is_verb(root):
            logging.log(INFO, "============= NNP SUBJECT with VERB ROOT ===============")
            subjs = get_all_nouns(subj, proper_noun=True)
            objs, aux_relations = vbroot_subj(root)
            relations = relations + create_nested_relations(subjs, aux_relations, objs)

        else:
            logging.log(INFO, "============= NNP SUBJECT with UNKNOWN STRUCTURE ===============")


    else:
        logging.log(INFO, "============== NOUN ROOT - No Direct SUBJ and OBJ ================")

        if subj is not None: # Mostly likely noun with possessive or nested
            if (subj["link"] == Relations.PASSIVE_NOM_SUBJECT): # Necessarily assume this since noun subj is possessive, else should Corefer
                logging.log(INFO, "============= NESTED POSSESSIVE OF PASSIVE SUBJECT ===============")
                subjs = subjpass_poss(subj)
            if DPHelper.has_rc_modifier(root): # NNP still might be present in rc modifier
                logging.log(INFO, "============= RELATIVE CLAUSE MODIFIER PRESENT ===============")

        if DPHelper.is_proper_noun(root):
            subj, relations, obj = nnproot(root)

    all_rel_tuples = []
    for relation in relations:
        rel_tuples = [(sub, relation['relation'], obj) for sub in relation['subjs'] for obj in relation['objs']]
        all_rel_tuples += rel_tuples
    return all_rel_tuples

