import shutil
import urllib.request
import zipfile
import torch
import numpy as np
from pathlib import Path
from allennlp.models.archival import Archive, load_archive
from allennlp.predictors.predictor import Predictor

# Get current directory
impl_dir = Path(__file__).parent.resolve()

# Download GLOVE embeddings and generate tokens.txt file
glove_url = "http://nlp.stanford.edu/data/glove.6B.zip"
glove_zip_path = Path.joinpath(impl_dir, "glove.6B.zip")
glove_dir_path = Path.joinpath(impl_dir, "glove.6B")

# Download and unzip if not present
if not Path(glove_dir_path).exists(): # Assume if directory exists, GLOVE embeddings already downloaded
    if not Path(glove_zip_path).exists():
        print("Downloading GLOVE embeddings")
        urllib.request.urlretrieve(glove_url, glove_zip_path)
    with zipfile.ZipFile(glove_zip_path,"r") as zip_ref:
        zip_ref.extractall(glove_dir_path)
    glove_dir_path.mkdir(parents=True, exist_ok=True) # Create storage directory

# Write tokens to file
print("Extracting GLOVE tokens and embeddings")
embedding_filepath = Path.joinpath(glove_dir_path, 'glove.6B.100d.txt')
token_filepath = Path.joinpath(glove_dir_path, 'tokens.txt')
token_file = open(token_filepath, "a+")
embedding_vectors = []
with open(embedding_filepath) as emb_file: # Read tokens only and write to tokens file
    for line in emb_file:
        line = line.split()
        token = line[0]
        token_file.write(token + "\n")
        embedding_vectors.append(np.array(line[1:]).astype(np.float)) # Get Embedding vector
token_file.close()

# Create Embedding Matrix
# Assume we're using dim=100 for now, also allow for PAD and UNK embeddings, hence + 2
embedding_matrix = np.zeros((len(embedding_vectors) + 2, 100))
for i, vector in enumerate(embedding_vectors):
    embedding_matrix[i + 2] = vector
embedding_tensor = torch.Tensor(embedding_matrix)
torch.save(embedding_tensor, Path.joinpath(glove_dir_path, 'token_embedder'))


# FOR ALLEN OIE MODEL ONLY
# Download model to extract parameters
archived_oie = load_archive("https://s3-us-west-2.amazonaws.com/allennlp/models/openie-model.2018-08-20.tar.gz")
predictor = Predictor.from_archive(archived_oie, "open-information-extraction")
model = predictor._model
encoder = model.encoder
stacked_bdlstm = encoder._module
vocab = model.vocab

allen_dir = Path.joinpath(impl_dir, "AllenOIE")
Path(allen_dir).mkdir(parents=True, exist_ok=True)
tokens_dir = Path.joinpath(allen_dir, "tokens")
Path(tokens_dir).mkdir(parents=True, exist_ok=True)
labels_dir = Path.joinpath(allen_dir, "labels")
Path(labels_dir).mkdir(parents=True, exist_ok=True)
weights_dir = Path.joinpath(allen_dir, "weights")
Path(weights_dir).mkdir(parents=True, exist_ok=True)

# VOCABULARY
vocab.save_to_files(tokens_dir)
shutil.move(Path.joinpath(tokens_dir, "labels.txt"), Path.joinpath(labels_dir, "labels.txt"))

# BIDIRECTIONAL LSTM WEIGHTS
for i, layer in enumerate(stacked_bdlstm.lstm_layers):
    for parameter in layer.input_linearity.parameters():
        if len(list(parameter.shape)) == 2:
            torch.save(parameter, "{}/layer{}_input_weight".format(weights_dir, i))
        else:
            torch.save(parameter, "{}/layer{}_input_bias".format(weights_dir, i))

    for parameter in layer.state_linearity.parameters():
        if len(list(parameter.shape)) == 2:
            torch.save(parameter, "{}/layer{}_state_weight".format(weights_dir, i))
        else:
            torch.save(parameter, "{}/layer{}_state_bias".format(weights_dir, i))

# EMBEDDINGS AND TAG LAYER WEIGHTS
for parameter in model.parameters():
    parameter_dims = list(parameter.shape)
    if len(parameter_dims) == 2 and parameter_dims[1] == 100:
        if parameter_dims[0] == 2:
            torch.save(parameter, "{}/verb_embedder".format(allen_dir))
        else:
            torch.save(parameter, "{}/token_embedder".format(tokens_dir))
    if parameter_dims[0] == 62:
        if len(parameter_dims) == 2:
            torch.save(parameter, "{}/tag_layer_weights".format(labels_dir))
        else:
            torch.save(parameter, "{}/tag_layer_bias".format(labels_dir))
