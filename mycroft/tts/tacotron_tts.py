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


import time
from mycroft.tts import TTS, TTSValidator
from mycroft.util.log import getLogger
from mycroft.configuration import ConfigurationManager
from mycroft.util import play_wav
from mycroft import MYCROFT_ROOT_PATH as root_path

__author__ = 'jarbas'

LOGGER = getLogger("Tacotron")


class Tacotron(TTS):
    def __init__(self, lang, voice):
        super(Tacotron, self).__init__(lang, voice,
                                       TacotronValidator(self))
        config = ConfigurationManager.get().get('tts', {}).get("tacotron", {})
        model = config.get("model", "tacotron-20170720")
        path = root_path + "/jarbas_models/tf_tacotron/trained/" + model + \
               "/model.ckpt"
        path = config.get("path", path)
        try:
            from jarbas_models.tf_tacotron.synthesizer import Synthesizer
            self.synthesizer = Synthesizer()
            self.synthesizer.load(path)
            LOGGER.info("Loaded Tacotron")
        except Exception as e:
            LOGGER.error(e)
            LOGGER.error("Install tacotron by running "
                         "/JarbasAI/scripts/install_tacotron.sh")
            self.synthesizer = None

    def execute(self, sentence, output="/tmp/tacotron_tts.wav"):
        if self.synthesizer is None:
            LOGGER.error("Tacotron failed to load")
            return
        self.begin_audio()
        try:
            start = time.time()
            LOGGER.info("Tacotron, Synthethize")
            self.synthesizer.synthesize(sentence, output)
            play_wav(output)
            LOGGER.info("elapsed time" + str(time.time() - start))
        except Exception as e:
            LOGGER.error(e)
            LOGGER.error("Install tacotron by running "
                         "/JarbasAI/scripts/install_tacotron.sh")
        self.end_audio()


class TacotronValidator(TTSValidator):
    def __init__(self, tts):
        super(TacotronValidator, self).__init__(tts)

    def validate_lang(self):
        # TODO
        pass

    def validate_connection(self):
        pass

    def get_tts_class(self):
        return Tacotron
