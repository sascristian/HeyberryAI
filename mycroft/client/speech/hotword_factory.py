# Copyright 2017 Mycroft AI, Inc.
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

import tempfile
import time
import re

import os
from os.path import dirname, exists, join, abspath

from mycroft.configuration import Configuration
from mycroft.util.log import LOG
from subprocess import Popen, PIPE, STDOUT

__author__ = 'seanfitz, jdorleans, jarbas'


RECOGNIZER_DIR = join(abspath(dirname(__file__)), "recognizer")


class HotWordEngine(object):
    def __init__(self, key_phrase="hey mycroft", config=None, lang="en-us"):
        self.lang = str(lang).lower()
        self.key_phrase = str(key_phrase).lower()
        # rough estimate 1 phoneme per 2 chars
        self.num_phonemes = len(key_phrase)
        if config is None:
            config = Configuration.get().get("hot_words", {})
            config = config.get(self.key_phrase, {})
        self.config = config
        self.listener_config = Configuration.get().get("listener", {})
        self.need_wav = False

    def found_wake_word(self, frame_data):
        return False

    def found_wake_word_from_wav(self, wav_file):
        return False


class PocketsphinxHotWord(HotWordEngine):
    def __init__(self, key_phrase="hey mycroft", config=None, lang="en-us"):
        super(PocketsphinxHotWord, self).__init__(key_phrase, config, lang)
        # Hotword module imports
        from pocketsphinx import Decoder
        # Hotword module config
        module = self.config.get("module")
        if module != "pocketsphinx":
            LOG.warning(
                str(module) + " module does not match with "
                              "Hotword class pocketsphinx")
        # Hotword module params
        self.phonemes = self.config.get("phonemes", "HH EY . M AY K R AO F T")
        self.num_phonemes = len(self.phonemes.split())
        self.threshold = self.config.get("threshold", 1e-90)
        self.sample_rate = self.listener_config.get("sample_rate", 1600)
        dict_name = self.create_dict(key_phrase, self.phonemes)
        config = self.create_config(dict_name, Decoder.default_config())
        self.decoder = Decoder(config)

    def create_dict(self, key_phrase, phonemes):
        (fd, file_name) = tempfile.mkstemp()
        words = key_phrase.split()
        phoneme_groups = phonemes.split('.')
        with os.fdopen(fd, 'w') as f:
            for word, phoneme in zip(words, phoneme_groups):
                f.write(word + ' ' + phoneme + '\n')
        return file_name

    def create_config(self, dict_name, config):
        model_file = join(RECOGNIZER_DIR, 'model', self.lang, 'hmm')
        if not exists(model_file):
            LOG.error('PocketSphinx model not found at ' + str(model_file))
        config.set_string('-hmm', model_file)
        config.set_string('-dict', dict_name)
        config.set_string('-keyphrase', self.key_phrase)
        config.set_float('-kws_threshold', float(self.threshold))
        config.set_float('-samprate', self.sample_rate)
        config.set_int('-nfft', 2048)
        config.set_string('-logfn', '/dev/null')
        return config

    def transcribe(self, byte_data, metrics=None):
        start = time.time()
        self.decoder.start_utt()
        self.decoder.process_raw(byte_data, False, False)
        self.decoder.end_utt()
        if metrics:
            metrics.timer("mycroft.stt.local.time_s", time.time() - start)
        return self.decoder.hyp()

    def found_wake_word(self, frame_data):
        hyp = self.transcribe(frame_data)
        return hyp and self.key_phrase in hyp.hypstr.lower()


class SnowboyHotWord(HotWordEngine):
    def __init__(self, key_phrase="hey mycroft", config=None, lang="en-us"):
        super(SnowboyHotWord, self).__init__(key_phrase, config, lang)
        # Hotword module imports
        try:
            from snowboydecoder import HotwordDetector
        except ImportError:
            from mycroft.client.speech.recognizer.snowboy.snowboydecoder \
                import HotwordDetector
        # Hotword module config
        module = self.config.get("module")
        if module != "snowboy":
            LOG.warning(module + " module does not match with Hotword class "
                                 "snowboy")
        # Hotword params
        models = self.config.get("models", {})
        paths = []
        for key in models:
            path = models[key]
            if ".pmdl" not in path and ".umdl" not in path:
                path += ".pmdl"
            if "/" not in path:
                path = dirname(
                    __file__) + "/recognizer/snowboy/resources/" + path
            paths.append(path)
        sensitivity = self.config.get("sensitivity", 0.5)
        self.snowboy = HotwordDetector(paths,
                                       sensitivity=[sensitivity] * len(paths))

    def found_wake_word(self, frame_data):
        wake_word = self.snowboy.detector.RunDetection(frame_data)
        return wake_word == 1


class JuliusHotWord(HotWordEngine):
    def __init__(self, key_phrase="hey mycroft", config=None, lang="en-us"):
        super(JuliusHotWord, self).__init__(key_phrase, config, lang)
        self.need_wav = True
        # Hotword module config
        module = self.config.get("module")
        if module != "julius":
            LOG.warning(
                str(module) + " module does not match with "
                              "Hotword class julius")
        # Hotword module params
        self.jconf = RECOGNIZER_DIR + "/julius/julius.jconf"
        self.grammar = RECOGNIZER_DIR + "/julius/julius"
        self.min_score = 0.5  # TODO find good compromise
        self.debug = True

    def ask_julius(self, file):
        path = RECOGNIZER_DIR + "/julius/julius.txt"
        with open(path, "w") as f:
            f.write(file)
        hyp = None
        score = -1.0
        args = ["julius", '-C', self.jconf, '-gram', self.grammar,
                '-input',
                "rawfile", "-filelist", path]
        p = Popen(args,
                  stdout=PIPE,
                  stderr=STDOUT)

        while True:
            line = p.stdout.readline()
            if not line:
                continue
            if self.debug and "warning" in line.lower():
                LOG.error(line)
            if "error" in line.lower() or "search failed" in line.lower():
                if self.debug:
                    LOG.error(line)
                break
            m = re.match(r'^(sentence|cmscore)1: (.*)', line)
            if m:
                attr = m.group(1)
                val = m.group(2)
                if attr == 'sentence':
                    hyp = val.split()
                elif attr == 'cmscore':
                    score = [float(v) for v in val.split()]
                break

        if score > self.min_score:
            return hyp
        return None

    def found_wake_word(self, frame_data):
        # TODO frame_data to .wav
        output = RECOGNIZER_DIR + "/julius/julius.wav"
        return False

    def found_wake_word_from_wav(self, wav_file):
        hyp = self.ask_julius(wav_file)
        return hyp and self.key_phrase in hyp.lower()


class HotWordFactory(object):
    CLASSES = {
        "pocketsphinx": PocketsphinxHotWord,
        "snowboy": SnowboyHotWord,
        "julius": JuliusHotWord
    }

    @staticmethod
    def create_hotword(hotword="hey mycroft", config=None, lang="en-us"):
        LOG.info("creating " + hotword)
        if not config:
            config = Configuration.get().get("hotwords", {})
        module = config.get(hotword, {}).get("module", "pocketsphinx")
        config = config.get(hotword, {"module": module})
        clazz = HotWordFactory.CLASSES.get(module)
        return clazz(hotword, config, lang=lang)

