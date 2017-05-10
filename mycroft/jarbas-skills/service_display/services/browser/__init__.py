import sys
from os.path import dirname

# add display service folder to import path
path= dirname(dirname(__file__))
sys.path.append(path)
# import display service
from backend import DisplayBackend


from mycroft.util.log import getLogger
from os.path import abspath
import webbrowser

logger = getLogger(abspath(__file__).split('/')[-2])


class BrowserService(DisplayBackend):
    def __init__(self, config, emitter, name):
        super(BrowserService, self).__init__()
        self.config = config
        self.emitter = emitter
        self.name = name
        self.pic = ""

    def show(self, pic):
        logger.info('Call browserServiceShow')
        logger.info('Picture is ' + pic)
        # show in browser
        webbrowser.open(pic)

    def stop(self):
        logger.info('browserServiceStop')


def load_service(base_config, emitter):
    # TODO add prefered bowser option
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'browser']
    instances = [BrowserService(s[1], emitter, s[0]) for s in services]
    return instances