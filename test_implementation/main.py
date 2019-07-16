from pathlib import Path
from trainer import Trainer

# Implementation root
impl_root = Path(__file__).parent.resolve()

# Data
traindata_file = Path.joinpath(impl_root.parent.resolve(), "data/OIE/train.oie.conll")
testdata_file = Path.joinpath(impl_root.parent.resolve(), "data/OIE/test.gold_conll")

# ALLEN OIE config
weights_dir = Path.joinpath(impl_root, "AllenOIE/weights")
tokens_dir = Path.joinpath(impl_root, "AllenOIE/tokens")
labels_dir = Path.joinpath(impl_root, "AllenOIE/labels") # This is the same as the weights dir for now
verb_embedding = Path.joinpath(impl_root, "AllenOIE/verb_embedder")

# Custom config
# weights_dir = Path.joinpath(impl_root, "Custom/weights")
# tokens_dir = Path.joinpath(impl_root, "Custom/tokens")
# labels_dir = Path.joinpath(impl_root, "Custom/labels") # This is the same as the weights dir for now
# verb_embedding = Path.joinpath(impl_root, "AllenOIE/verb_embedder")


model_config = {
    "input_size": 200,
    "hidden_size": 300,
    "highway": True,
    "dropout": 0.2, # Irrelevant for now
    "layers": 8,
    "weights_dir": weights_dir, # Directory containing LSTM weights
    "tokens_dir": tokens_dir, # Directory containing tokens.txt and embeddings
    "labels_dir": labels_dir, # Directory containing labels.txt and corresponding weights and bias
    "verb_embedding": verb_embedding, # Filepath to verb embedding file
    "embedding_dim": 100, # Ensure this matches token embedding dimensions
    "num_classes": 62, # Ensure this matches num labels
}

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

trainer = Trainer(model_config, training_config)
for sentence in sentences:
    print(trainer.predict(sentence))
