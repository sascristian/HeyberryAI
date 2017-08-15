from mycroft.messagebus.message import Message
from mycroft.configuration import ConfigurationManager
from mycroft.skills.displayservice import DisplayService
from os.path import dirname
from mycroft.skills.core import MycroftSkill
from adapt.intent import IntentBuilder

config = ConfigurationManager.get().get('Displays')

__author__ = 'jarbas'


class DisplayControlSkill(MycroftSkill):
    def __init__(self):
        super(DisplayControlSkill, self).__init__(name="DisplayControlSkill")
        self.log.info('Display Control Started')

    def initialize(self):
        self.log.info('initializing Display Control Skill')
        super(DisplayControlSkill, self).initialize()
        self.load_data_files(dirname(__file__))
        self.display_service = DisplayService(self.emitter)

        clear_intent = IntentBuilder("ClearPicIntent").require(
            "PictureKeyword").require("ClearKeyword").build()
        self.register_intent(clear_intent, self.handle_clear)

        reset_intent = IntentBuilder("ResetPicIntent").require(
            "PictureKeyword").require("ResetKeyword").build()
        self.register_intent(reset_intent, self.handle_reset)

        next_intent = IntentBuilder("NextPicIntent").require(
            "PictureKeyword").require("NextKeyword").build()
        self.register_intent(next_intent, self.handle_next)

        prev_intent = IntentBuilder("PrevPicIntent").require(
            "PictureKeyword").require("PrevKeyword").build()
        self.register_intent(prev_intent, self.handle_prev)

        close_intent = IntentBuilder("ClosePicIntent").require(
            "PictureKeyword").require("CloseKeyword").build()
        self.register_intent(close_intent, self.handle_close)

    def handle_close(self, message):
        self.display_service.close()

    def handle_next(self, message):
        self.display_service.next()

    def handle_prev(self, message):
        self.display_service.prev()

    def handle_reset(self, message):
        self.display_service.reset()

    def handle_clear(self, message):
        self.display_service.clear()

    def handle_currently_displaying(self, message):
        return

    def stop(self, message=None):
        self.log.info("Stopping Display")
        self.emitter.emit(Message('MycroftDisplayServiceStop'))


def create_skill():
    return DisplayControlSkill()