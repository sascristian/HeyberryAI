# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.


from adapt.intent import IntentBuilder

from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft import MYCROFT_ROOT_PATH
from os import listdir
import pickle
import random
from jarbas_utils import RBM_Sampling as Sampling

from jarbas_utils import RBM_Utils as Utils
from jarbas_utils.ShortTextCodec import ShortTextCodec, BinomialShortTextCodec
from jarbas_utils.RBM import CharBernoulliRBM, CharBernoulliRBMSoftmax
from sklearn.cross_validation import train_test_split

# this is needed for pickled models that were trained somewhere else
# otherwise will complain of RBM / ShortTextCodec missing
import sys
sys.path.append(MYCROFT_ROOT_PATH + "/jarbas_utils")

__author__ = 'jarbas'

LOGGER = getLogger(__name__)


class RBM_Sampling_Service(MycroftSkill):
    def __init__(self):
        super(RBM_Sampling_Service, self).__init__()
        self.reload_skill = False
        self.external_reload = False
        self.external_shutdown = False
        self.model_path = MYCROFT_ROOT_PATH + "/jarbas_models/Char-RBM"

    def scan_models(self):
        # TODO some pre-processing
        models = listdir(self.model_path)
        return models

    def sample_models(self, models, n_samples=30, iters= 10 ** 3, start_temp=1.0,
                      end_temp=1.0, every=1, first=-1, sil=None):

        energy = True  # Along with each sample generated, print its free energy

        samples = []
        for model_fname in models:
            self.log.info("Drawing samples from model defined at {}".format(model_fname))
            try:
                with open(model_fname) as f:
                    model = pickle.load(f)
            except Exception as e:
                self.log.error(e)
                continue
            self.log.info("loaded model")
            if every == -1:
                sample_indices = [iters - 1]
            else:
                first = every if first == -1 else first
                sample_indices = range(first, iters, every)
                if sample_indices[-1] != iters - 1:
                    sample_indices.append(iters - 1)

            cb = Sampling.print_sample_callback

            kwargs = dict(start_temp=start_temp, final_temp=end_temp,
                          sample_energy=energy,
                          callback=cb)
            if sil:
                kwargs['init_method'] = Sampling.VisInit.silhouettes
                kwargs['training_examples'] = sil
            self.log.info("Starting Sampling")
            vis, new_samples = Sampling.sample_model(model, n_samples, iters,
                                        sample_indices, **kwargs)
            self.log.info(new_samples)
            samples.extend(new_samples)
            if energy:
                fe = model._free_energy(vis)
                self.log.debug('Final energy: {:.2f} (stdev={:.2f})\n'.format(fe.mean(), fe.std()))

        return samples

    def train_model(self, input_txt):
        # TODO finish this
        test_ratio=0.05
        softmax=False
        preserve_case=True
        binomial=False
        batch_size=10
        max_text_length=20
        min_text_length=1
        # only abcde...xyz by default lowe-cased, allow extra chars bellow
        extra_chars =' 1234567890'
        n_hidden=180
        learning_rate=0.1
        weight_cost=0.0001
        learning_rate_backoff=True
        epochs=5
        left=False
        model=None
        tag=''
        # If the path to a pretrained, pickled model was provided, resurrect it, and
        # update the attributes that make sense to change (stuff like #hidden units,
        # or max string length of course can't be changed)
        if model is not None:
            f = open(model)
            rbm = pickle.load(f)
            f.close()
            rbm.learning_rate = learning_rate
            rbm.base_learning_rate = learning_rate
            rbm.lr_backoff = learning_rate_backoff
            rbm.n_iter = epochs
            rbm.batch_size = batch_size
            rbm.weight_cost = weight_cost
            codec = rbm.codec
        else:
            codec_kls = BinomialShortTextCodec if binomial else ShortTextCodec
            codec = codec_kls(extra_chars, max_text_length,
                              min_text_length, preserve_case,
                              left)
            model_kwargs = {'codec': codec,
                            'n_components': n_hidden,
                            'learning_rate': learning_rate,
                            'lr_backoff': learning_rate_backoff,
                            'n_iter': epochs,
                            'verbose': 1,
                            'batch_size': batch_size,
                            'weight_cost': weight_cost,
                            }
            kls = CharBernoulliRBMSoftmax if softmax else CharBernoulliRBM
            rbm = kls(**model_kwargs)

        vecs = Utils.vectors_from_txtfile(input_txt, codec)
        train, validation = train_test_split(vecs, test_size=test_ratio)
        self.log.info("Training data shape : " + str(train.shape))

        rbm.fit(train, validation)
        out_fname = pickle_name(input_txt)
        out_fname = MYCROFT_ROOT_PATH + "/jarbas_models/Char-RBM/" + out_fname
        f = open(out_fname, 'wb')
        pickle.dump(rbm, f)
        f.close()
        self.log.info("Wrote model to " + out_fname)

    def initialize(self):
        self.emitter.on("RBM.sample.request", self.handle_sample_request)
        rbm_intent = IntentBuilder("TestRBMIntent").require(
            "TestRBMKeyword").build()
        self.register_intent(rbm_intent, self.handle_sample_intent)

    def handle_sample_request(self, message):
        models = message.data.get("model_path")
        n_samples = message.data.get("n_samples", 30)
        iters = message.data.get("n_iters", 10 ** 3)
        start_temp = message.data.get("start_temp", 1.0)
        end_temp = message.data.get("end_temp", 1.0)
        samples = self.sample_models(models, n_samples, iters, start_temp,
                                     end_temp)
        self.emitter.emit(Message("RBM.sample.result", {"samples": samples},
                                  self.message_context))

    def handle_sample_intent(self, message):
        model = random.choice(self.scan_models())
        name = model.replace("_", " ").replace(" .pickle", "")
        self.speak("Testing RBM Sampling with " + name + " model")
        model_path = self.model_path + "/" + model
        samples = self.sample_models([model_path], 5)
        for sample in samples:
            self.speak(sample)

    def stop(self):
        pass


def create_skill():
    return RBM_Sampling_Service()

def pickle_name(txt):
    fname = txt.split('.')[0].split('/')[-1]
    fname += '_'
    return fname + '.pickle'

