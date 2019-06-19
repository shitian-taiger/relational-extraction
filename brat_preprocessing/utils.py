from enum import IntEnum
from typing import List, Dict, Tuple

class Dim_Index(IntEnum):
    batch = 0
    sequence_length = 1
    feature = 2

class LSTM_Direction(IntEnum):
    forward = 0
    backward = 1


class AnnHeader(IntEnum):
    row_type = 0
    desc = 1
    entity = 2

class BRATHelper:

    def __init__(self):
        return

    @staticmethod
    def print_bounds(text: str, arg_bounds: List):
        print(text[arg_bounds[0]:arg_bounds[1]])

    @staticmethod
    def get_ent_bounds(arg: Dict):
        bounds = [int(x) for x in arg["bounds"]]
        return (bounds[0], bounds[1])

    @staticmethod
    def get_sent_bounds(sent_stops: List, min_bound: int, max_bound: int):
        sent_min = 0
        sent_max = sent_stops[-1]
        prev_stop = 0
        min_reached = False

        for stop in sent_stops:
            if min_reached: # Bounds not within a single sentence
                if max_bound < stop:
                    sent_max = stop
                    break
            elif min_bound > stop: # Store prev stop for later if min not reached
                prev_stop = stop
            else: # Min bound reached in prev stop
                sent_min = prev_stop
                min_reached = True
                if max_bound < stop: # Max bound might have been reached at this point (within 1 sentence)
                    sent_max = stop
                    break
        return sent_min + 1, sent_max # sentence index is end, min + 1


    @staticmethod
    def get_arg_indexes(text: str, arg_bounds: List, sent_bounds: Tuple):
        sentence = text[sent_bounds[0] : sent_bounds[1]]
        words = text[arg_bounds[0] : arg_bounds[1]]
        sent_len = len([word for word in sentence.split(" ")])
        words_before = text[sent_bounds[0] : arg_bounds[0]]
        word_index_lower = len(words_before.split(" ")) - 1 # Extra space prior or default 1 for split on ""
        word_index_upper = word_index_lower + len(words.split(" ")) # As above but taken care of in range func below
        return [i for i in range(word_index_lower, word_index_upper)]


    @staticmethod
    def add_tagged_word(curr: str, index: int, word: str, pred: str, tag: str):
        line: str = "\t".join([str(index), word, pred, tag])
        return "\n".join([curr, line])


    @staticmethod
    def get_tagged_sentence(text: str, rel: Tuple[Dict], sentence_bounds: Tuple[int]):
        ent1, relation, ent2 = rel
        sent_min, sent_max = sentence_bounds
        ent1_bounds: List = BRATHelper.get_ent_bounds(ent1)
        rel_bounds: List = BRATHelper.get_ent_bounds(relation)
        ent2_bounds: List = BRATHelper.get_ent_bounds(ent2)

        # TODO Is this necessary?
        # assert(ent1_bounds[1] < rel_bounds[0] and rel_bounds[1] < ent2_bounds[0])

        ent1_indexes: List = BRATHelper.get_arg_indexes(text, ent1_bounds, sentence_bounds)
        rel_indexes: List = BRATHelper.get_arg_indexes(text, rel_bounds, sentence_bounds)
        ent2_indexes: List = BRATHelper.get_arg_indexes(text, ent2_bounds, sentence_bounds)

        # FIXME Hacky implementation pls refactor
        # TODO Is there a need for differentiation of Arg1 from Arg2
        tagged: str = ""
        split_sentence = text[sent_min:sent_max].split(" ")
        i = 0
        pred = " ".join([split_sentence[i] for i in rel_indexes])
        while(True):
            if i in ent1_indexes: # Arg1
                tagged = BRATHelper.add_tagged_word(tagged, i, split_sentence[i], pred, "B-ARG1")
                i += 1
                for j in range(len(ent1_indexes) - 1):
                    tagged = BRATHelper.add_tagged_word(tagged, i, split_sentence[i], pred, "I-ARG1")
                    i += 1
            elif i in rel_indexes: # P
                tagged = BRATHelper.add_tagged_word(tagged, i, split_sentence[i], pred, "B-P")
                i += 1
                for j in range(len(rel_indexes) - 1):
                    tagged = BRATHelper.add_tagged_word(tagged, i, split_sentence[i], pred, "I-P")
                    i += 1
            elif i in ent2_indexes: # Arg2
                tagged = BRATHelper.add_tagged_word(tagged, i, split_sentence[i], pred, "B-ARG2")
                i += 1
                for j in range(len(ent2_indexes) - 1):
                    tagged = BRATHelper.add_tagged_word(tagged, i, split_sentence[i], pred, "I-ARG2")
                    i += 1
            elif i < len(split_sentence): # O
                tagged = BRATHelper.add_tagged_word(tagged, i, split_sentence[i], pred, "O")
                i += 1
            else:
                break

        return(tagged)


    @staticmethod
    def get_tagged_sentences(text: str, rels: List[Tuple], sentence_bounds: List):
        assert(len(rels) == len(sentence_bounds)) # Number of sentence bounds must matches number of rel pairs
        tagged_sentences = ""
        for i in range(len(rels)):
            tagged_sentence = BRATHelper.get_tagged_sentence(text, rels[i], sentence_bounds[i])
            tagged_sentences = "\n".join([tagged_sentences, tagged_sentence])
        return tagged_sentences




