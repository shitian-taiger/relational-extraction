import sqlite3
import json
from pathlib import Path
from spacy.lang.en import English

SENTENCE_TABLE = "Sentence"

def quote_string(txt: str):
    return "\"" + txt + "\""

def process_file(file_path: str):

    nlp = English() # Sentencizer
    nlp.add_pipe(nlp.create_pipe('sentencizer'))

    # Connection to database
    db_file_path = Path.joinpath(Path(__file__).parent, "store.db")
    connection = sqlite3.connect(str(db_file_path))
    cursor = connection.cursor()

    # Create table if not created
    # INTEGER Representation of Boolean value processed: true(0), false(1)
    cursor.execute('create table if not exists {} (sentence TEXT, valid_keys STRING, invalid_keys STRING, processed INTEGER, UNIQUE(sentence))'
                   .format(SENTENCE_TABLE))

    with open(file_path, "r") as data_file:
        num_lines_processed = 0
        for line in data_file:
            try:
                num_lines_processed += 1
                paragraph = json.loads(line)["evidences"][0]["snippet"]
                # TODO Only add in the first sentence for now considering these contain
                # the name of the subject of the paragraph. Coreference Resolve before
                # adding in all sentences
                sentence = next(nlp(paragraph).sents).text
            except:
                # Certain escape characters, ignore these paragraphs
                continue

            # Duplicated sentences do exist, REPLACE handles these
            cursor.execute("INSERT OR REPLACE INTO {} ({}, {}, {}, {}) VALUES ({}, {}, {}, {})"
                        .format(SENTENCE_TABLE,
                                "sentence", "valid_keys", "invalid_keys", "processed",
                                quote_string(sentence),
                                quote_string(",".join([])), # No instances validated yet
                                quote_string(",".join([])),
                                0 # Signify unprocessed sentence
                                )
                            )
    # Due to the format of GoogleTagged sentences, highly unlikely for sentences
    # beginning with subject pronouns to contain Named Entities
    cursor.execute("DELETE FROM Sentence WHERE SUBSTR(sentence, 1, 2) = 'He' OR SUBSTR(sentence, 1, 3) = 'She'
    OR SUBSTR(sentence, 1, 3) = 'His' OR SUBSTR(sentence, 1, 3) = 'Her'")

    connection.commit()
    connection.close()

    return num_lines_processed


if __name__ == "__main__":

    root = Path(__file__).parent.resolve()
    google_tagged_dir = Path.joinpath(root, "RE/GoogleTagged")

    num_paragraphs_processed = 0
    for data_file in google_tagged_dir.iterdir():
        data_file_path = Path.joinpath(root, data_file)
        num_paragraphs_processed += process_file(data_file_path)
        print("Finished processing: {}".format(data_file))

    print(num_paragraphs_processed)


