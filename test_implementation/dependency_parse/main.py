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

    if subj == None and obj == None:
        print("============== NOUN ROOT - No SUBJ and OBJ ================")
        if DPHelper.is_proper_noun(root):
            subj, relations, obj = nnproot(root)
            print("subj: %s" % subj)
            print("obj: %s " % obj)

    elif obj == None:

        # Check for clausal complement for Subj (INDEPENDENT)
        if DPHelper.get_child_type(root, Relations.CLAUSAL_COMPLEMENT):
            pass

        # Passive subject, look into preposition for predicate object with possessive
        if DPHelper.is_proper_noun(subj) and subj["link"] == Relations.PASSIVE_NOM_SUBJECT:
            print("============= PASSIVE SUBJECT ===============")
            print("subj(s): %s" % get_all_proper_nouns(subj))
            obj, relations = subjpass(root)
            print("obj: %s " % obj)

        # Possible case where root is noun and hence subject is not labeled passive but relation still exists
        elif DPHelper.is_noun(root):
            print("============= SUBJECT with NOUN ROOT ===============")
            print("subj(s): %s" % get_all_proper_nouns(subj))
            obj, relations = nnroot_subj(root)
            print("obj: %s " % obj)

        # Special cases, root verb without concrete noun form but valid relation (E.g. lives, resides) TODO Do we require `in` for prep?
        elif DPHelper.is_verb(root):
            print("============= SUBJECT with VERB ROOT (spe.) ===============")
            print("subj(s): %s" % get_all_proper_nouns(subj))
            objs, aux_relations = vbroot_subj(root)
            relations = relations + aux_relations
            print("objs(s): %s" % objs)

    else:
        # Simplest case: NE subject and object
        if DPHelper.is_proper_noun(subj) and DPHelper.is_proper_noun(obj):
            print("============ Rooted SUBJECT and OBJECT =============")
            print("subj(s): %s" % get_all_proper_nouns(subj))
            print("obj: %s" % obj["word"])
            relations = sub_obj_vbroot(root) # Relations between subject and object
            print("relations %s" % relations)

            # Relations within clausal complements
            open_comp: List[Dict] = DPHelper.get_child_type(root, Relations.OPEN_CLAUSAL_COMPLEMENT)
            comp: List[Dict] = DPHelper.get_child_type(root, Relations.CLAUSAL_COMPLEMENT)
            if open_comp: # Assume for now open_comps all relate to object
                print("================= Open Clausal Complement =================")
                print("subj: %s" % obj["word"])
                objs, xcomp_relations = x_comp(open_comp[0]) # TODO Can there be multiple xcomps?
                print("objs: %s" % objs)
                print("xcomp_relations %s" % xcomp_relations)

            return

    print("relation(s): %s" % relations)
