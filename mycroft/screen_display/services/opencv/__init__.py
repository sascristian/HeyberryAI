from mycroft.screen_display.services import DisplayBackend
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

from os.path import abspath

import imutils
import cv2

__author__ = 'jarbas'

logger = getLogger(abspath(__file__).split('/')[-2])


class OpenCVService(DisplayBackend):
    """
        Display backend for opencv package.
    """
    def __init__(self, config, emitter, name='OpenCV'):
        self.config = config
        self.emitter = emitter
        self.name = name
        self._is_Displaying = False
        self.pictures = []
        self.index = 0
        self.emitter.on('mycroft.display.service.OpenCV', self._display)
        # image size
        self.width = 500
        self.height = 500

    def _display(self, message=None):
        """
        Open file with opencv
        """
        logger.info(self.name + '_display')
        if len(self.pictures) == 0:
            logger.error("No picture to display")
            return
        path = self.pictures[self.index]
        self._is_Displaying = True
        image = cv2.imread(path)
        image = imutils.resize(image, self.width, self.height)
        # Process finished with exit code 139 (interrupted by signal 11: SIGSEGV)
        #  SIGSEGV 139 attempt to access a virtual address which is not in your address space
        cv2.imshow("OpenCV Display", image)
        cv2.waitKey(1)

    def display(self, pictures):
        pictures = pictures.reverse()
        for picture in pictures:
            self.pictures.insert(0, picture)
        logger.info('Call OpenCVDisplay')
        self.emitter.emit(Message('mycroft.display.service.OpenCV'))

    def next(self):
        """
            Skip to next pic in playlist.
        """
        logger.info('Call OpenCVNext')
        self.index += 1
        self._display()

    def previous(self):
        """
            Skip to previous pic in playlist.
        """
        logger.info('Call OpenCVPrevious')
        self.index -= 1
        self._display()

    def reset(self):
        """
            Reset Display.Clear Picture List, Clear Screen
        """
        logger.info('Call OpenCVReset')
        self.index = 0
        self.pictures = []
        self.clear()

    def clear(self):
        """
            Clear Display.
        """
        self._is_Displaying = False

    def stop(self):
        logger.info('OpenCVDisplayStop')
        cv2.destroyAllWindows()


def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'opencv']
    instances = [OpenCVService(s[1], emitter, s[0]) for s in services]
    return instances
