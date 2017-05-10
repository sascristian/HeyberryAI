import sys
from os.path import dirname
from threading import Thread

from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

obj = dirname(dirname(__file__))
sys.path.append(obj)
from service_display.display import start as DisplayStart

__author__ = "jarbas"

logger = getLogger(__name__)


class DisplayService(MycroftSkill):
    def __init__(self):
        super(DisplayService, self).__init__(name="DisplayService")
        self.display_thread = None

    def initialize(self):
        self.display_thread = Thread(target=self.start)
        self.display_thread.setDaemon(True)
        self.display_thread.start()
        # TODO intent to tell available displays, usage help intent

    def start(self):
        DisplayStart()

    def stop(self):
        if self.display_thread is not None:
            pass
            #self.display_thread.terminate() # TODO whats the syntax?


def create_skill():
    return DisplayService()