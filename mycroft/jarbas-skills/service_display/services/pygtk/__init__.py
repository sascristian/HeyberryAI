import sys
from os.path import dirname
# add display service folder to import path
path= dirname(dirname(__file__))
sys.path.append(path)
# import display service
from backend import DisplayBackend

from mycroft.util.log import getLogger
from os.path import abspath
import gtk

logger = getLogger(abspath(__file__).split('/')[-2])


class gtkimageshow(gtk.Window):
    def __init__(self, path):
        super(gtkimageshow, self).__init__()
        # quit button
        self.connect("destroy", gtk.main_quit)
        # set title
        self.set_title("Pygtk Display")
        # create pic widget
        image = gtk.Image()
        image.set_from_file(path)
        # add pic widget box to window
        self.add(image)
        # show
        self.show_all()

class GTKService(DisplayBackend):
    def __init__(self, config, emitter, name):
        super(GTKService, self).__init__()
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        self.pic = ""

    def show(self, pic):
        logger.info('Call pygtkServiceShow')
        logger.info('Picture is ' + pic)
        # show in pygtk
        gtkimageshow(pic)
        gtk.main()

    def stop(self):
        logger.info('pygtkServiceStop')
        # TODO make this actually quit, how to send gtk destroy signal?

def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'pygtk']
    instances = [GTKService(s[1], emitter, s[0]) for s in services]
    return instances