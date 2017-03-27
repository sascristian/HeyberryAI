from mycroft.messagebus.message import Message


class DisplayService():
    def __init__(self, emitter):
        self.emitter = emitter

    def show(self, pic="", utterance=''):
        self.emitter.emit(Message('MycroftDisplayServiceShow',
                                  data={'picture': pic,
                                        'utterance': utterance}))