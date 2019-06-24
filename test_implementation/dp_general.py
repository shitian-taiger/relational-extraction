from constants import Relations, POS
from utils import DPHelper
from typing import Dict, List
from allen_models import DepParse
from dep_parse import *

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

    elif subj == None:
        print("============ Only OBJ present ===============" )

    elif obj == None:
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
            relations = [root["word"]]
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


if __name__ == "__main__":

    dep_parse = DepParse()

    sentences = [
        "Yoda and ObiWan were the mentors of Skywalker.",
        "Contaldo was a good friend of Jose Calderon",
        "Federer hired Annacone as his coach.",
        "Federer hired Annacone as his coach and business partner and as a best friend.",
        "Annacone was hired as Federer's coach.",
        "Hired, was Annacone, as Federer's coach.",
        "Bojack Horseman resides in Hollywoo, California, and works on Detective X.",
        "Annacone coached Federer to win multiple Wimbledon Championships, and in turn became his best friend.", # TODO Handle verbs with concrete form
    ]

    for sentence in sentences:
        root = dep_parse.get_tree(sentence)
        print("\n%s" % sentence)
        generate(root)
