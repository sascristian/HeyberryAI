from adapt.engine import IntentDeterminationEngine
from adapt.intent import Intent
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

__author__ = 'jarbas'

logger = getLogger(__name__)


class IntentParser():
    def __init__(self, emitter):
        self.engine = IntentDeterminationEngine()
        self.emitter = emitter
        self.reply = None
        self.emitter.on('register_vocab', self.handle_register_vocab)
        self.emitter.on('detach_intent', self.handle_detach_intent)

    def register_intent(self, intent_dict):
        intent = Intent(intent_dict.get('name'),
                      intent_dict.get('requires'),
                      intent_dict.get('at_least_one'),
                      intent_dict.get('optional'))
        self.engine.register_intent_parser(intent)

    def determine_intent(self, utterances):
        best_intent = None
        self.reply = None
        for utterance in utterances:
            try:
                best_intent = next(self.engine.determine_intent(
                    utterance, 100))
                # TODO - Should Adapt handle this?
                best_intent['utterance'] = utterance
            except StopIteration, e:
                logger.exception(e)
                continue
        if best_intent and best_intent.get('confidence', 0.0) > 0.0:
            self.reply = Message(best_intent.get('intent_type'), best_intent)
            return True, best_intent

        return False, best_intent

    def execute_intent(self):
        if self.reply is not None:
            self.emitter.emit(self.reply)
            # self.reply = None #actually its nice to be able to call execute_intent as many times as wanted
            return True
        return False

    def handle_register_vocab(self, message):
        start_concept = message.data.get('start')
        end_concept = message.data.get('end')
        regex_str = message.data.get('regex')
        alias_of = message.data.get('alias_of')
        if regex_str:
            self.engine.register_regex_entity(regex_str)
        else:
            self.engine.register_entity(
                start_concept, end_concept, alias_of=alias_of)

    def handle_detach_intent(self, message):
        intent_name = message.data.get('intent_name')
        new_parsers = [
            p for p in self.engine.intent_parsers if p.name != intent_name]
        self.engine.intent_parsers = new_parsers
