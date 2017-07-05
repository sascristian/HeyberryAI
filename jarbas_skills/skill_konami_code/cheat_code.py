from mycroft.messagebus.message import Message
from mycroft.skills.intent_service import IntentParser


class CheatCode():
    def __init__(self, emitter):
        self.emitter = emitter
        self.parser = IntentParser(self.emitter)

    def speak(self, utterance):
        self.emitter.emit(Message("speak", {"utterance": utterance, "target":"all", "mute":False, "more":False, "metadata":{"source":"cheat_code"}}))

    def execute_intent(self, intent_name, params_dict=None):
        intent_name = str(self.parser.get_skill_id(intent_name))+":"+intent_name
        if params_dict is None:
            params_dict = {}
        self.emitter.emit(Message(intent_name, params_dict))

    def execute_cheat_code(self):
        self.speak("God Mode Activated")
        self.execute_intent("WikipediaIntent", {"ArticleTitle": "Konami Code"})
