import sys
sys.path.insert(0, "/Users/shitian/Github/allennlp")

from constants import Relations, POS
from utils import DPHelper
from typing import Dict, List
from allen_models import DepParse

# ============================================== CASES =============================================

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
    for prep in DPHelper.get_child_type(root, Relations.PREPOSITION):
        pred_objs = DPHelper.get_child_type(prep, Relations.PREDICATE_OBJECT)
        assert(len(pred_objs) == 1) # TODO Similar to above, refactor
        obj = None # Actual Named entity to find
        pred_obj = pred_objs[0]

        if DPHelper.has_possession_by(pred_obj) and \
           DPHelper.is_proper_noun(DPHelper.get_possessor(pred_obj)): # Possessive should be named entity
            obj = DPHelper.get_possessor(pred_obj)["word"]
            relations = relations + get_all_nouns(pred_obj)
        else:
            continue
    return obj, relations


def nnroot_subj(root: Dict):
    '''
    Noun root with only nominal subject, find entity in prepositions

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



def nnp_root(root: Dict):
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


# ========================================= DRIVER =================================================

def generate(root: Dict):
    # Is this applicable only to root?
    subj = DPHelper.get_subject(root)
    obj = DPHelper.get_object(root)
    relations = []

    if subj == None and obj == None:
        print("============== No direct SUBJ and OBJ ================")
        if DPHelper.is_proper_noun(root):
            subj, relations, obj = nnp_root(root)
            print("subj (passive): %s" % subj)
            print("obj (active): %s " % obj)
    elif subj == None:
        print("============ Only OBJ present ===============" )
    elif obj == None:
        print("============= Only SUBJ present ===============")
        # Passive subject, look into preposition for predicate object with possessive
        if DPHelper.is_proper_noun(subj) and subj["link"] == Relations.PASSIVE_NOM_SUBJECT:
            print("subj (passive): %s" % subj["word"])
            obj, relations = subjpass(root)
            print("obj (active): %s " % obj)

        # Possible case where root is noun and hence subject is not labeled passive but relation still exists
        elif DPHelper.is_noun(root) and DPHelper.is_proper_noun(subj):
            print("subj (passive): %s" % subj["word"])
            obj, relations = nnroot_subj(root)
            print("obj (active): %s " % obj)
    else:
        print("============ SUBJ and OBJ present =============")
        # Simplest case: NE subject and object
        if DPHelper.is_proper_noun(subj) and DPHelper.is_proper_noun(obj):
            print("subj: %s" % subj["word"])
            print("obj: %s" % obj["word"])
            relations = sub_obj_vbroot(root) # Relations between subject and object
            print("relations %s" % relations)

            # Relations within clausal complements
            open_comp: List[Dict] = DPHelper.get_child_type(root, Relations.OPEN_CLAUSAL_COMPLEMENT)
            comp: List[Dict] = DPHelper.get_child_type(root, Relations.CLAUSAL_COMPLEMENT)
            if open_comp: # Assume for now open_comps all relate to object
                print("subj: %s" % obj["word"])
                objs, xcomp_relations = x_comp(open_comp[0]) # TODO Can there be multiple xcomps?
                print("objs: %s" % objs)
                print("xcomp_relations %s" % xcomp_relations)

            return

    print("relations %s" % relations)

# ========================================= HELPERS =================================================

def get_all_nouns(noun: Dict) -> List[str]:
    # Finds all noun phrases with given word as root, also look for conjunctions
    nouns = []
    nouns.append(get_noun_phrase(noun))
    for conj in DPHelper.get_child_type(noun, Relations.CONJUNCTION): # Conjuncting predicate objects are also relations
        nouns.append(get_noun_phrase(conj))
    return nouns

def get_all_proper_nouns(noun: Dict) -> List[str]:
    # Finds all proper noun phrases with given word as root, also look for conjunctions
    proper_nouns = []
    proper_nouns.append(get_noun_phrase(noun)) # Assume root noun is proper noun
    for conj in DPHelper.get_child_type(noun, Relations.CONJUNCTION): # Conjuncting predicate objects are also relations
        if DPHelper.is_proper_noun:
            proper_nouns.append(get_noun_phrase(conj))
    return proper_nouns


def get_noun_phrase(noun: Dict) -> str:
    # Given a noun, include all ADJMOD and NN to get full noun phrase
    if not noun.get("children"):
        return noun["word"]
    else:
        full = ""
        for child in noun["children"]:
            if not DPHelper.is_leaf(child):
                continue
            elif child["link"] == Relations.ADJECTIVAL_MODIFIER:
                full = child["word"] # FIXME Assume singular adjectival modifiers for now
            elif child["link"] == Relations.NOUN:
                full = " ".join([full, child["word"]])
            else:
                continue
        return "".join([full, noun["word"]]) if not full else " ".join([full, noun["word"]])


if __name__ == "__main__":

    dep_parse = DepParse()

    sentences = [
        "Contaldo was a good friend of Jose Calderon",
        "Federer hired Annacone as his coach.",
        "Federer hired Annacone as his coach and business partner and as a permanent friend.",
        "Annacone was hired as Federer's coach.",
        "Hired, was Annacone, as Federer's coach.",
        "Annacone coached Federer to win multiple Wimbledon Championships, and became his best friend."
    ]

    for sentence in sentences:
        root = dep_parse.get_tree(sentence)
        print("\n%s" % sentence)
        generate(root)
