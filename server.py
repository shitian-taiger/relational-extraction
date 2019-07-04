from flask_cors import CORS
from flask import Flask, request, jsonify
# Model
from test_implementation.trainer import Trainer
from test_implementation.main import model_config, training_config
# Dependency Parse
from generation.allen_models import DepParse
from generation.allen_models import OpenIE
from generation.dependency_parse.main import generate
from generation.oie_generate import DataGenerator

app = Flask(__name__)
CORS(app)

model_trainer = Trainer(model_config, training_config)
oie_generator = OpenIE()
dependency_parser = DepParse()
ner_oie_generator = DataGenerator(use_allen = True)

@app.route('/predict/all',methods=['POST'])
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

if __name__ == '__main__':
    app.run(port=8000, debug=True)
