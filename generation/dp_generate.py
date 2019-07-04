import logging
import unittest
from allen_models import DepParse
from dependency_parse.main import generate
import dependency_parse.tests

sentences = [
    "Sarah Palin is a friend of Trump",
    "Yoda and ObiWan were the mentors of Skywalker.",
    "Contaldo was a good friend of Jose Calderon",
    "Federer hired Annacone as his coach.",
    "Federer hired Annacone as his coach and business partner and as a best friend.",
    "Annacone was hired as Federer's coach.",
    "Hired, was Annacone, as Federer's coach.",
    "Bojack Horseman resides in Hollywoo, California, and worked on Horsing Around.",
    "Annacone coached Federer to win multiple Wimbledon Championships, and in turn became his best friend.", # TODO Handle verbs with concrete form
    "Harry was born September 4, 1946.",
    "Harry graduated from Maryville High School, completed his undergraduate work as a Speech and Communication major at Carson Newman College, and got his graduate degree from the University of Tennessee, Knoxville.",
    "Harry is married to Mary and has two children.", # TODO Relation (verbal) -- see Concrete Nouns (Notes.org)
    "Stapledon was born in Seacombe, Wallasey, on the Wirral Peninsula near Liverpool, the only son of William Clibbert Stapledon and Emmeline Miller.",
    "The first six years of Stapledon's and Magaret's life were spent with their parents at Port Tortilla.", # TODO Complex relation representation
    "Stapledon was educated at Abbotsholme School and Balliol College, Oxford, where he acquired a BA in Modern History in 1909 and a MA in 1913.",
    "After a brief stint as a teacher at Manchester Grammar School, Stapledon worked in shipping offices in Liverpool and Port Tortilla from 1910 to 1913.",
    "Dmitry was born in Moscow.",
    "In 1993 Dmitry graduated from Russian Academy of Theatre Arts as stage director.", # TODO (Special x-y)
    "Dmitry started his career in the Russian Drama Theatre of Lithuania in Vilnius.",
    "Then Dmitry directed opera and drama in many major Russian cities: Moscow, Saint Petersburg, Novosibirsk, Omsk, Samara, Kazan and others.",
]

# Move test sentence unit test and move to sentences once complete
test_sentences = [
    "Peckham was born in Albany, New York, to Rufus Wheeler Peckham and Isabella Adeline; his mother died when he was only nine.", # TODO (Special x-y)
    "Following his graduation from The Albany Academy, Peckham followed in his father's footsteps as a lawyer, being admitted to the bar in Albany in 1859 after teaching himself law by studying in his father's office.",
    "After a decade of private practice, Peckham served as the Albany district attorney from 1869 to 1872.",
    "Peckham then returned to private legal practice and served as counsel to the City of Albany, until being elected as a trial judge on the New York Supreme Court in 1883.", # TODO (Special x-y)
    "In 1886, Peckham was elected to the New York Court of Appeals, the highest court in the state.",
    "This was the third position that Peckham had held after his father, who had also served as the Albany D.A., on the New York Supreme Court, and finally on the Court of Appeals until his death in the 1873 Ville du Havre sinking.",
    "Lillian Lux died at St. Vincent 's hospital in Manhattan.",
    "Lillian Lux, the Matriarch of YiThFa, a celebrated yiddish theatrical family, died on saturday at St. Vincent's hospital in Manhattan."
    ]


logging.basicConfig(level=logging.INFO) # Defaults to WARN, enable only here
if __name__ == "__main__":

    suite = unittest.TestLoader().loadTestsFromModule(dependency_parse.tests)
    unittest.TextTestRunner(verbosity=2).run(suite)

    dep_parse = DepParse()

    for sentence in test_sentences:
        root = dep_parse.get_tree(sentence)
        print("\n%s" % sentence)
        results = generate(root)
        print(results)



