from mycroft.context import Context, FreeWillContext,VisionContext
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message

from threading import Thread
import time

def main():
    ####context manager bus listener

    context_general = Context("general")
    freewill_context = FreeWillContext("general_freewill")
    vision_context = VisionContext("general_vision")
    ##### connect to messagebus

    client = WebsocketClient()

    def connect():
        client.run_forever()

    ####### on context_result, listen for more signals if needed

    def vision(message):
        vision_context.asctime = message.data.get('asctime')
        vision_context.time = message.data.get('time')
        vision_context.movement = message.data.get('movement')
        vision_context.number = message.data.get('number of persons')
        vision_context.master = message.data.get('master')
        vision_context.smile = message.data.get('smile detected')
        vision_context.update()

    def freewill(message):
        freewill_context.dopamine = message.data.get('dopamine')
        freewill_context.serotonine = message.data.get('serotonine')
        freewill_context.tiredness = message.data.get('tiredness')
        freewill_context.tought = message.data.get('last_tought')
        freewill_context.action = message.data.get('last_action')
        freewill_context.mood = message.data.get('mood')

    def speak(message):
        context_general.lastutterance = message.data.get('utterance')

    def utterance(message):
        context_general.lastorder = message.data.get('utterances')

    def results(message):
        #parse only relevant skills, add context skill to change some properties like location
        context_general.lastaction = message.data.get('skill_name') #must send results in skill, NOT default
        # time skill
        if context_general.lastresults == "TimeSkill":
            context_general.time = message.data.get('time')
            context_general.timezone = message.data.get('timezone')
        # TODO
            # weather skill
            # IP skill
            # dream skill and remove flag from freewill context

    #####  send current context

    def requested(target):
        #emit unified response from all contexts?
        client.emit(
            Message("context_result",
                    {
                     'time': context_general.time,
                     'timezone': context_general.timezone,
                     'location': context_general.location,
                     'last action': context_general.lastaction,
                     'last utterance': context_general.lastutterance,
                     #'last results': context_general.lastresults,
                     'failures': context_general.failures
                     }))
        request_update("all")

    def fail():
        context_general.failures +=1

    client.emitter.on("vision_result", vision)
    client.emitter.on('recognizer_loop:utterance', utterance)
    client.emitter.on("freewill_result",freewill)
    client.emitter.on("speak",speak)
    client.emitter.on("results",results)
    client.emitter.on("context_request",requested)
    client.emitter.on("intent_failure", fail)

    event_thread = Thread(target=connect)
    event_thread.setDaemon(True)
    event_thread.start()

    #####  #request context update from other services
    def request_update(target):
        #target = freewill / vision / all
        client.emit(Message("context_update", {'target': target}))
        pass

    while True:
        request_update("all")
        time.sleep(5)

main()