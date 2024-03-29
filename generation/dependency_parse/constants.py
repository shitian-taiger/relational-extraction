class Relations:
    # words links
    ADJECTIVAL_MODIFIER = "amod"
    APPOSITION = "appos"
    CLAUSAL_SUBJECT = "csubj"
    CLAUSAL_COMPLEMENT = "ccomp"
    CONJUNCTION = "conj"
    DIRECT_OBJECT = "dobj"
    INDIRECT_OBJECT = "iobj"
    NOMINAL_SUBJECT = "nsubj"
    NOUN = "nn" # noun as part of noun object group
    NUMERAL = "num"
    TEMPORAL_MODIFIER = "tmod"
    OPEN_CLAUSAL_COMPLEMENT = "xcomp"
    PASSIVE_NOM_SUBJECT = "nsubjpass"
    POSSESSIVE = "possessive"
    POSSESSION_BY = "poss"
    PREPOSITION = "prep"
    PREPOSITIONAL_COMP = "pcomp"
    PREDICATE_OBJECT = "pobj"
    PUNCTUATION = "punct"
    RELATIVE_CLAUSE_MODIFIER = "rcmod"
    UNKNOWN_DEPENDENCY = "dep"

class POS:
    ADJECTIVE = "JJ"
    CARDINAL_NUMBER = "CD"
    NOUN = "NN"
    NOUN_PLURAL = "NNS"
    PROPER_NOUN = "NNP"
    VERB_BASE = "VB"
    VERB_PAST = "VBD"
    VERB_GERUND = "VBG" # Pseudo nouns
    VERB_PAST_PARTICIPLE = "VBN"
    VERB_3SP = "VBZ" # 3rd person singular present
    VERB_NON_3SP = "VBP"
    WH_PRONOUN = "WP"
