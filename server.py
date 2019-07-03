from flask import Flask, request, jsonify
from test_implementation.trainer import Trainer
from test_implementation.main import model_config, training_config

app = Flask(__name__)

trainer = Trainer(model_config, training_config)

@app.route('/rel_extract/predict',methods=['POST'])
def predict():
    data = request.get_json(force=True)
    prediction = trainer.predict(data)
    return jsonify(prediction)

@app.route('/rel_extract/add_instance',methods=['POST'])
def add_instance():
    data = request.get_json(force=True)
    return jsonify("Ok")

if __name__ == '__main__':
    app.run(port=3000, debug=True)
