from flask_cors import CORS
from flask import Flask, request, jsonify
# Model
from test_implementation.trainer import Trainer
from test_implementation.main import model_config, training_config
# Dependency Parse
from generation.allen_models import DepParse
from generation.dependency_parse.main import generate

app = Flask(__name__)
CORS(app)

model_trainer = Trainer(model_config, training_config)
dependency_parser = DepParse()

@app.route('/predict/oie',methods=['POST'])
def predict_oie():
    data = request.get_json(force=True)
    sentence = data["sentence"]
    prediction = model_trainer.predict(sentence)
    return jsonify(prediction)

@app.route('/predict/dep_parse', methods=['POST'])
def predict_dep_parse():
    data = request.get_json(force=True)
    sentence = data["sentence"]
    root = dependency_parser.get_tree(sentence) # Get tree from dependency parse
    results = generate(root) # Evaluate
    print(results)
    return jsonify(results)

if __name__ == '__main__':
    app.run(port=8000, debug=True)
