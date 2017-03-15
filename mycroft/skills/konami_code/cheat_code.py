

from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from threading import Thread
from time import sleep

# cheat code script imports


# connect to message bus to interact with mycroft

client = WebsocketClient()

def connect():
    global client
    client.run_forever()

event_thread = Thread(target=connect)
event_thread.setDaemon(True)
event_thread.start()

# wait for thread to connect
sleep(1)


# helper functions
def execute_intent(intent_name, params_dict=None):
    if params_dict is None:
        params_dict = {}
    client.emit(Message(intent_name , params_dict))


def speak(utterance):
    client.emit(Message("speak",{"utterance":utterance}))


# cheat code script
speak("God Mode Activated")
# first line just in case using pr#558 https://github.com/MycroftAI/mycroft-core/pull/558  14/3/2017
execute_intent("WikipediaSkill:WikipediaIntent",{"ArticleTitle":"Konami Code"})
execute_intent("WikipediaIntent",{"ArticleTitle":"Konami Code"})