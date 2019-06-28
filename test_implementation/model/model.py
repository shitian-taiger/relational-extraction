import torch
from .utils import *


class REModel(torch.nn.Module):

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.embedding = self.load_embedding(config["embedding"])


    def load_embedding(self, embedding_dir: str):
        


    def forward(self, input: Dict):
        """
        Takes as input dictionary of { "sent_vec": Tensor, "pred_vec": Tensor }
        """


