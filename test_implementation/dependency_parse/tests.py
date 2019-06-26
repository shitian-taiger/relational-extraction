import unittest
from .main import generate
from allen_models import DepParse

dep_parse = DepParse()

class TestBasic(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestBasic, self).__init__(*args, **kwargs)

    def test_noun_root(self):
        sentences = [
            ("Sarah Palin is a friend of Trump",
             eval("[{'subjs': ['Sarah Palin'], 'relation': 'friend', 'objs': ['Trump']}]")),
            ("Yoda and ObiWan were the mentors of Skywalker.",
             eval("[{'subjs': ['Yoda', 'ObiWan'], 'relation': 'mentors', 'objs': ['Skywalker']}]")),
            ("Contaldo was a good friend of Jose Calderon",
             eval("[{'subjs': ['Contaldo'], 'relation': 'friend', 'objs': ['Jose Calderon']}]")),
            ("The first six years of Stapledon's and Magaret's life were spent with their parents at Port Tortilla.",
             eval("[]"))
            ]
        for sentence, relations in sentences:
            results = generate(dep_parse.get_tree(sentence))
            self.assertEqual(results, relations)

    def test_rooted_subj_obj(self):
        sentences = [
            ("Federer hired Annacone as his coach.",
             eval("[{'subjs': ['Federer'], 'relation': 'coach', 'objs': ['Annacone']}]")),
            ("Federer hired Annacone as his coach and business partner and as a best friend.",
             eval("[{'subjs': ['Federer'], 'relation': 'coach', 'objs': ['Annacone']}, {'subjs': ['Federer'], 'relation': 'business partner', 'objs': ['Annacone']}, {'subjs': ['Federer'], 'relation': 'best friend', 'objs': ['Annacone']}]")),
            ]
        for sentence, relations in sentences:
            results = generate(dep_parse.get_tree(sentence))
            self.assertEqual(results, relations)

    def test_vbroot_subj(self):
        sentences = [
            ("Bojack Horseman resides in Hollywoo, California, and worked on Horsing Around.",
             eval("[{'subjs': ['Bojack Horseman'], 'relation': 'resides', 'objs': ['Hollywoo', 'California']}, {'subjs': ['Bojack Horseman'], 'relation': 'worked', 'objs': ['Horsing Around']}]")),
            ("Annacone coached Federer to win multiple Wimbledon Championships, and in turn became his best friend.",
             eval("[{'subjs': ['Federer'], 'relation': 'win', 'objs': ['Wimbledon Championships']}]")),
            ("Harry was born September 4, 1946.",
             eval("[{'subjs': ['Harry'], 'relation': 'born', 'objs': ['4 September, 1946']}]")),
            ("Harry graduated from Maryville High School, completed his undergraduate work as a Speech and Communication major at Carson Newman College, and got his graduate degree from the University of Tennessee, Knoxville.",
             eval("[{'subjs': ['Harry'], 'relation': 'graduated', 'objs': ['Maryville High School']}, {'subjs': ['Harry'], 'relation': 'major', 'objs': ['Carson Newman College']}, {'subjs': ['Harry'], 'relation': 'graduate degree', 'objs': ['University of Tennessee', 'Knoxville']}]")),
            ("Harry retired from law enforcement and was a business employer before pursuing politics.",
             eval("[]")),
            ("After a brief stint as a teacher at Manchester Grammar School, Stapledon worked in shipping offices in Liverpool and Port Tortilla from 1910 to 1913.",
             eval("[{'subjs': ['Stapledon'], 'relation': 'worked', 'objs': ['Port Tortilla', 'Liverpool']}]"))
            ]
        for sentence, relations in sentences:
            results = generate(dep_parse.get_tree(sentence))
            self.assertEqual(results, relations)

    def test_passive_subj(self):
        sentences = [
            ("Annacone was hired as Federer's coach.",
             eval("[{'subjs': ['Annacone'], 'relation': 'coach', 'objs': ['Federer']}]")),
            ("Stapledon was born in Seacombe, Wallasey, on the Wirral Peninsula near Liverpool, the only son of William Clibbert Stapledon and Emmeline Miller.",
             eval("[{'subjs': ['Stapledon'], 'relation': 'only son', 'objs': ['William Clibbert Stapledon', 'Emmeline Miller']}, {'subjs': ['Stapledon'], 'relation': 'born', 'objs': ['Seacombe', 'Wallasey', 'Peninsula near Liverpool']}]")),
            ("Stapledon was educated at Abbotsholme School and Balliol College, Oxford, where he acquired a BA in Modern History in 1909 and a MA in 1913.",
             eval("[{'subjs': ['Stapledon'], 'relation': 'educated', 'objs': ['Abbotsholme School', 'Balliol College']}]")),
            ("Dmitry was born in Moscow.",
             eval("[{'subjs': ['Dmitry'], 'relation': 'born', 'objs': ['Moscow']}]")),
            ]
        for sentence, relations in sentences:
            results = generate(dep_parse.get_tree(sentence))
            self.assertEqual(results, relations)

    def test_unknown(self):
        sentences = [
            ("Harry is married to Mary and has two children.",
             eval("[]")
             )
            ]
        for sentence, relations in sentences:
            results = generate(dep_parse.get_tree(sentence))
            self.assertEqual(results, relations)



