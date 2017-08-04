
from mycroft.skills.core import MycroftSkill

__author__ = 'jarbas'


class TotalFailure(MycroftSkill):

    def __init__(self):
        super(TotalFailure, self).__init__()

    def initialize(self):
        self.emitter.on("complete_intent_failure", self.handle_fail)

    def handle_fail(self, message):
        # TODO use dialog
        self.speak("I don't know how to answer that")

    def stop(self):
        pass


def create_skill():
    return TotalFailure()
