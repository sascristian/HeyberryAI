import time
from os.path import abspath
from mycroft.messagebus.message import Message


def ensure_uri(s):
    """
        Interprete paths as file:// uri's

        Args:
            s: string to be checked

        Returns:
            if s is uri, s is returned otherwise file:// is prepended
    """
    if '://' not in s:
        return 'file://' + abspath(s)
    else:
        return s


class DisplayService():
    """
        DisplayService object for interacting with the display subsystem

        Args:
            emitter: eventemitter or websocket object
    """
    def __init__(self, emitter):
        self.emitter = emitter
        self.emitter.on('mycroft.display.service.pic_info_reply',
                        self._pic_info)
        self.info = None

    def _pic_info(self, message=None):
        """
            Handler for catching returning pic info
        """
        self.info = message.data

    def display(self, file_path, utterance=''):
        """ Start playback.

            Args:
                tracks: track uri or list of track uri's
                utterance: forward utterance for further processing by the
                           audio service.
        """
        if not isinstance(file_path, basestring):
            raise ValueError

        self.emitter.emit(Message('mycroft.display.service.display',
                                  data={'file_path': file_path,
                                        'utterance': utterance}))

    def next(self):
        """ Change to next track. """
        self.emitter.emit(Message('mycroft.display.service.next'))

    def prev(self):
        """ Change to previous track. """
        self.emitter.emit(Message('mycroft.display.service.prev'))

    def clear(self):
        """ Clear Display """
        self.emitter.emit(Message('mycroft.display.service.clear'))

    def reset(self):
        """ Reset Display. """
        self.emitter.emit(Message('mycroft.display.service.reset'))

    def pic_info(self):
        """ Request information of current displaying pic.

            Returns:
                Dict with pic info.
        """
        self.info = None
        self.emitter.emit(Message('mycroft.display.service.pic_info'))
        wait = 5.0
        while self.info is None and wait >= 0:
            time.sleep(0.1)
            wait -= 0.1

        return self.info or {}

    @property
    def is_playing(self):
        return self.track_info() != {}
