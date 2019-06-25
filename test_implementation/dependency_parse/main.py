from typing import Dict, List
from .constants import Relations, POS
from .general import DPHelper
from .general import *
from .evaluator import *

# ========================================= DRIVER =================================================

def generate(root: Dict):
    # Is this applicable only to root?
    subj = DPHelper.get_subject(root)
    obj = DPHelper.get_object(root)
    relations = []

    if subj is not None and DPHelper.is_proper_noun(subj) and \
       obj is not None and DPHelper.is_proper_noun(obj):

        if DPHelper.is_proper_noun(subj) and DPHelper.is_proper_noun(obj):
            print("============ Rooted NNP SUBJECT and NNP OBJECT =============")
            print("subj(s): %s" % get_all_nouns(subj))
            print("obj: %s" % obj["word"])
            relations = sub_obj_vbroot(root) # Relations between subject and object
            print("relations %s" % relations)

            # Relations within clausal complements
            open_comp: List[Dict] = DPHelper.get_child_type(root, Relations.OPEN_CLAUSAL_COMPLEMENT)
            comp: List[Dict] = DPHelper.get_child_type(root, Relations.CLAUSAL_COMPLEMENT)
            if open_comp: # Assume for now open_comps all relate to object
                print("+++++++++++++++++ Open Clausal Complement +++++++++++++++++")
                print("subj: %s" % obj["word"])
                objs, xcomp_relations = x_comp(open_comp[0]) # TODO Can there be multiple xcomps?
                print("objs: %s" % objs)
                print("xcomp_relations %s" % xcomp_relations)

            return

    elif subj is not None and DPHelper.is_proper_noun(subj):

        # Check for clausal complement for Subj (INDEPENDENT)
        if DPHelper.get_child_type(root, Relations.CLAUSAL_COMPLEMENT):
            pass

        # Passive subject, look into preposition for predicate object with possessive
        if DPHelper.is_proper_noun(subj) and subj["link"] == Relations.PASSIVE_NOM_SUBJECT:
            print("============= NNP PASSIVE SUBJECT ===============")
            print("subj(s): %s" % get_all_nouns(subj, proper_noun=True))
            obj, relations = subjpass(root)
            print("obj: %s " % obj)

        # Possible case where root is noun and hence subject is not labeled passive but relation still exists
        elif DPHelper.is_noun(root):
            print("============= NNP SUBJECT with NOUN ROOT ===============")
            print("subj(s): %s" % get_all_nouns(subj, proper_noun=True))
            obj, relations = nnroot_subj(root)
            print("obj: %s " % obj)

        # Usually the case that the direct obj being non-NNP represents relation
        elif DPHelper.is_verb(root) and obj is not None:
            print("============= NNP SUBJECT with VERB ROOT (NON-NNP DOBJ present) ===============")
            print("subj(s): %s" % get_all_nouns(subj, proper_noun=True))
            objs, aux_relations = vbroot_subj_xobj(root)
            print("objs(s): %s" % objs)
            relations = relations + aux_relations

        # Root verb without concrete noun form but valid relation (E.g. lives, resides) TODO Do we require `in/from etc.` for preposition?
        elif DPHelper.is_verb(root):
            print("============= NNP SUBJECT with VERB ROOT ===============")
            print("subj(s): %s" % get_all_nouns(subj, proper_noun=True))
            objs, aux_relations = vbroot_subj(root)
            relations = relations + aux_relations
            print("objs(s): %s" % objs)

        else:
            print("============= NNP SUBJECT with UNKNOWN STRUCTURE ===============")


    else:
        print("============== NOUN ROOT - No Direct SUBJ and OBJ ================")

        if subj is not None: # Mostly likely noun with possessive or nested
            print("============= NESTED POSSESSIVE OF PASSIVE SUBJECT ===============")
            assert(subj["link"] == Relations.PASSIVE_NOM_SUBJECT) # Necessarily assume this since noun subj is possessive
            subjs = subjpass_poss(subj)
            print("subj(s): %s" % subjs)


        if DPHelper.is_proper_noun(root):
            subj, relations, obj = nnproot(root)
            print("subj: %s" % subj)
            print("obj: %s " % obj)

    print("relation(s): %s" % relations)
