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


from mycroft.tts import TTS, TTSValidator
from mycroft.util.log import getLogger
from mycroft.util import play_wav

__author__ = 'jarbas'

LOGGER = getLogger("Deep_Throat")


class DeepThroat(TTS):
    def __init__(self, lang, voice):
        super(DeepThroat, self).__init__(lang, voice,
                                         DeepThroatValidator(self))
        from jarbas_utils.deep_throat import say
        self.synth = say

    def execute(self, sentence, output="/tmp/deep_throat_tts.wav"):
        self.begin_audio()
        try:
            mode_file_output = True
            verbose = False
            mode_translate_numbers = True
            self.synth(
                text=sentence,
                save_to_file=mode_file_output,
                filename_output=output,
                explain=verbose,
                translate_numbers=mode_translate_numbers
            )
            play_wav(output)
        except Exception as e:
            LOGGER.error(e)
            LOGGER.error("Install deep_throat by running "
                         "/JarbasAI/scripts/install_deep_throat.sh")
        self.end_audio()


class DeepThroatValidator(TTSValidator):
    def __init__(self, tts):
        super(DeepThroatValidator, self).__init__(tts)

    def validate_lang(self):
        # TODO
        pass

    def validate_connection(self):
        pass

    def get_tts_class(self):
        return DeepThroat
