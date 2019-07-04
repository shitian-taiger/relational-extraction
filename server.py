from flask_cors import CORS
from flask import Flask, request, jsonify
from test_implementation.trainer import Trainer
from test_implementation.main import model_config, training_config

app = Flask(__name__)
CORS(app)

trainer = Trainer(model_config, training_config)

@app.route('/rel_extract/predict',methods=['POST'])
def predict():
    data = request.get_json(force=True)

    sentence = data["sentence"]

    prediction = trainer.predict(sentence)
    return jsonify(prediction)

if __name__ == '__main__':
    app.run(port=8000, debug=True)
