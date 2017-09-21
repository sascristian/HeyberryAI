from jarbas_models.tf_tacotron.models.tacotron import Tacotron


def create_model(name, hparams):
    if name == 'tacotron':
        return Tacotron(hparams)
    else:
        raise Exception('Unknown model: ' + name)
