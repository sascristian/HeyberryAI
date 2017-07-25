
import time

from mycroft.util import play_wav
from mycroft.tts import TTS, TTSValidator
from mycroft.configuration import ConfigurationManager
from mycroft import MYCROFT_ROOT_PATH

__author__ = 'jarbas'

config = ConfigurationManager.get().get("tts").get("morse")


class MorseCode(TTS):
    def __init__(self, lang, voice, timestep=0.5):
        super(MorseCode, self).__init__(lang, voice, MorseCodeValidator(self))
        self.code = {'A': '.-', 'B': '-...', 'C': '-.-.',
                'D': '-..', 'E': '.', 'F': '..-.',
                'G': '--.', 'H': '....', 'I': '..',
                'J': '.---', 'K': '-.-', 'L': '.-..',
                'M': '--', 'N': '-.', 'O': '---',
                'P': '.--.', 'Q': '--.-', 'R': '.-.',
                'S': '...', 'T': '-', 'U': '..-',
                'V': '...-', 'W': '.--', 'X': '-..-',
                'Y': '-.--', 'Z': '--..',

                '0': '-----', '1': '.----', '2': '..---',
                '3': '...--', '4': '....-', '5': '.....',
                '6': '-....', '7': '--...', '8': '---..',
                '9': '----.'
                }

        self.time_step = float(config.get("time_step", timestep))
        self.morse_sound_path = config.get("path", MYCROFT_ROOT_PATH +
                                           "/mycroft/res/morse_sound_files")

        self.process = None

    def verify(self, string):
        keys = self.code.keys()
        for char in string:
            if char.upper() not in keys and char != ' ':
                print 'Error the character ' + char + ' cannot be translated to Morse Code'
                string.replace(char.upper(), " ")

    def execute(self, msg):

        self.verify(msg)

        for char in msg:
            if char == ' ':
                time.sleep(5 * self.time_step)
            else:
                morse_sound_path = self.morse_sound_path + "/" + char.upper() + '_morse_code.ogg'
                self.process = play_wav(morse_sound_path)
                time.sleep(2 * self.time_step) # ~sound duration


class MorseCodeValidator(TTSValidator):
    def __init__(self, tts):
        super(MorseCodeValidator, self).__init__(tts)

    def validate_lang(self):
        # TODO
        pass

    def validate_connection(self):
        # TODO check if sound files exist
        pass

    def get_tts_class(self):
        return MorseCode