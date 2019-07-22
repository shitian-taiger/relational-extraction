from pathlib import Path
from trainer import Trainer

# Implementation root
impl_root = Path(__file__).parent.resolve()

# Data
traindata_file = Path.joinpath(impl_root.parent.resolve(), "data/generated_instances.txt")
testdata_file = Path.joinpath(impl_root.parent.resolve(), "data/generated_instances.txt")

# ALLEN OIE config
# weights_dir = Path.joinpath(impl_root, "AllenOIE/weights")
# tokens_dir = Path.joinpath(impl_root, "AllenOIE/tokens")
labels_dir = Path.joinpath(impl_root, "AllenOIE/labels") # This is the same as the weights dir for now
# verb_embedding = Path.joinpath(impl_root, "AllenOIE/verb_embedder")

# Custom config
weights_dir = None
tokens_dir = Path.joinpath(impl_root, "Custom/tokens")
labels_dir = Path.joinpath(impl_root, "Custom/labels")
pos_dir = Path.joinpath(impl_root, "Custom/pos")


model_config = {
    "input_size": 200,
    "hidden_size": 300,
    "highway": True,
    "dropout": 0.2, # Irrelevant for now
    "layers": 8,
    "weights_dir": weights_dir, # Directory containing LSTM weights
    "tokens_dir": tokens_dir, # Directory containing tokens.txt and embeddings
    "pos_dir": pos_dir, # Directory containing pos.txt and corresponding embeddings
    "labels_dir": labels_dir, # Directory containing labels.txt and corresponding weights and bias
    "token_embedding_dim": 100,
    "ne_embedding_dim": 50,
    "pos_embedding_dim": 50,
}

training_config = {
    "epochs": 5,
    "batch_size": 2,
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
trainer.train()
