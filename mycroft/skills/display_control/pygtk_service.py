from mycroft.skills.displayservice import DisplayBackend
from mycroft.messagebus.message import Message
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
    def __init__(self, config, emitter, name='pygtk'):
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        self.pic = ""
        self.emitter.on('pygtkServiceShow', self._show)

    def show(self, pic):
        logger.info('Call pygtkServiceShow')
        self.emitter.emit(Message('pygtkServiceShow', {"pic": pic}))

    def _show(self, message):
        logger.info('pygtkService._Show')
        pic = message.data["pic"]
        # show in pygtk
        gtkimageshow(pic)
        gtk.main()

    def stop(self):
        logger.info('pygtkServiceStop')
        # TODO make this actually quit, how to send gtk destroy signal?
