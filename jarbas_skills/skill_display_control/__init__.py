from mycroft.messagebus.message import Message
from mycroft.configuration import ConfigurationManager
from mycroft.skills.displayservice import DisplayService
from os.path import dirname
from mycroft.skills.core import MycroftSkill
from adapt.intent import IntentBuilder
from jarbas_utils.jarbas_services import url_to_pic
from time import sleep

config = ConfigurationManager.get().get('Displays')

__author__ = 'jarbas'


class DisplayControlSkill(MycroftSkill):
    def __init__(self):
        super(DisplayControlSkill, self).__init__()
        self.log.info('Display Control Started')
        self.reload_skill = False
        self.default_pic = dirname(__file__) + "/pixel jarbas.png"
        self.height = 500
        self.width = 500
        self.pics = []
        self.index = 0
        self.source = "unknown"

    def initialize(self):
        self.log.info('initializing Display Control Skill')
        self.display_service = DisplayService(self.emitter, self.name)
        self.display_service.set_width(self.width)
        self.display_service.set_height(self.height)

        current_intent = IntentBuilder("CurrentPicIntent").require(
            "PictureKeyword").require("CurrentKeyword").build()
        self.register_intent(current_intent, self.handle_currently_displaying)

        random_intent = IntentBuilder("RandomPicIntent").require(
            "PictureKeyword").require("RandomKeyword").optionally("ShowKeyword").build()
        self.register_intent(random_intent, self.handle_random)

        increase_intent = IntentBuilder("DisplayIncreaseIntent").require(
            "PictureKeyword").require("IncreaseKeyword").build()
        self.register_intent(increase_intent, self.handle_increase)

        decrease_intent = IntentBuilder("DisplayDecreaseIntent").require(
            "PictureKeyword").require("DecreaseKeyword").build()
        self.register_intent(decrease_intent, self.handle_decrease)

        display_intent = IntentBuilder("DisplayPicIntent").require(
            "PictureKeyword").require("ShowKeyword").build()
        self.register_intent(display_intent, self.handle_display)

        unset_fs_intent = IntentBuilder("UnsetPicFullscreenIntent").require(
            "PictureKeyword").require("UnsetKeyword").require(
            "FullscreenKeyword").build()
        self.register_intent(unset_fs_intent, self.handle_unset_fullscreen)

        set_fs_intent = IntentBuilder("SetPicFullscreenIntent").require(
            "PictureKeyword").require("SetKeyword").require(
            "FullscreenKeyword").build()
        self.register_intent(set_fs_intent, self.handle_set_fullscreen)

        width_intent = IntentBuilder("SetPicWidthIntent").require(
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

        self.emitter.on('mycroft.display.service.display',
                        self.handle_cache_pics)
        self.emitter.on('mycroft.display.service.add_pictures',
                        self.handle_cache_pics)

    def handle_cache_pics(self, message):
        self.log.info("Caching pictures")
        pics = message.data.get("file_list", [])
        reset = message.data.get("reset")
        index = message.data.get("index")
        self.source = message.context.get("source", "unknown")
        if index is not None:
            self.index = index
        if reset is not None:
            if reset:
                self.pics = pics
                if len(pics):
                    self.set_context("PicturePath", pics[0])
                return
        self.pics.extend(pics)
        if len(pics):
            self.set_context("PicturePath", pics[0])

    def handle_random(self, message):
        self.speak("Displaying random picture")
        pic = url_to_pic("https://unsplash.it/600/?random")
        self.display_service.display([pic], utterance=message.data.get(
            "utterance"))

    def handle_display(self, message):
        self.speak("Displaying")
        # display cached picture paths, allow for "display in backend" current pic
        self.display_service.display(self.pics,
                                     index=self.index,
                                     utterance=message.data.get("utterance"))

    def handle_close(self, message):
        self.index = 0
        self.pics = []
        self.width = 500
        self.height = 500
        self.speak("Closing display")
        self.display_service.close(utterance=message.data.get("utterance"))

    def handle_next(self, message):
        self.index += 1
        if self.index > len(self.pics):
            self.index = 0
        if len(self.pics):
            self.set_context("PicturePath", self.pics[self.index])
        self.speak("Displaying next picture")
        self.display_service.next(utterance=message.data.get("utterance"))

    def handle_prev(self, message):
        self.index -= 1
        if self.index > 0:
            self.index = len(self.pics)
        if len(self.pics):
            self.set_context("PicturePath", self.pics[self.index])
        self.speak("Displaying previous picture")
        self.display_service.prev(utterance=message.data.get("utterance"))

    def handle_reset(self, message):
        self.index = 0
        self.pics = []
        self.width = 500
        self.height = 500
        self.speak("Reseting picture list and window size")
        self.display_service.reset(utterance=message.data.get("utterance"))
        self.display_service.set_width(500, utterance=message.data.get("utterance"))
        self.display_service.set_height(500, utterance=message.data.get("utterance"))

    def handle_clear(self, message):
        self.speak("Clearing Display")
        self.display_service.clear(utterance=message.data.get("utterance"))

    def handle_start(self, message):
        self.speak("Starting Display")
        self.display_service.display([self.default_pic], reset=False,
                                     utterance=message.data.get("utterance"))

    def handle_stop(self, message):
        self.speak("Closing display")
        self.index = 0
        self.pics = []
        self.width = 500
        self.height = 500
        utterance = message.data.get("utterance")
        self.display_service.reset(utterance)
        self.display_service.close(utterance)

    def handle_decrease(self, message):
        self.speak("Decreasing Display size")
        h_ammount = self.height * 30 / 100
        w_ammount = self.width * 30 / 100
        self.width = self.width + w_ammount
        self.height = self.height + h_ammount
        self.display_service.set_width(self.width, message.data.get("utterance"))
        self.display_service.set_height(self.height, message.data.get("utterance"))
        self.display_service.display(reset=False)

    def handle_increase(self, message):
        self.speak("Increasing Display size")
        h_ammount = self.height * 30 / 100
        w_ammount = self.width * 30 / 100
        self.display_service.set_width(self.width + w_ammount, message.data.get("utterance"))
        self.display_service.set_height(self.height + h_ammount, message.data.get("utterance"))
        self.display_service.display(reset=False)

    def handle_set_width(self, message):
        width = message.data.get("TargetKeyword", 500)
        if not width.isdigit():
            self.speak("invalid width")
            return
        self.speak("Changing Display width to " + width)
        self.width = width
        self.display_service.set_width(int(width), message.data.get("utterance"))
        self.display_service.display(reset=False)

    def handle_set_height(self, message):
        height = message.data.get("TargetKeyword", 500)
        if not height.isdigit():
            self.speak("invalid height")
            return
        self.speak("Changing Display heigth to " + height)
        self.height = height
        self.display_service.set_height(int(height), message.data.get(
            "utterance"))
        self.display_service.display(reset=False)

    def handle_currently_displaying(self, message):
        if len(self.pics):
            self.speak("Currently displaying picture " + str(self.index)
                       + "from " + self.source)
        else:
            self.speak("Currently not displaying any pictures")

    def handle_set_fullscreen(self, message):
        self.speak("Setting fullscreen")
        self.display_service.set_fullscreen(True, message.data.get("utterance"))

    def handle_unset_fullscreen(self, message):
        self.speak("Unsetting fullscreen")
        self.display_service.set_fullscreen(False, message.data.get(
            "utterance"))

    def stop(self, message=None):
        pass
        #self.log.info("Stopping Display")
        #self.emitter.emit(Message('MycroftDisplayServiceStop'))


def create_skill():
    return DisplayControlSkill()