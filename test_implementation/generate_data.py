from utils import get_sentences
from typing import Tuple, List, Iterator, Dict
from ner import NER
from oie import OpenIE
import spacy

PRINT_SENTENCE = True # Only print for questioning sentence validity
PRINT_NAMED_ENTITIES = False
TEST_SENTENCE = False

class DataGenerator:

    def __init__(self, use_allen=True, use_spacy=False):
        self.use_spacy = use_spacy
        self.use_allen = use_allen
        if use_spacy:
            self.spacy_nlp = spacy.load("en_core_web_sm")
        if use_allen:
            self.ner = NER() # Load NER model from allen

        self.open_ie = OpenIE() # Load SupervisedOIE model from allen
        self.ent_tagged_sent: List[Dict] = []
        self.entities: List[str] = []
        self.ent_idx_map: List[int] = []
        self.sentence = ""


    def generate(self, sentence: str):
        """ Generate BIO tagged instance for a sentence

        Args:
            sentence: Raw sentence string
        Returns:
            void: Writes directly to file
        """
        self.sentence = sentence
        self.ent_tagged_sent, self.entities, self.ent_idx_map = self.get_tagged_entities(sentence)
        if not (list(filter(lambda word: word["ent_type"] is not None, self.ent_tagged_sent))): # If no named entities, skip
            # print("No named entities in sentence")
            return ""

        oie_tuples = self.filter_oie_tuples(self.open_ie.get_tuples(sentence)) # Get relational tuples from oie extractor, filtered conditionally

        concat_instances = ""
        for rel_tuple in oie_tuples:
            arg1, arg2 = rel_tuple[0], rel_tuple[2]
            if self.contains_named_entity(arg1) and self.contains_named_entity(arg2):
                instances = self.create_instances(rel_tuple)
                concat_instances = "\n".join([concat_instances, instances])

        return concat_instances


    def filter_oie_tuples(self, tuples: List[Tuple]):
        mask = lambda t: not t[1] == "is"
        return list(filter(mask, tuples))

    def get_tagged_entities(self, sentence: str):
        """ Retrieves NER tagged entities and tags the given sentence accordingly
        - Tokenization of sentence is basic and does not remove punctuation
        - Spacy
            -- Get noun chunks to consolidate named entities
            -- Create mapping of named entity to index range within tokenized sentence
        - Allen
            -- Handled in NER Class

        Args:
            sentence: Raw string
        Returns:
            words (List[Dict]): Tokenized sentence containing entity type
            entities (List[str]): Consolidated named entities
            ent_idx_map (Dict<str, Tuple>): Mapping of entity to start and end index within tokenized sentence
        """

        if self.use_spacy:
            doc = self.spacy_nlp(sentence)
            words : List[Dict] = [ {"text": token.text,
                    "ent_type": token.ent_type_ if not token.ent_type_ == "" else None,
                    } for token in doc ]
            noun_chunks = [(ent.start, ent.end - 1) for ent in doc.noun_chunks]

            named_ents = []
            for chunk in noun_chunks: # Consolidate entity tags to named entity chunks
                if words[chunk[0]]["ent_type"] is not None:
                    named_ents.append(chunk)
                elif words[chunk[0]]["text"].lower() == "the": # Allow first word of named entity chunk to be 'the'
                    if words[chunk[1]]["ent_type"] is not None:
                        named_ents.append(chunk)
            entities: List[str] = [] # String entities
            ent_idx_map: Dict = {} # Entity index corresponding to entities
            for named_ent in (named_ents):
                start, end = named_ent[0], named_ent[1]

                entity = " ".join([words[i]["text"] for i in range(start, end + 1)])
                entities.append(entity)
                ent_idx_map[entity] = (start, end)

        elif self.use_allen:
            words : List[Dict] = self.ner.get_tagged_tokens(sentence)
            entities, ent_idx_map = self.ner.get_entities(words)

        else:
            raise Exception("Unable to obtain NE tags -- Please specify allen or spacy")


        if PRINT_NAMED_ENTITIES:
            print("=============== Named Entities ===================")
            for word in words:
                print(word["text"], word["ent_type"])


        return words, entities, ent_idx_map


    def create_instances(self, rel_tuple: Tuple):
        """ Create BIO tagged instances given a relationship tuple

        Args:
            rel_tuple: Tuple of (sub, rel, obj, verb_index)
        Returns:
            instances (str): Formatted instances in string format
        """
        instances = ""
        sub, obj, rel_idx = rel_tuple[0], rel_tuple[2], rel_tuple[3]

        assert(rel_idx is not None) # Ensure relation index exists for tagging purposes

        sub_idxs, obj_idxs = [], [] # Possibility of multiple named entities in both sub and obj relational groups
        for entity in self.entities:
            if entity in sub:
                sub_idxs.append(self.ent_idx_map[entity])
            elif entity in obj:
                obj_idxs.append(self.ent_idx_map[entity])

        for sub_idx in sub_idxs:
            for obj_idx in obj_idxs:

                '''
                Printing of relational tuple
                '''
                sub = [self.ent_tagged_sent[i]["text"] for i in range(sub_idx[0], sub_idx[1] + 1)]
                rel = self.ent_tagged_sent[rel_idx]["text"]
                obj = [self.ent_tagged_sent[i]["text"] for i in range(obj_idx[0], obj_idx[1] + 1)]

                '''
                Manual user input
                '''
                if PRINT_SENTENCE:
                    print(" ===================== POTENTIAL INSTANCE =========================")
                    print(self.sentence)
                dec = False
                while not dec:
                    tag = input("Valid? - [y/n]: %s - %s - %s" % (sub, rel, obj))
                    if tag == "y":
                        print("Adding to instances")
                        instances = "\n".join([instances, self.tag_sentence(sub_idx, obj_idx, rel_idx)])
                        dec = True
                    elif tag == "n":
                        print("Skipping")
                        dec = True
                    else:
                        print("Invalid option")

        return instances


    def tag_sentence(self, sub_idx: Tuple, obj_idx: Tuple, rel_idx):
        """ BIO tagging of sentence given subject, relation, object

        Returns:
            tagged (str): Formatted BIO tagged instance
        """
        tagged = ""
        relation = self.ent_tagged_sent[rel_idx]["text"] # Limited to verbs
        for i in range(len(self.ent_tagged_sent)):
            tag = "O"
            token = self.ent_tagged_sent[i]
            word = token["text"]
            if (i in range(sub_idx[0], sub_idx[1] + 1)):
                tag = "B-ARG1" if i == sub_idx[0] else "I-ARG1"
            elif (i in range(obj_idx[0], obj_idx[1] + 1)):
                tag = "B-ARG2" if i == obj_idx[0] else "I-ARG2"
            elif (i == rel_idx):
                tag = "B-V"
            tagged_word = " ".join([word, tag])
            tagged = "\n".join([tagged, tagged_word])

        return tagged


    def contains_named_entity(self, arg: str) -> bool:
        # Whether any entities are contained within an arg phrase from OIE
        for entity in self.entities:
            if entity in arg:
                return True
        return False


if __name__ == "__main__":
    generator = DataGenerator(use_allen = True)


    if TEST_SENTENCE:
        sentences = ["Lillian lux, the matriarch of a celebrated yiddish theatrical family who performed for decades as an actress and singer in New York and around the world, died on saturday at St. Vincent's hospital in Manhattan.",
                    "Courtalds' spinoff reflects pressure on British industry to boost share prices beyond the reach of corporate raiders.",
                    "In 1971 , the FDA banned the use of Amphetamines after studies linked it to cancer and other problems in daughters of women who took the drug.",
                    "Deva has moved to Mumbai and has is residing at Boney Kapoor's old place called Green Acres.",
                     "In London, prices finished at intraday peaks, comforted by a reassuring early performance on Wall Street and news that the British government will waive its `` golden share'' in auto maker Jaguar."
                    ]
        sentence = sentences[4]
        generator.generate(sentence)

    if not TEST_SENTENCE:
        with open("./generated.txt", "a+") as f:
            for sentence in get_sentences("../data/OIE/train.oie.conll"):
                instance = generator.generate(sentence)
                if not instance == "":
                    f.write(instance)
                else:
                    print("No extracted NE relation pairs")
                    continue
