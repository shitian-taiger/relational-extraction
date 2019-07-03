from pathlib import Path
from .trainer import Trainer

p = Path(__file__).parent.resolve()

model_config = {
    "input_size": 200,
    "hidden_size": 300,
    "highway": True,
    "dropout": 0.2, # Irrelevant for now
    "embedding_dim": 100,
    "layers": 8,
    "num_classes": 62,
}

traindata_file = Path.joinpath(p.parent, "data/OIE/train.oie.conll")
testdata_file = Path.joinpath(p.parent, "data/OIE/test.gold_conll")

training_config = {
    "epochs": 5,
    "batch_size": 50,
    "learning_rate": 0.01,
    "traindata_file": traindata_file,
    "testdata_file": testdata_file
}

sentences = [
    "Harry is a random dude.",
    "Linguistics is extremely interesting while being highly relevant.",
    "These reports were later denied by a high Brazilian official, who said Brazil wasn't involved in any coffee discussions on quotas, the analyst said.",
    ]

# trainer = Trainer(model_config, training_config)
# trainer.train()
# for sentence in sentences:
#     print(trainer.predict(sentence))
