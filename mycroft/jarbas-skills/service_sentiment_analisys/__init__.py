from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger

import thread
import unirest
import random

__author__ = 'jarbas'

class SentimentSkill(MycroftSkill):

    def __init__(self):
        super(SentimentSkill, self).__init__(name="SentimentSkill")
        try:
            self.mashapekey = self.config_apis.get('MashapeAPI')
        except:
            self.mashapekey = self.config.get('MashapeAPI')
        # TODO make config
        self.defaultapi = 2



    def initialize(self):
        sentiment_intent = IntentBuilder("SentimentIntent"). \
            require("SentimentKeyword").build()
        self.register_intent(sentiment_intent, self.handle_sentiment_intent)

        sentiment2_intent = IntentBuilder("Sentiment2Intent"). \
            require("Sentiment2Keyword").build()
        self.register_intent(sentiment2_intent, self.handle_sentiment2_intent)

        sentiment3_intent = IntentBuilder("Sentiment3Intent"). \
            require("Sentiment3Keyword").build()
        self.register_intent(sentiment3_intent, self.handle_sentiment3_intent)

        self.emitter.on("sentiment_request", self.handle_sentiment_request)

    def handle_sentiment_request(self, message):
        txt = message.data.get('utterances')[0]
        sent = "unknown"
        posconf = 0
        negconf = 0
        try:
            sent, posconf, negconf = self.sentiment2(txt)
        except:
           self.log.error("couldnt reach sentiment api")
        self.emitter.emit(
            Message("sentiment_result",
                    {'text': [txt], 'result': [sent], 'conf+': [posconf], 'conf-': [negconf]}))
        self.log.info("text: " + txt + " sentiment: " + sent + " confidence: +" + str(posconf) + " - " + str(negconf))

    def handle_sentiment_intent(self, message):
        txt = ["i love you", "i hate you", "where are the ninjas"]
        txt = random.choice(txt)
        sent, conf = self.sentiment(txt)
        self.speak(txt)
        self.speak("Sentiment " + sent)
        self.speak("Confidence " + conf)

    def handle_sentiment2_intent(self, message):
        txt = ["i love you", "i hate you", "where are the ninjas"]
        txt = random.choice(txt)
        sent, posconf, negconf = self.sentiment2(txt)
        self.speak(txt)
        self.speak("Sentiment " + sent)
        self.speak("Positive Confidence " + str(posconf))
        self.speak("Negative Confidence " + str(negconf))

    def handle_sentiment3_intent(self, message):
        txt = ["i love you", "i hate you", "where are the ninjas"]
        txt = random.choice(txt)
        sent, conf = self.sentiment3(txt)
        self.speak(txt)
        self.speak("Sentiment " + sent)
        self.speak("Confidence " + conf)

    def sentiment3(self, txt):
        # https://market.mashape.com/vivekn/sentiment-3#sentiment
        response = unirest.post("https://community-sentiment.p.mashape.com/text/",
                                headers={
                                    "X-Mashape-Key": self.mashapekey,
                                    "Content-Type": "application/x-www-form-urlencoded",
                                    "Accept": "application/json"
                                },
                                params={
                                    "txt": txt
                                }
                                )
        sentiment = response.body["result"]["sentiment"]
        confidence = response.body["result"]["confidence"]
        return sentiment, str(confidence)

    def sentiment2(self, txt):
        # https://market.mashape.com/sentity/sentity-text-analytics
        txt = txt.replace(" ", "+")
        response = unirest.get("https://sentity-v1.p.mashape.com/v1/sentiment?text=" + txt,
                               headers={
                                   "X-Mashape-Key": self.mashapekey,
                                   "Accept": "application/json"
                               }
                               )
        # why did this start giving an error? it was working in the service, maybe api is down or changed something
        if "Internal Server Error" in response.body:
            pos = "Internal Server Error"
            neg = "Internal Server Error"
        else:
            pos = response.body["pos"]
            neg = response.body["neg"]

        # do some processing instead of printing
        if neg < 0.5 and pos > 0.5:
            sentiment = "positive"
        elif pos < 0.5 and neg > 0.5:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return sentiment, pos, neg

    def sentiment(self, txt):
        # https://market.mashape.com/mtnfog/cloud-nlp
        txt = txt.replace(" ", "+")
        response = unirest.get("https://mtnfog-cloud-nlp-v1.p.mashape.com/sentiment?text=" + txt,
                               headers={
                                   "X-Mashape-Key": self.mashapekey,
                                   "Accept": "application/json"
                               }
                               )
        confidence = response.body

        if confidence > 0:
            sentiment = "positive"
        elif confidence < 0:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        # sentiment =
        return sentiment, str(confidence)

    def stop(self):
        pass


def create_skill():
    return SentimentSkill()
