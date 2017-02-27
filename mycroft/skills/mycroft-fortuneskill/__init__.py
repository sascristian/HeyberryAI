import os
import subprocess
from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'jaevans'

LOGGER = getLogger(__name__)

class FortuneSkill(MycroftSkill):
    def __init__(self):
        super(FortuneSkill, self).__init__(name="FortuneSkill")
        self.process = None

    def initialize(self):
       # self.load_data_files(dirname(__file__))
        intent = IntentBuilder('FortuneIntent').require(
            'FortuneKeyword').build()
        self.register_intent(intent, self.handle_intent)

    def handle_intent(self, message):
        fortune = subprocess.check_output('fortune')
        self.speak(fortune)

        self.add_result("fortune",fortune)
        self.emit_results()
        

def create_skill():
    return FortuneSkill()
