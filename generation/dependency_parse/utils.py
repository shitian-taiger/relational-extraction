from typing import Dict, List

def create_relations(subjs: List[str], relations: List[str], objs: List[str], nested=False):
    """
    Returns list of Dict objects of form {"relation": <>, "subj": [<>], "obj": [<>]}
    """
    relation_dicts = []
    for relation in relations:
        relation_dicts.append({ "subjs": subjs, "relation": relation, "objs": objs})
    return relation_dicts


def create_nested_relations(subjs: List[str], relations: List[str], objs: List[str], nested=False):
    """
    Handle the case where there are multiple pairs of relation_lists to objs, we assume for now subjs have no permutations
    Returns list of Dict objects of form {"relation": <>, "subj": [<>], "obj": [<>]}
    """
    assert(len(relations) == len(objs))

    relation_dicts = []
    for i in range(len(relations)):
        relations_instance = relations[i]
        objs_instance = objs[i]
        relation_dicts = relation_dicts + create_relations(subjs, relations_instance, objs_instance)
    return relation_dicts


