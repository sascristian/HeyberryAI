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



import unirest

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'jarbas'

logger = getLogger(__name__)


class LotterySkill(MycroftSkill):

    def __init__(self):
        super(LotterySkill, self).__init__(name="LotterySkill")
        self.mashape = self.config["mashape_key"]

    def initialize(self):

        last_numbers_intent = IntentBuilder("LastLotteryIntent")\
            .require("CurrentLotteryKeyword").build()
        self.register_intent(last_numbers_intent,
                             self.handle_last_numbers_intent)

        jackpot_intent = IntentBuilder("JackpotIntent") \
            .require("JackPotKeyword").build()
        self.register_intent(jackpot_intent,
                             self.handle_jackpot_intent)

        next_key_intent = IntentBuilder("NextLotteryResultIntent") \
            .require("NextKeyKeyword").build()
        self.register_intent(next_key_intent,
                             self.handle_next_key_intent)

        ### TODO add historic numbers data
        ### TODO read prizes and winners
        ### TODO add non european lotterys and stuff

    def handle_next_key_intent(self, message):
        self.speak_dialog("nextlottery")
    def handle_last_numbers_intent(self, message):
        # These code snippets use an open-source library. http://unirest.io/python
        response = unirest.get("https://euromillions.p.mashape.com/ResultsService/FindLast",
                               headers={
                                   "X-Mashape-Key": self.mashape,
                                   "Accept": "text/plain"
                               }
                               )
        date =  response.body["Date"] #todo conver to human readable and speak
        n1 = response.body["Num1"]
        n2 = response.body["Num2"]
        n3 = response.body["Num3"]
        n4 = response.body["Num4"]
        n5 = response.body["Num5"]
        s1 = response.body["Star1"]
        s2 = response.body["Star2"]
        self.speak_dialog("currenteuromillions",{"n1":n1,"n2":n2,"n3":n3,"n4":n4,"n5":n5,"s1":s1,"s2":s2})
        self.add_result("n1", n1)
        self.add_result("n2", n2)
        self.add_result("n3", n3)
        self.add_result("n4", n4)
        self.add_result("n5", n5)
        self.add_result("s1", s1)
        self.add_result("s2", s2)
        self.add_result("date", date)
        self.emit_results()

    def handle_jackpot_intent(self, message):
        # These code snippets use an open-source library. http://unirest.io/python
        response = unirest.get("https://euromillions.p.mashape.com/ResultsService/FindLast",
                               headers={
                                   "X-Mashape-Key": self.mashape,
                                   "Accept": "text/plain"
                               }
                               )
        jackpot = response.body["Jackpot"]
        nextjackpot = response.body["NextJackpot"]
        date = response.body["Date"]  # todo conver to human readable and speak
        self.speak_dialog("jackpot", {"jackpot": jackpot})
        self.speak_dialog("nextjackpot", {"nextjackpot": nextjackpot})
        self.add_result("jackpot", jackpot)
        self.add_result("next jackpot", jackpot)
        self.add_result("date", date)
        self.emit_results()

    def handle_prize(self, message):
        # These code snippets use an open-source library. http://unirest.io/python
        response = unirest.get("https://euromillions.p.mashape.com/ResultsService/FindLast",
                               headers={
                                   "X-Mashape-Key": self.mashape,
                                   "Accept": "text/plain"
                               }
                               )
        prizes = response.body["PrizeCombinations"]
        #TODO parse
        self.add_result("prizes",prizes)
        self.emit_results()

    def stop(self):
        pass


def create_skill():
    return LotterySkill()


