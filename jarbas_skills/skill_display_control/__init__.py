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
        self.reload_skill = False

    def initialize(self):
        self.log.info('initializing Display Control Skill')
        super(DisplayControlSkill, self).initialize()
        self.load_data_files(dirname(__file__))
        self.display_service = DisplayService(self.emitter)

        unset_fs_intent = IntentBuilder("UnsetPicFullscreenIntent").require(
            "PictureKeyword").require("UnsetKeyword").require(
            "FullscreenKeyword").build()
        self.register_intent(unset_fs_intent, self.handle_unset_fullscreen)

        set_fs_intent = IntentBuilder("SetPicFullscreenIntent").require(
            "PictureKeyword").require("SetKeyword").require(
            "FullscreenKeyword").build()
        self.register_intent(set_fs_intent, self.handle_set_fullscreen)

        width_intent = IntentBuilder("SetPicHeightIntent").require(
            "PictureKeyword").require("SetKeyword").require(
            "TargetKeyword").require("WidthKeyword").build()
        self.register_intent(width_intent, self.handle_set_width)

        height_intent = IntentBuilder("SetPicHeightIntent").require(
            "PictureKeyword").require("SetKeyword").require(
            "TargetKeyword").require("HeightKeyword").build()
        self.register_intent(height_intent, self.handle_set_height)

        stop_intent = IntentBuilder("StopPicIntent").require(
            "PictureKeyword").require("StopKeyword").build()
        self.register_intent(stop_intent, self.handle_stop)

        start_intent = IntentBuilder("StartPicIntent").require(
            "PictureKeyword").require("StartKeyword").build()
        self.register_intent(start_intent, self.handle_start)

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

        self.handle_start(Message("dummy"))

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

    def handle_start(self, message):
        pic = dirname(__file__) + "/pixel jarbas.png"
        self.display_service.display([pic], "start opencv display")
        #self.display_service.reset()

    def handle_stop(self, message):
        utterance = message.data.get("utterance")
        self.display_service.reset()
        self.display_service.close(utterance)

    def handle_currently_displaying(self, message):
        return

    def handle_set_width(self, message):
        width = message.data.get("TargetKeyword", 500)
        if not width.isdigit():
            self.speak("invalid width")
            return
        self.display_service.set_width(width, message.data.get("utterance"))

    def handle_set_height(self, message):
        height = message.data.get("TargetKeyword", 500)
        if not height.isdigit():
            self.speak("invalid height")
            return
        self.display_service.set_height(height, message.data.get("utterance"))

    def handle_set_fullscreen(self, message):
        self.display_service.set_fullscreen(True, message.data.get("utterance"))

    def handle_unset_fullscreen(self, message):
        self.display_service.set_fullscreen(False, message.data.get(
            "utterance"))

    def stop(self, message=None):
        self.log.info("Stopping Display")
        self.emitter.emit(Message('MycroftDisplayServiceStop'))


def create_skill():
    return DisplayControlSkill()