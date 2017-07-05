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


import re
import sys
from threading import Thread, Lock
import time

from mycroft.client.enclosure.api import EnclosureAPI
from mycroft.client.speech.listener import RecognizerLoop
from mycroft.configuration import ConfigurationManager
from mycroft.identity import IdentityManager
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from mycroft.tts import TTSFactory
from mycroft.util import kill, create_signal, check_for_signal, stop_speaking
from mycroft.util.log import getLogger
from mycroft.lock import Lock as PIDLock  # Create/Support PID locking file

logger = getLogger("SpeechClient")
ws = None
lock = Lock()
loop = None

config = ConfigurationManager.get()

disable_speak_flag = False


def handle_record_begin():
    logger.info("Begin Recording...")
    ws.emit(Message('recognizer_loop:record_begin'))


def handle_record_end():
    logger.info("End Recording...")
    ws.emit(Message('recognizer_loop:record_end'))


def handle_no_internet():
    logger.debug("Notifying enclosure of no internet connection")
    ws.emit(Message('enclosure.notify.no_internet'))


def handle_wakeword(event):
    logger.info("Wakeword Detected: " + event['utterance'])
    ws.emit(Message('recognizer_loop:wakeword', event))


def handle_utterance(event):
    logger.info("Utterance: " + str(event['utterances']))
    event["source"] = "speech"
    ws.emit(Message('recognizer_loop:utterance', event))


def set_speak_flag(event):
    global disable_speak_flag
    disable_speak_flag = True


def unset_speak_flag(event):
    global disable_speak_flag
    disable_speak_flag = False


def handle_multi_utterance_intent_failure(event):
    logger.info("Failed to find intent on multiple intents.")
    # TODO: Localize
    ws.emit(Message('speak', {"utterance": "Sorry, I didn't catch that. Please rephrase your request."}))


def handle_sleep(event):
    loop.sleep()


def handle_wake_up(event):
    loop.awaken()


def handle_mic_mute(event):
    if not loop.is_muted():
        loop.mute()


def handle_mic_unmute(event):
    if loop.is_muted():
        loop.unmute()


def handle_stop(event):
    global _last_stop_signal
    _last_stop_signal = time.time()
    stop_speaking()


def handle_paired(event):
    IdentityManager.update(event.data)


def handle_open():
    # TODO: Move this into the Enclosure (not speech client)
    # Reset the UI to indicate ready for speech processing
    EnclosureAPI(ws).reset()


def connect():
    ws.run_forever()


def main():
    global ws
    global loop
    global config
    lock = PIDLock("voice")
    ws = WebsocketClient()
    config = ConfigurationManager.get()
    ConfigurationManager.init(ws)
    loop = RecognizerLoop()
    loop.on('recognizer_loop:utterance', handle_utterance)
    loop.on('recognizer_loop:record_begin', handle_record_begin)
    loop.on('recognizer_loop:wakeword', handle_wakeword)
    loop.on('recognizer_loop:record_end', handle_record_end)
    loop.on('recognizer_loop:no_internet', handle_no_internet)
    ws.on('open', handle_open)
    ws.on(
        'multi_utterance_intent_failure',
        handle_multi_utterance_intent_failure)
    ws.on('recognizer_loop:sleep', handle_sleep)
    ws.on('recognizer_loop:wake_up', handle_wake_up)
    ws.on('mycroft.mic.mute', handle_mic_mute)
    ws.on('mycroft.mic.unmute', handle_mic_unmute)
    ws.on("mycroft.paired", handle_paired)
    ws.on('do_not_speak_flag_enable', set_speak_flag)
    ws.on('do_not_speak_flag_disable', unset_speak_flag)
    event_thread = Thread(target=connect)
    event_thread.setDaemon(True)
    event_thread.start()

    try:
        loop.run()
    except KeyboardInterrupt, e:
        logger.exception(e)
        event_thread.exit()
        sys.exit()


if __name__ == "__main__":
    main()
