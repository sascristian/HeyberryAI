from mycroft.configuration import ConfigurationManager
from mycroft.util.log import getLogger
from mycroft.client.speech.recognizer.pocketsphinx_recognizer import PocketsphinxRecognizer
from mycroft.client.speech.recognizer.snowboy_recognizer import SnowboyRecognizer

__author__ = "jarbas"

LOG = getLogger("Hotwords")


class PocketsphinxHotWord():
    def __init__(self, key_phrase, lang="en-us", config=None):
        if config is None:
            config = ConfigurationManager.get().get("hot_words", {})
            config = config.get(key_phrase, {})
        phonemes = config.get("phonemes")
        threshold = config.get("threshold", 1e-90)
        sample_rate = config.get("sample_rate", 1600)
        self.recognizer = PocketsphinxRecognizer(key_phrase, phonemes, threshold,
                                                 sample_rate=sample_rate,
                                                 lang="en-us")
        self.lang = str(lang).lower()
        self.key_phrase = str(key_phrase).lower()

    def found_wake_word(self, frame_data, lang="en-us"):
        return self.recognizer.found_wake_word(frame_data)


class SnowboyHotWord():
    def __init__(self, key_phrase, lang="en-us", config=None):
        if config is None:
            config = ConfigurationManager.get().get("hot_words", {})
            config = config.get(key_phrase, {})
        models = config.get("models", {})
        paths = []
        for key in models:
            paths.append(models[key])
        sensitivity = config.get("sensitivity", 0.5)
        self.recognizer = SnowboyRecognizer(models_path_list=paths,
                                            sensitivity=sensitivity,
                                            wake_word=key_phrase)
        self.lang = str(lang).lower()
        self.key_phrase = str(key_phrase).lower()

    def found_wake_word(self, frame_data, lang="en-us"):
        return self.recognizer.found_wake_word(frame_data)


class HotWordFactory(object):
    CLASSES = {
        "pocketsphinx": PocketsphinxHotWord,
        "snowboy": SnowboyHotWord
    }

    @staticmethod
    def create_hotword(hotword):
        LOG.info("creating " + hotword)
        config = ConfigurationManager.get().get("hot_words", {})
        module = config.get(hotword).get("module")
        clazz = HotWordFactory.CLASSES.get(module)
        return clazz(hotword)

    @staticmethod
    def create_wake_word():
        config = ConfigurationManager.get().get("listener", {})
        wake_word = config.get('wake_word', "hey jarbas").lower()
        LOG.info("creating " + wake_word)
        config = config.get("wake_word_config", {})
        module = config.get('module', "pocketsphinx")
        clazz = HotWordFactory.CLASSES.get(module)
        return clazz(wake_word, config)

    @staticmethod
    def create_standup_word():
        config = ConfigurationManager.get().get("listener", {})
        standup_word = config.get('standup_word', "wake up").lower()
        LOG.info("creating " + standup_word)
        config = config.get("standup_word_config", {})
        module = config.get('module', "pocketsphinx")
        clazz = HotWordFactory.CLASSES.get(module)
        return clazz(standup_word, config)
