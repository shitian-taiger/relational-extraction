import pandas as pd
from flask_cors import CORS
from flask import Flask, request, jsonify

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

def quote_string(txt: str):
    return "\"" + txt + "\""

@app.route('/predict/all', methods=['POST'])
def predict_oie():
    data = request.get_json(force=True)
    sentence = data["sentence"]

    oie_prediction = oie_generator.get_tuples(sentence)
    dp_prediction = generate(dependency_parser.get_tree(sentence)) # Get tree from dependency parse first
    instance, ner_oie_prediction = ner_oie_generator.generate(sentence)
    return jsonify({"oie_prediction": oie_prediction,
                    "dp_prediction": dp_prediction,
                    "ner_oie_prediction": ner_oie_prediction
                    })

@app.route('/addinstances', methods=['POST'])
def add_instances():
    print("Add instances")
    SENTENCE_TABLE = "Sentence"
    VALID_INSTANCES_TABLE = "PositiveInstance"
    INVALID_INSTANCES_TABLE = "NegativeInstance"
    data = request.get_json(force=True)
    sentence = data["sentence"]
    valid_instances, invalid_instances = data["validInstances"], data["invalidInstances"]

    connection = sqlite3.connect('./data/store.db')
    cursor = connection.cursor()
    # Arrays are not supported in SQLite3, map string keys to integer primary keys in corresponding tables
    cursor.execute('create table if not exists {} (sentence TEXT, valid_keys STRING, invalid_keys STRING, UNIQUE(sentence))'
                   .format(SENTENCE_TABLE))
    cursor.execute('create table if not exists {} (entity1 TEXT, rel TEXT, entity2 TEXT)'
                   .format(VALID_INSTANCES_TABLE))
    cursor.execute('create table if not exists {} (entity1 TEXT, rel TEXT, entity2 TEXT)'
                   .format(INVALID_INSTANCES_TABLE))

    # Store primary keys of instances to store in sentence table
    valid_instance_keys = []
    invalid_instance_keys = []

    # Check if sentence already exists in table
    cursor.execute("SELECT * FROM {} WHERE sentence={}".format(SENTENCE_TABLE, quote_string(sentence)))
    result = cursor.fetchone()
    response = "" # Status of instances addition
    if result:
        response = "Sentence already in table"
    else:
        response = "Instances added"
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
        # Insertion into Sentence Table
        cursor.execute("INSERT INTO {} ({}, {}, {}) VALUES ({}, {}, {})"
                    .format(SENTENCE_TABLE,
                            "sentence", "valid_keys", "invalid_keys",
                            quote_string(sentence),
                            quote_string(",".join(valid_instance_keys)),
                            quote_string(",".join(invalid_instance_keys))
                            )
                    )

    # Save changes and close connection
    connection.commit()
    connection.close()
    return jsonify({
        "response": response
        });
if __name__ == '__main__':
    app.run(port=8000, debug=True)
