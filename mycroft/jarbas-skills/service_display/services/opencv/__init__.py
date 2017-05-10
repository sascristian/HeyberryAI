import sys
from os.path import dirname
# add display service folder to import path
path= dirname(dirname(__file__))
sys.path.append(path)
# import display service
from backend import DisplayBackend


from mycroft.util.log import getLogger
from os.path import abspath
import imutils
import cv2

logger = getLogger(abspath(__file__).split('/')[-2])


class OpenCVService(DisplayBackend):
    def __init__(self, config, emitter, name='opencv'):
        super(OpenCVService, self).__init__()
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        # image size
        self.width = 500
        self.height = 500

    def show(self, pic):
        logger.info('Call OpenCVServiceShow')
        # show in opencv2
        image = cv2.imread(pic)
        image = imutils.resize(image, self.width, self.height)
        # Process finished with exit code 139 (interrupted by signal 11: SIGSEGV)
        #  SIGSEGV 139 attempt to access a virtual address which is not in your address space
        cv2.imshow("OpenCV Display", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def stop(self):
        logger.info('OpenCVServiceStop')
        cv2.destroyAllWindows()

def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'opencv']
    instances = [OpenCVService(s[1], emitter, s[0]) for s in services]
    return instances