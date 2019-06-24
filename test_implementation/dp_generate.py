from allen_models import DepParse
from dependency_parse.main import generate




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
    "Harry was born September 4, 1946.",
    "Harry graduated from Maryville High School, completed his undergraduate work as a Speech and Communication major at Carson Newman College, and got his graduate degree from the University of Tennessee, Knoxville.",
    "Harry is married to Mary and has two children.",
    "Harry retired from law enforcement and was a business employer before pursuing politics.",
    "Stapledon was born in Seacombe, Wallasey, on the Wirral Peninsula near Liverpool, the only son of William Clibbert Stapledon and Emmeline Miller.",
    "The first six years of Stapledon's life were spent with his parents at Port Said.",
    "Stapledon was educated at Abbotsholme School and Balliol College, Oxford, where he acquired a BA in Modern History in 1909 and a MA in 1913.",
    "After a brief stint as a teacher at Manchester Grammar School, Stapledon worked in shipping offices in Liverpool and Port Said from 1910 to 1913.",
]

for sentence in sentences:
    root = dep_parse.get_tree(sentence)
    print("\n%s" % sentence)
    generate(root)

