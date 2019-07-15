import random
import pandas as pd
from flask_cors import CORS
from flask import Flask, request, jsonify, send_file
from pathlib import Path

# Model
from test_implementation.trainer import Trainer
from test_implementation.main import model_config, training_config

# Instance generation
from generation.allen_models import DepParse
from generation.allen_models import OpenIE
from generation.dependency_parse.main import generate
from generation.oie_generate import DataGenerator

# Database
import sqlite3

app = Flask(__name__)
CORS(app)

model_trainer = Trainer(model_config, training_config)
oie_generator = OpenIE()
dependency_parser = DepParse()
ner_oie_generator = DataGenerator(use_allen = True)

# TODO Refactor: Move constants
SENTENCE_TABLE = "Sentence"
VALID_INSTANCES_TABLE = "PositiveInstance"
INVALID_INSTANCES_TABLE = "NegativeInstance"

def quote_string(txt: str):
    return "\"" + txt + "\""

@app.route('/db_download', methods=['GET'])
def download_db():
    # Allow error stacktrace here, handle in frontend
    root = Path(__file__).parent.resolve()
    print(Path.joinpath(root, "data/store.db"))
    return send_file(str(Path.joinpath(root, "data/store.db")), cache_timeout=0)


@app.route('/get_sentence', methods=['GET'])
def get_sentence():
    # Get from database a random sentence which is not yet processed
    connection = sqlite3.connect('./data/store.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM {} WHERE processed=0 AND length(sentence)<250 and skip=0 LIMIT 15'.format(SENTENCE_TABLE))
    sentence_rows = cursor.fetchall()
    sentence = random.choice(sentence_rows)[0] if sentence_rows else ""
    return jsonify({
        "sentence": sentence
    });


# We allow a sentence to be marked as skipped due to ambiguity or lack of Named Entity
@app.route('/skip_sentence', methods=['POST'])
def skip_sentence():
    data = request.get_json(force=True)
    sentence = data["sentence"]
    # Set sentence as skipped
    connection = sqlite3.connect('./data/store.db')
    cursor = connection.cursor()
    cursor.execute("UPDATE {} SET skip=1 WHERE sentence={}".format(SENTENCE_TABLE, quote_string(sentence)))
    return jsonify({
        "message": "Set skipped on sentence".format(sentence)
    });


@app.route('/predict/all', methods=['POST'])
def predict_oie():
    data = request.get_json(force=True)
    sentence = data["sentence"]

    oie_prediction = oie_generator.get_tuples(sentence)
    dp_prediction = generate(dependency_parser.get_tree(sentence)) # Get tree from dependency parse first
    instance, ner_oie_prediction = ner_oie_generator.generate(sentence)
    return jsonify({
        "oie_prediction": oie_prediction,
        "dp_prediction": dp_prediction,
        "ner_oie_prediction": ner_oie_prediction
        })


@app.route('/addinstances', methods=['POST'])
def add_instances():
    data = request.get_json(force=True)
    sentence = data["sentence"]
    valid_instances, invalid_instances = data["validInstances"], data["invalidInstances"]

    connection = sqlite3.connect('./data/store.db')
    cursor = connection.cursor()
    # Create tables if they don't yet exist
    # Arrays are not supported in SQLite3, map string keys to integer primary keys in corresponding tables
    cursor.execute('CREATE TABLE IF NOT EXISTS {} (sentence TEXT, valid_keys STRING, invalid_keys STRING, processed INTEGER, UNIQUE(sentence))'
                   .format(SENTENCE_TABLE))
    cursor.execute('CREATE TABLE IF NOT EXISTS {} (entity1 TEXT, rel TEXT, entity2 TEXT)'
                   .format(VALID_INSTANCES_TABLE))
    cursor.execute('CREATE TABLE IF NOT EXISTS {} (entity1 TEXT, rel TEXT, entity2 TEXT)'
                   .format(INVALID_INSTANCES_TABLE))

    # Store primary keys of instances to store in sentence table
    valid_instance_keys = []
    invalid_instance_keys = []

    # Check if sentence already exists in table
    cursor.execute("SELECT * FROM {} WHERE sentence={}".format(SENTENCE_TABLE, quote_string(sentence)))
    result = cursor.fetchone()
    response = "Sentence already in table, updating" if result else "Sentence and Instances added"

    # Since we are unable to store arrays with SQLite3, indexes are comma joined and stringified
    for instance in valid_instances:
        cursor.execute("INSERT INTO {} ({}, {}, {}) VALUES ({}, {}, {})"
                    .format(VALID_INSTANCES_TABLE,
                            "entity1", "rel", "entity2",
                            quote_string(instance[0]), quote_string(instance[1]), quote_string(instance[2])))
        valid_instance_keys.append(str(cursor.lastrowid))
    for instance in invalid_instances:
        cursor.execute("INSERT INTO {} ({}, {}, {}) VALUES ({}, {}, {})"
                    .format(INVALID_INSTANCES_TABLE,
                            "entity1", "rel", "entity2",
                            quote_string(instance[0]), quote_string(instance[1]), quote_string(instance[2])))
        invalid_instance_keys.append(str(cursor.lastrowid))

    # Insertion or updating of sentence in Sentence Table with instance indices
    insertion_command = "INSERT OR REPLACE INTO {} ({}, {}, {}, {}) VALUES ({}, {}, {}, {})".format(
        SENTENCE_TABLE,
        "sentence", "valid_keys", "invalid_keys", "processed",
        quote_string(sentence),
        quote_string(",".join(valid_instance_keys)),
        quote_string(",".join(invalid_instance_keys)),
        1)
    cursor.execute(insertion_command)

    # Save changes and close connection
    connection.commit()
    connection.close()
    return jsonify({
        "response": response
        });


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=False)
