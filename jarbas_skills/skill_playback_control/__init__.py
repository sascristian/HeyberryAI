from os.path import abspath
from mycroft.messagebus.message import Message
from mycroft.configuration import ConfigurationManager
from mycroft.skills.audioservice import AudioService
from os.path import dirname
from mycroft.skills.media import MediaSkill
from mycroft.util.log import getLogger


config = ConfigurationManager.get().get('Audio')
logger = getLogger(abspath(__file__).split('/')[-2])
__author__ = 'forslund'


class PlaybackControlSkill(MediaSkill):
    def __init__(self):
        super(PlaybackControlSkill, self).__init__('Playback Control Skill')
        logger.info('Playback Control Inited')

    def initialize(self):
        logger.info('initializing Playback Control Skill')
        super(PlaybackControlSkill, self).initialize()
        self.load_data_files(dirname(__file__))
        self.audio_service = AudioService(self.emitter)

    def handle_next(self, message):
        self.audio_service.next()

    def handle_prev(self, message):
        self.audio_service.prev()

    def handle_pause(self, message):
        self.audio_service.pause()

    def handle_play(self, message):
        """Resume playback if paused"""
        self.audio_service.resume()

    def handle_currently_playing(self, message):
        return

    def stop(self, message=None):
        logger.info("Stopping audio")
        self.emitter.emit(Message('MycroftAudioServiceStop'))


def create_skill():
    return PlaybackControlSkill()