from pathlib import Path
from model_implementation.trainer import Trainer

# Implementation root
impl_root = Path.joinpath(Path(__file__).parent.resolve(), 'model_implementation')

# Data
traindata_file = Path.joinpath(impl_root.parent.resolve(), "data/generated_instances.txt")
testdata_file = Path.joinpath(impl_root.parent.resolve(), "data/_generated_instances.txt")

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

save_path = Path.joinpath(impl_root, "saved")

training_config = {
    "epochs": 101,
    "batch_size": 50,
    "learning_rate": 0.01,
    "traindata_file": traindata_file,
    "testdata_file": testdata_file,
    "save_path": save_path
}

sentences = [
    "Knox continued to work for the East India Company for thirteen years after his return from the East, captaining the ship Tonqueen Merchant for four further voyages to the East.",
    "After leaving Congress, Horace G. Snover moved to Port Huron, where he died at the age of seventy-six and is interred there in Lakeside Cemetery.",
    "Erdman was elected as a Democrat to the Twenty-ninth Congress.",
    "Noam Chomsky began undergraduate studies at the University of Pennsylvania at age 16, and from 1951 to 1955 was a member of Harvard University's Society of Fellows, where he developed the theory of transformational grammar for which he earned his doctorate in 1955. ",
    "Chomsky's B.A. honors thesis was titled 'Morphophonemics of Modern Hebrew', and involved applying Harris's methods to the language.",
    "Bob died in July 1984 in Bosnia.",
    "Bob killed Conrad in London",
    "Bob is a member of the London Society of Murderers",
    "Bob is an associate of the London Society of Murderers",
    "Bob got his master's degree from the University Of Chainsaws.",
    "Bob got his Phd from the University Of Chanad.",
    "Bob is currently a student in Xaunity University."
             ]

if __name__ == "__main__":
    TRAIN = True
    trainer = Trainer(model_config, training_config)
    if TRAIN:
        trainer.train()
    else:
        for sentence in sentences:
            predicted = trainer.predict(sentence)
            print(predicted)

