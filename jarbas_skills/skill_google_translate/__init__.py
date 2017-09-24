from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.skills.audioservice import AudioService

import os

from mtranslate import translate
import unicodedata

__author__ = 'jcasoft'


class TranslateSkill(MycroftSkill):
    def __init__(self):
        super(TranslateSkill, self).__init__('speech_client')

    def initialize(self):
        intent = IntentBuilder('TranslateIntent') \
            .require('TranslateKeyword') \
            .require('LanguageKeyword') \
            .require('phrase') \
            .build()
        self.register_intent(intent, self.handle_translate)

        intent = IntentBuilder('TranslateToIntent') \
            .require('TranslateKeyword') \
            .require('translate') \
            .require('ToKeyword') \
            .require('LanguageKeyword') \
            .build()
        self.register_intent(intent, self.handle_translate_to)

        self.audio = AudioService(self.emitter)

    def handle_translate(self, message):
        lang = message.data.get("LanguageKeyword")
        sentence = message.data.get("phrase")

        translated = translate(sentence, lang)

        self.say(translated, lang)

    def handle_translate_to(self, message):
        lang = message.data.get("LanguageKeyword")
        sentence = message.data.get("translate")

        translated = translate(sentence, lang)

        self.say(translated, lang)

    def say(self, sentence, lang):
        # sentence = unicode(sentence, "utf-8")
        sentence = unicodedata.normalize('NFKD', sentence).encode('ascii',
                                                                  'ignore')
        self.log.info("TRANSLATED PHRASE:", sentence)
        get_sentence = 'wget -q -U Mozilla -O /tmp/translated.mp3 "https://translate.google.com/translate_tts?tl=' + lang + '&q=' + sentence + '&client=tw-ob' + '"'
        os.system(get_sentence)
        self.audio.play("/tmp/translated.mp3")


def create_skill():
    return TranslateSkill()
