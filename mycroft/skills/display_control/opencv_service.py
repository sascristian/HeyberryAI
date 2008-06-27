from mycroft.skills.displayservice import DisplayBackend
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger
from os.path import abspath
import cv2
import imutils

logger = getLogger(abspath(__file__).split('/')[-2])

class OpenCVService(DisplayBackend):
    def __init__(self, config, emitter, name='opencv'):
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        self.index = 0
        self.emitter.on('OpenCVServiceShow', self.display)

    def clear_list(self):
        self.pics = []
        self.index = 0

    def add_list(self, pics):
        self.pics = pics
        logger.info("Pic is " + str(pics))

    def show(self):
        logger.info('Call OpenCVServiceShow')
        self.index = 0
        self.emitter.emit(Message('OpenCVServiceShow'))

    def display(self, message):
        logger.info('OpenCVService._Show')
        pic = self.pics[self.index]
        # show in opencv2
        image = cv2.imread(pic)
        image = imutils.resize(image, 500, 500)
        cv2.imshow(pic, image)
        cv2.waitKey(500)

    def stop(self):
        logger.info('OpenCVServiceStop')
        self.clear_list()
        cv2.destroyAllWindows()

    def next(self):
        if len(self.pics) > self.index:
            self.index += 1
        else:
            self.index = 0
        self.show("")

    def previous(self):
        self.index -= 1
        if self.index < 0:
            self.index = 0
        self.show("")
