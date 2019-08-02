import re
from pathlib import Path
from model_implementation.trainer import Trainer

def get_model_training_config(impl_root: str):

    # Data
    traindata_file = Path.joinpath(impl_root.parent.resolve(), "data/generated/db_generated_instances.txt")
    testdata_file = Path.joinpath(impl_root.parent.resolve(), "data/generated/db_generated_instances.txt")

    # Model savepath
    save_path = Path.joinpath(impl_root, "db_saved")
    save_path.mkdir(parents=True, exist_ok=True)
    num_epochs_per_save = 5

    # Saved model path for prediction
    predict_path = Path.joinpath(impl_root, "db_saved/model_epoch5")

    # Custom configurations
    weights_dir = None
    tokens_dir = Path.joinpath(impl_root, "Custom/tokens")
    pos_dir = Path.joinpath(impl_root, "Custom/pos")
    ne_emb_path = None
    labels_dir = Path.joinpath(impl_root, "Custom/labels")

    # Ensure tokens_dir, pos_dir and labels_dir are present considering they all required for vocabulary generation
    # weights_dir and ne_dir can be `None`
    model_config = {
        "input_size": 200,
        "hidden_size": 300,
        "highway": True,
        "dropout": 0.2, # Irrelevant for now
        "layers": 8,
        "weights_dir": weights_dir,
        "tokens_dir": tokens_dir,
        "pos_dir": pos_dir,
        "labels_dir": labels_dir,
        "token_embedding_dim": 100,
        "ne_embedding_dim": 50,
        "pos_embedding_dim": 50,
        "predict_path": predict_path
    }

    training_config = {
        "epochs": 100,
        "batch_size": 10,
        "learning_rate": 0.001,
        "traindata_file": traindata_file,
        "testdata_file": testdata_file,
        "save_on_epochs": num_epochs_per_save, # Every x number of epochs to save on
        "save_path": save_path
    }

    return model_config, training_config


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
    "Bob is currently a student in Xaunity University.",
    "Bob walked into the Couldola Mall.",
    "This $1 stamp features a screen painting by Japanese painter Houitsu Sakai..",
    "As part of the island’s upgrading works, a $100,000 interactive Sounds of Siloso exhibit was added to the Fort’s tunnel system in 1987..",
    "This $2 Singapore Biennale stamp was issued by Singapore Post on 13 September 2006..",
    "Postcard bearing King George V 1-cent green stamp, used in Federated Malay States (FMS) in 1916.",
    "Meanwhile, the ’80s saw a turning point in Goh’s opera vocation."
             ]

if __name__ == "__main__":

    # Implementation root
    impl_root = Path.joinpath(Path(__file__).parent.resolve(), 'model_implementation')

    TRAIN = True
    model_config, training_config = get_model_training_config(impl_root)
    trainer = Trainer(model_config, training_config)
    if TRAIN:
        trainer.train()
    else:
        for sentence in sentences:
            predicted = trainer.predict(sentence)
            print(predicted)

