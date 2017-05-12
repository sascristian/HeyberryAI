# mycroft-skill-obitcoin-enhanced
#
# A skill for MycroftAI that querys various bitcoin statistics.
#
# Adapted from a MycroftAI skill by Red5d
#
# Licensed under the GNU General Public License v3
# (see LICENSE for more details

from os.path import dirname, join

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
import requests

__author__ = 'Red5d', 'chrison999'

class BitcoinSkill(MycroftSkill):
    def __init__(self):
        super(BitcoinSkill, self).__init__(name="BitcoinSkill")
        self.default_currency = "euro"

    def initialize(self):
        intent = IntentBuilder("BitcoinAvgIntent").require("BitcoinAvgKeyword") \
            .optionally("Currency").build()
        self.register_intent(intent, self.handle_avg)

        intent = IntentBuilder("BitcoinHighIntent").require("BitcoinHighKeyword") \
            .optionally("Currency").build()
        self.register_intent(intent, self.handle_high)

        intent = IntentBuilder("BitcoinLowIntent").require("BitcoinLowKeyword") \
            .optionally("Currency").build()
        self.register_intent(intent, self.handle_low)

        intent = IntentBuilder("BitcoinLastIntent").require("BitcoinLastKeyword") \
            .optionally("Currency").build()
        self.register_intent(intent, self.handle_last)

        intent = IntentBuilder("BitcoinVolIntent").require("BitcoinVolKeyword") \
            .optionally("Currency").build()
        self.register_intent(intent, self.handle_volume)

    def handle_avg(self, message):
        currency = str(message.data.get("Currency"))  # optional parameter
        if currency == 'None':
            currency = self.default_currency
        result = self.fiat_get(currency)
        price = requests.get("https://api.bitcoinaverage.com/all").json()[str(result)]['averages']['24h_avg']
        self.speak("The 24 hour average bitcoin price is "+str(price)+" "+currency+".")

    def handle_high(self, message):
        currency = str(message.data.get("Currency"))  # optional parameter
        if currency == 'None':
            currency = self.default_currency
        result = self.fiat_get(currency)
        price = requests.get("https://api.bitcoinaverage.com/all").json()[str(result)]['averages']['ask']
        self.speak("The current asking price for bitcoin "+str(price)+" "+currency+".")

    def handle_low(self, message):
        currency = str(message.data.get("Currency"))  # optional parameter
        if currency == 'None':
            currency = self.default_currency
        result = self.fiat_get(currency)
        price = requests.get("https://api.bitcoinaverage.com/all").json()[str(result)]['averages']['bid']
        self.speak("The current bid price for bitcoin "+str(price)+" "+currency+".")

    def handle_last(self, message):
        currency = str(message.data.get("Currency"))  # optional parameter
        if currency == 'None':
            currency = self.default_currency
        result = self.fiat_get(currency)
        price = requests.get("https://api.bitcoinaverage.com/all").json()[str(result)]['averages']['last']
        self.speak("The current price for bitcoin "+str(price)+" "+currency+".")

    def handle_volume(self, message):
        currency = str(message.data.get("Currency"))  # optional parameter
        if currency == 'None':
            currency = self.default_currency
        result = self.fiat_get(currency)
        price = requests.get("https://api.bitcoinaverage.com/all").json()[str(result)]['averages']['total_vol']
        self.speak("The 24 hour volume for "+currency+ " bitcoin is "+str(price)+" btc.")

    def fiat_get(self, currency):
        if currency == 'None':
            currency = self.default_currency
            result = 'EUR'
            return result
        else:
            choices = {
                       'reals': 'BRL',
                       'canadian dollars': 'CAD',
                       'euros': 'EUR',
                       'yuans': 'CNY',
                       'koruna': 'CZK',
                       'rupiahs': 'IDR',
                       'shekels': 'ILS',
                       'rupees': 'INR',
                       'yens': 'JPY',
                       'won': 'KRW',
                       'pesos': 'MXN',
                       'ringgit': 'MYR',
                       'nairas': 'NGN',
                       'zlotys':  'PLN',
                       'roubles': 'RUB',
                       'kronas': 'SEK',
                       'singapore dollars': 'SGD',
                       'lira': 'TRY',
                       'u s a dollars': 'USD',
                       'american dollars': 'USD',
                       'rands': 'ZAR',
                       'pounds': "GBP"}
            result = choices.get(str(currency), 'USD')
            return result

    def stop(self):
        pass


def create_skill():
    return BitcoinSkill()
