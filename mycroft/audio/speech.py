from mycroft.tts import TTSFactory
from mycroft.util import create_signal, stop_speaking, check_for_signal
from mycroft.lock import Lock as PIDLock  # Create/Support PID locking file
from mycroft.configuration import ConfigurationManager
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger

from threading import Lock
import time
import re

logger = getLogger("Audio speech")

ws = None
config = None
tts = None
tts_hash = None
lock = Lock()

_last_stop_signal = 0
disable_speak_flag = False


def set_speak_flag(event):
    global disable_speak_flag
    disable_speak_flag = True


def unset_speak_flag(event):
    global disable_speak_flag
    disable_speak_flag = False


def handle_speak(event):
    """
        Handle "speak" message
    """
    config = ConfigurationManager.get()
    ConfigurationManager.init(ws)
    global _last_stop_signal

    utterance = event.data['utterance']
    expect_response = event.data.get('expect_response', False)
    mute = event.data.get("mute", False)
    target = event.data.get("target", "all")
    if target != "speech" and target != "all":
        return
    # This is a bit of a hack for Picroft.  The analog audio on a Pi blocks
    # for 30 seconds fairly often, so we don't want to break on periods
    # (decreasing the chance of encountering the block).  But we will
    # keep the split for non-Picroft installs since it give user feedback
    # faster on longer phrases.
    #
    # TODO: Remove or make an option?  This is really a hack, anyway,
    # so we likely will want to get rid of this when not running on Mimic
    if not mute:
        # Mild abuse of the signal system to allow other processes to detect
        # when TTS is happening.  See mycroft.util.is_speaking()
        create_signal("isSpeaking")
        if not config.get('enclosure', {}).get('platform') == "picroft":
            start = time.time()
            chunks = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s',
                              utterance)
            for chunk in chunks:
                try:
                    mute_and_speak(chunk)
                except:
                    logger.error('Error in mute_and_speak', exc_info=True)
                if _last_stop_signal > start or check_for_signal('buttonPress'):
                    break
        else:
            mute_and_speak(utterance)

    # This check will clear the "signal"
    check_for_signal("isSpeaking")

    if expect_response:
        create_signal('startListening')


def mute_and_speak(utterance):
    """
        Mute mic and start speaking the utterance using selected tts backend.

        Args:
            utterance: The sentence to be spoken
    """
    global tts_hash
    global tts
    global disable_speak_flag

    lock.acquire()
    # update TTS object if configuration has changed
    if tts_hash != hash(str(config.get('tts', ''))):
        tts = TTSFactory.create()
        tts.init(ws)
        tts_hash = hash(str(config.get('tts', '')))

    ws.emit(Message("mycroft.audio.speech.start"))
    try:
        logger.info("Speak: " + utterance)
        ws.emit(Message("mycroft.mic.mute"))

        if not disable_speak_flag:
            tts.execute(utterance)
    finally:
        ws.emit(Message("mycroft.mic.unmute"))
        lock.release()
        ws.emit(Message("mycroft.audio.speech.end"))


def handle_stop(event):
    """
        handle stop message
    """
    global _last_stop_signal
    _last_stop_signal = time.time()
    stop_speaking()


def init(websocket):
    """
        Start speach related handlers
    """

    global ws
    global tts
    global tts_hash
    global config

    ws = websocket
    ConfigurationManager.init(ws)
    config = ConfigurationManager.get()
    ws.on('mycroft.stop', handle_stop)
    ws.on('speak', handle_speak)
    ws.on('do_not_speak_flag_enable', set_speak_flag)
    ws.on('do_not_speak_flag_disable', unset_speak_flag)

    tts = TTSFactory.create()
    tts.init(ws)
    tts_hash = config.get('tts')
