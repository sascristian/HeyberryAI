import sys
from os.path import dirname, abspath

from mycroft.skills.core import MycroftSkill
from mycroft.configuration import ConfigurationManager
from mycroft.skills.display_control.opencv_service import OpenCVService
from mycroft.skills.display_control.pygtk_service import GTKService
from mycroft.util.log import getLogger

config = ConfigurationManager.get().get('Displays')
logger = getLogger(abspath(__file__).split('/')[-2])

__author__ = 'jarbas'

sys.path.append(abspath(dirname(__file__)))


class DisplayControlSkill(MycroftSkill):
    def __init__(self):
        super(DisplayControlSkill, self).__init__('Display Control Skill')
        self.current = None
        self.default = None
        logger.info('Display Control Initiated')
        self.service = []

    def initialize(self):
        logger.info('initializing Display Control Skill')

        for name in config['backends']:
            b = config['backends'][name]
            logger.debug(b)
            if b['type'] == 'opencv' and b.get('active', False):
                logger.info('starting OpenCV service')
                self.service.append(OpenCVService(b, self.emitter, name))
            if b['type'] == 'pygtk' and b.get('active', False):
                logger.info('starting PyGTK service')
                self.service.append(GTKService(b, self.emitter, name))

        default_name = config.get('default-backend', '')
        for s in self.service:
            if s.name == default_name:
                self.default = s
                break
        else:
            self.default = None
        logger.info(self.default)

        self.emitter.on('MycroftDisplayServiceShow', self._show)

    def show(self, pic, prefered_service):
        logger.info('show')
        self.stop()
        # check if user requested a particular service
        if prefered_service:
            service = prefered_service
        elif self.default:
            logger.info("Using default backend")
            logger.info(self.default.name)
            service = self.default
        else:
            logger.error("NO DEFAULT DISPLAY BACKEND")
            return

        logger.info('Displaying')
        service.show(pic)
        self.current = service

    def _show(self, message):
        logger.info('MycroftDisplayServiceShow')
        logger.info(message.data['picture'])

        pic = message.data['picture']

        # Find if the user wants to use a specific backend
        for s in self.service:
            logger.info(s.name)
            if s.name in message.data['utterance']:
                prefered_service = s
                logger.info(s.name + ' would be prefered')
                break
        else:
            prefered_service = None
        self.show(pic, prefered_service)

    def stop(self, message=None):
        logger.info('stopping all displaying services')
        if self.current:
            self.current.stop()
            self.current = None


def create_skill():
    return DisplayControlSkill()
