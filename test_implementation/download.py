import torch
from pathlib import Path
from allennlp.models.archival import Archive, load_archive
from allennlp.predictors.predictor import Predictor

# Download model to extract parameters
archived_oie = load_archive("https://s3-us-west-2.amazonaws.com/allennlp/models/openie-model.2018-08-20.tar.gz")
predictor = Predictor.from_archive(archived_oie, "open-information-extraction")
model = predictor._model
encoder = model.encoder
stacked_bdlstm = encoder._module
vocab = model.vocab

impl_dir = Path(__file__).parent.resolve()
weights_dir = Path.joinpath(impl_dir, "weights")
Path(weights_dir).mkdir(parents=True, exist_ok=True)

# VOCABULARY
vocab.save_to_files("{}/vocab".format(impl_dir))

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
            torch.save(parameter, "{}/verb_embedder".format(weights_dir))
        else:
            torch.save(parameter, "{}/token_embedder".format(weights_dir))
    if parameter_dims[0] == 62:
        if len(parameter_dims) == 2:
            torch.save(parameter, "{}/tag_layer_weights".format(weights_dir))
        else:
            torch.save(parameter, "{}/tag_layer_bias".format(weights_dir))
