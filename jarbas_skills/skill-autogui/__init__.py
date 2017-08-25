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

from adapt.intent import IntentBuilder

from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from os.path import dirname

import pyautogui
import platform
from PIL import ImageDraw, ImageFont

from num2words import num2words

# TODO handle no DisplayService, using PIL? im.show() fails for me
from mycroft.skills.displayservice import DisplayService

__author__ = 'eClarity'

LOGGER = getLogger(__name__)


class AutoguiSkill(MycroftSkill):
    def __init__(self):
        super(AutoguiSkill, self).__init__(name="AutoguiSkill")
        screen = pyautogui.size()
        self.resx = screen[0]
        self.resy = screen[1]
        self.boundings = []
        self.grid = False

    def initialize(self):
        self.display_service = DisplayService(self.emitter)

        type_intent = IntentBuilder("TypeIntent"). \
            require("TypeKeyword").require("Text").build()
        self.register_intent(type_intent, self.handle_type_intent)

        intent = IntentBuilder("ActivateMouseClickGridIntent"). \
            require("GridKeyword").require("EnableKeyword").build()
        self.register_intent(intent,
                             self.handle_activate_grid_intent)

        intent = IntentBuilder("ResetMouseClickGridIntent"). \
            require("GridKeyword").require("ResetKeyword").build()
        self.register_intent(intent,
                             self.handle_reset_grid_intent)

        intent = IntentBuilder("DeactivateMouseClickGridIntent"). \
            require("GridKeyword").require("DisableKeyword").build()
        self.register_intent(intent,
                             self.handle_deactivate_grid_intent)

        intent = IntentBuilder("ZoomMouseClickGridIntent"). \
            optionally("GridKeyword").require("ZoomKeyword")\
            .require("TargetKeyword").build()
        self.register_intent(intent,
                             self.handle_zoom_grid_intent)

        intent = IntentBuilder("GridMouseClickGridIntent"). \
            optionally("GridKeyword").require("ClickKeyword")\
            .require("TargetKeyword").build()
        self.register_intent(intent,
                             self.handle_click_grid_intent)

        mouse_click_intent = IntentBuilder("MouseClickIntent"). \
            optionally("MouseKeyword").require("ClickKeyword").build()
        self.register_intent(mouse_click_intent,
                             self.handle_mouse_click_intent)

        mouse_pos_intent = IntentBuilder("MousePositionIntent"). \
            require("MouseKeyword").require("PositionKeyword").build()
        self.register_intent(mouse_pos_intent,
                             self.handle_mouse_position_intent)

        mouse_absolute_intent = IntentBuilder("MouseAbsoluteIntent"). \
            require("MouseAbsoluteKeyword").require("X").require("Y").build()
        self.register_intent(mouse_absolute_intent,
                             self.handle_mouse_absolute_intent)

        mouse_scroll_down_intent = IntentBuilder("MouseScrollDownIntent"). \
            optionally("MouseKeyword").require(
            "MouseScrollDownKeyword").require("Scroll").build()
        self.register_intent(mouse_scroll_down_intent,
                             self.handle_mouse_scroll_down_intent)

        mouse_scroll_up_intent = IntentBuilder("MouseScrollUpIntent"). \
            optionally("MouseKeyword").require("MouseScrollUpKeyword").require(
            "Scroll").build()
        self.register_intent(mouse_scroll_up_intent,
                             self.handle_mouse_scroll_up_intent)

        mouse_scroll_right_intent = IntentBuilder("MouseScrollRightIntent"). \
            optionally("MouseKeyword").require(
            "MouseScrollRightKeyword").require("Scroll").build()
        self.register_intent(mouse_scroll_right_intent,
                             self.handle_mouse_scroll_right_intent)

        screen_res_intent = IntentBuilder("ScreenResIntent"). \
            require("ScreenResKeyword").build()
        self.register_intent(screen_res_intent, self.handle_screen_res_intent)

        press_key_intent = IntentBuilder("PressKeyIntent"). \
            require("PressKeyKeyword").require("Key").build()
        self.register_intent(press_key_intent, self.handle_press_key_intent)

        hold_key_intent = IntentBuilder("HoldKeyIntent"). \
            require("HoldKeyKeyword").require("Key").build()
        self.register_intent(hold_key_intent, self.handle_hold_key_intent)

        release_key_intent = IntentBuilder("ReleaseKeyIntent"). \
            require("ReleaseKeyKeyword").require("Key").build()
        self.register_intent(release_key_intent, self.handle_release_key_intent)

    def get_grid(self, path=None, num=-1):
        if path is None:
            path = dirname(__file__) + "/screenshot.jpg"
        img = pyautogui.screenshot(path)
        draw = ImageDraw.Draw(img)
        if num >= 1 and len(self.boundings):
            box = self.boundings[num]
            img = img.crop((box[0], box[1], box[2], box[3]))
            self.grid_reference = [box[0], box[1]]
        w, h = img.size
        self.w = x = w / 3
        self.h = y = h / 3
        # draw vertical lines
        i = 0
        while i < 4:
            draw.line(((x * i, 0), (x * i, h)), fill=(255, 0, 0), width=5)
            i += 1
        # draw horizontal lines
        i = 0
        while i < 4:
            draw.line(((0, y * i), (w, y * i)), fill=(255, 0, 0), width=5)
            i += 1
        # save bounding boxes
        num = 0
        for o in range(0, 3):
            for i in range(0, 3):
                num += 1
                box = [x * i, o * y, x, y]
                self.boundings.append(box)
        # draw nums
        for num in range(1, 10):
            box = self.boundings[num - 1]
            x = box[2] / 2 + box[0]
            y = box[3] / 2 + box[1]
            font = ImageFont.truetype(dirname(__file__) + "/METALORD.TTF", 30)
            draw.text((x, y), str(num), (255, 0, 0), font)
        img.save(path)
        return path

    def handle_activate_grid_intent(self, message):
        self.set_context("GridKeyword", "grid")
        if self.grid:
            self.speak("grid is already active")
            return
        self.speak("Grid activated")
        self.set_context("GridKeyword", "grid")
        path = self.get_grid()
        self.grid = True
        self.display_service.set_fullscreen(True, utterance=message.data.get(
            "utterance"))
        self.display_service.display([path], utterance=message.data.get(
            "utterance"))

    def handle_deactivate_grid_intent(self, message):
        self.set_context("GridKeyword", "grid")
        if not self.grid:
            self.speak("Grid is already deactivated")
            return
        self.boundings = []
        self.speak("Grid deactivated")
        self.grid = False
        self.display_service.set_fullscreen(False, utterance=message.data.get(
            "utterance"))
        self.display_service.clear(utterance=message.data.get(
            "utterance"))

    def handle_reset_grid_intent(self, message):
        self.set_context("GridKeyword", "grid")
        if not self.grid:
            self.handle_activate_grid_intent(message)
            return
        self.speak("Grid reset")
        self.grid_reference = [0, 0]
        path = self.get_grid(num=-1)
        self.display_service.display([path], utterance=message.data.get(
            "utterance"))

    def handle_zoom_grid_intent(self, message):
        self.set_context("GridKeyword", "grid")
        if not self.grid:
            self.speak("you must activate grid first")
            return
        num = message.data.get("TargetKeyword")
        if not num.isdigit():
            self.speak("bad input")
            return
        num = int(num)
        if num < 0 or num > 9:
            self.speak("bad number")
            return
        self.speak("zooming to number " + str(num))
        path = self.get_grid(num=num)
        self.display_service.display([path], utterance=message.data.get(
            "utterance"))

    def handle_click_grid_intent(self, message):
        self.set_context("GridKeyword", "grid")
        if not self.grid:
            self.speak("you must activate grid first")
            return
        num = message.data.get("TargetKeyword", "")
        if not num.isdigit():
            self.speak("bad input")
            return
        num = int(num)
        if num < 1 or num > 9:
            self.speak("bad number")
            return
        x = self.grid_reference[0] + self.w / 2
        y = self.grid_reference[1] + self.h / 2
        # deactivate grid cause we dont want to click in picture
        self.handle_deactivate_grid_intent(message)
        self.speak("clicking " + str(num))
        # move mouse to look better and work as a delay for grid to deactivate
        pyautogui.moveTo(x, y, duration=2)
        pyautogui.click(x, y)

    def handle_mouse_position_intent(self, message):
        pos = pyautogui.recordMousePositions(amount=1)[0]
        self.speak("mouse position is")
        self.speak("x " + str(pos[0]) + " y " + str(pos[1]))

    def handle_mouse_click_intent(self, message):
        self.speak("clicking mouse")
        pyautogui.click()

    def handle_type_intent(self, message):
        self.speak_dialog("typing")
        text = message.data.get('Text')
        pyautogui.typewrite(text, interval=0.05)

    def handle_mouse_absolute_intent(self, message):
        self.speak('moving mouse now')
        X = message.data.get('X')
        Y = message.data.get('Y')
        # pyautogui.moveTo(X, Y)

    def handle_mouse_scroll_down_intent(self, message):
        self.speak('scrolling down now')
        scroll = message.data.get('Scroll')
        scroll_down = int(scroll) * -1
        pyautogui.scroll(scroll_down)

    def handle_mouse_scroll_up_intent(self, message):
        self.speak('scrolling up now')
        scroll = message.data.get('Scroll')
        scroll_up = int(scroll)
        pyautogui.scroll(scroll_up)

    def handle_mouse_scroll_right_intent(self, message):
        if platform.system().lower().startswith('lin'):
            self.speak('scrolling right now')
            scroll = message.data.get('Scroll')
            scroll_right = int(scroll)
            pyautogui.hscroll(scroll_right)
        else:
            self.speak(
                'Sorry, I cannot scroll right on your current operating system')

    def handle_screen_res_intent(self, message):
        screen = pyautogui.size()
        self.resx = screen[0]
        self.resy = screen[1]
        responsex = num2words(self.resx)
        responsey = num2words(self.resy)
        self.speak(
            "Your screen resolution is %s by %s" % (responsex, responsey))

    def handle_press_key_intent(self, message):
        key = message.data.get('Key')
        self.speak("Pressing %s" % key)
        pyautogui.keyDown(key)
        pyautogui.keyUp(key)

    def handle_hold_key_intent(self, message):
        key = message.data.get('Key')
        self.speak("Holding down %s key" % key)
        pyautogui.keyDown(key)

    def handle_release_key_intent(self, message):
        key = message.data.get('Key')
        self.speak("Releasing %s key" % key)
        pyautogui.keyUp(key)

    def stop(self):
        pass


def create_skill():
    return AutoguiSkill()
