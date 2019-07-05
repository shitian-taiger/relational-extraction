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
             eval("[('Sarah Palin', 'friend', 'Trump')]")),
            ("Yoda and ObiWan were the mentors of Skywalker.",
             eval("[('Yoda', 'mentors', 'Skywalker'), ('ObiWan', 'mentors', 'Skywalker')]")),
            ("Contaldo was a good friend of Jose Calderon",
             eval("[('Contaldo', 'good friend', 'Jose Calderon')]")),
            ("The first six years of Stapledon's and Magaret's life were spent with their parents at Port Tortilla.",
             eval("[]"))
            ]
        for sentence, relations in sentences:
            results = generate(dep_parse.get_tree(sentence))
            self.assertEqual(results, relations)

    def test_rooted_subj_obj(self):
        sentences = [
            ("Federer hired Annacone as his coach.",
             eval("[('Federer', 'coach', 'Annacone')]")),
            ("Federer hired Annacone as his coach and business partner and as a best friend.",
             eval("[('Federer', 'coach', 'Annacone'), ('Federer', 'business partner', 'Annacone'), ('Federer', 'best friend', 'Annacone')]")),
            ("Dmitry started his career in the Russian Drama Theatre of Lithuania in Vilnius.",
             eval("[('Dmitry', 'career', 'Drama Theatre of Lithuania'), ('Dmitry', 'career', 'Vilnius')]")),
            ("Then Dmitry directed opera and drama in many major Russian cities: Moscow, Saint Petersburg, Novosibirsk, Omsk, Samara, Kazan and others.",
             eval("[('Dmitry', 'opera', 'Moscow'), ('Dmitry', 'opera', 'Saint Petersburg'), ('Dmitry', 'opera', 'Novosibirsk'), ('Dmitry', 'opera', 'Omsk'), ('Dmitry', 'opera', 'Samara'), ('Dmitry', 'opera', 'Kazan'), ('Dmitry', 'drama', 'Moscow'), ('Dmitry', 'drama', 'Saint Petersburg'), ('Dmitry', 'drama', 'Novosibirsk'), ('Dmitry', 'drama', 'Omsk'), ('Dmitry', 'drama', 'Samara'), ('Dmitry', 'drama', 'Kazan')]")),
            ]
        for sentence, relations in sentences:
            results = generate(dep_parse.get_tree(sentence))
            self.assertEqual(results, relations)

    def test_vbroot_subj(self):
        sentences = [
            ("Bojack Horseman resides in Hollywoo, California, and worked on Horsing Around.",
             eval("[('Bojack Horseman', 'resides', 'Hollywoo'), ('Bojack Horseman', 'resides', 'California'), ('Bojack Horseman', 'worked', 'Horsing Around')]")),
            ("Annacone coached Federer to win multiple Wimbledon Championships, and in turn became his best friend.",
             eval("[('Federer', 'win', 'Wimbledon Championships')]")),
            ("Harry was born September 4, 1946.",
             eval("[('Harry', 'born', '4 September, 1946')]")),
            ("Harry graduated from Maryville High School, completed his undergraduate work as a Speech and Communication major at Carson Newman College, and got his graduate degree from the University of Tennessee, Knoxville.",
             eval("[('Harry', 'graduated', 'Maryville High School'), ('Harry', 'major', 'Carson Newman College'), ('Harry', 'graduate degree', 'University of Tennessee'), ('Harry', 'graduate degree', 'Knoxville')]")),
            ("Harry retired from law enforcement and was a business employer before pursuing politics.",
             eval("[]")),
            ("After a brief stint as a teacher at Manchester Grammar School, Stapledon worked in shipping offices in Liverpool and Port Tortilla from 1910 to 1913.",
             eval("[('Stapledon', 'teacher', 'Manchester Grammar School'), ('Stapledon', 'worked', 'Port Tortilla'), ('Stapledon', 'worked', 'Liverpool')]"))
            ]
        for sentence, relations in sentences:
            results = generate(dep_parse.get_tree(sentence))
            self.assertEqual(results, relations)

    def test_passive_subj(self):
        sentences = [
            ("Annacone was hired as Federer's coach.",
             eval("[('Annacone', 'coach', 'Federer')]")),
            ("Stapledon was born in Seacombe, Wallasey, on the Wirral Peninsula near Liverpool, the only son of William Clibbert Stapledon and Emmeline Miller.",
             eval("[('Stapledon', 'only son', 'William Clibbert Stapledon'), ('Stapledon', 'only son', 'Emmeline Miller'), ('Stapledon', 'born', 'Seacombe'), ('Stapledon', 'born', 'Wallasey'), ('Stapledon', 'born', 'Wirral Peninsula')]")),
            ("Stapledon was educated at Abbotsholme School and Balliol College, Oxford, where he acquired a BA in Modern History in 1909 and a MA in 1913.",
             eval("[('Stapledon', 'educated', 'Abbotsholme School'), ('Stapledon', 'educated', 'Balliol College')]")),
            ("Dmitry was born in Moscow.",
             eval("[('Dmitry', 'born', 'Moscow')]")),
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



