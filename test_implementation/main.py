from trainer import Trainer

model_config = {
    "input_size": 200,
    "hidden_size": 300,
    "highway": True,
    "dropout": 0.2, # Irrelevant for now
    "embedding_dim": 100,
    "layers": 8,
    "num_classes": 62
}


training_config = {
    "epochs": 5,
    "batch_size": 20,
    "learning_rate": 0.01,
}

sentences = [
    "Harry is a random dude.",
    # "Linguistics is extremely interesting while being highly relevant.",
    # "These reports were later denied by a high Brazilian official, who said Brazil wasn't involved in any coffee discussions on quotas, the analyst said.",
    ]

tokens = [
    [ "Harry", "is", "a", "random", "dude", "." ],
    [ "Linguistics", "is", "extremely", "interesting", "while", "being", "highly", "relevant", "." ],
    [ "Linguistics", "is", "extremely", "interesting", "while", "being", "highly", "relevant", "." ],
    ]
tags = [
    ['B-ARG0', 'B-V', 'O', 'O', 'O', 'O'],
    ['B-ARG0', 'B-V', 'B-ARG1', 'O', 'B-ARG2', 'O', 'I-ARG2', 'O', 'O'],
    ['O', 'O', 'O', 'O', 'O', 'B-V', 'B-ARG1', 'I-ARG1', 'O'],
    ]

trainer = Trainer(model_config, training_config)
trainer.train()
