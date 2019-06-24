
class Relations:
    # words links
    APPOSITION = "appos"
    CLAUSAL_SUBJECT = "csubj"
    OPEN_CLAUSAL_COMPLEMENT = "xcomp"
    CLAUSAL_COMPLEMENT = "ccomp"
    CONJUNCTION = "conj"
    DIRECT_OBJECT = "dobj"
    INDIRECT_OBJECT = "iobj"
    NOMINAL_SUBJECT = "nsubj"
    NOUN = "nn" # noun as part of noun object group
    PASSIVE_NOM_SUBJECT = "nsubjpass"
    POSSESSION_BY = "poss"
    PREPOSITION = "prep"
    PREDICATE_OBJECT = "pobj"
    PUNCTUATION = "punct"
    ADJECTIVAL_MODIFIER = "amod"

class POS:
    PROPER_NOUN = "NNP"
    NOUN = "NN"
    NOUN_PLURAL = "NNS"
    VERB_BASE = "VB"
    VERB_PAST = "VBD"
    VERB_GERUND = "VBG" # Pseudo nouns
    VERB_PAST_PARTICIPLE = "VBN"
    VERB_3SP = "VBZ" # 3rd person singular present
    VERB_NON_3SP = "VBP"
