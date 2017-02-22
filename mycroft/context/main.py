from mycroft.context import Context, FreeWillContext,VisionContext
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message

from threading import Thread
import time
import re

#from adapt.context import ContextManager
import adapt.entity_tagger as entity_tag
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
            # generalize for all results in a dicT!!!!
        # update regex contexts

        print "\n"+context_general.lastaction
        #print "\nmessage fields received\n"
        #fields=[]
        #for field in message.data:
        #    print str(field)
        #    fields.append(field)

        #print "\nregistered words\n"
        for word in vocab:
            #print word #key
            #if word in fields:
                #im obviously missing osmething, word doesnt work in message.data.get but appears in field
            try:
                ctxt = message.data[word]
            #ctxt = message.data.get[word] #try to get that context key -> this crashes thread ALWAYS, wtf? encoding?
            #print word #key
                print "\nkey detected"
                print ctxt  # result
                context_general.contextdict[word] = ctxt
                return
            except:
                pass#key not detected


    #####  send current context

    def requested(target):
        request_update("all")
        time.sleep(0.1)
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
                     'failures': context_general.failures,
                     'regex': context_general.contextdict
                     }))

       # inject_context() #handled in intent skill ?

    def fail():
        context_general.failures +=1

    vocab = []

    def addvocab(message):
        words = message.data.get("regex")
        if words is not None:
            #print words
            #parse words for regex (<?P<KEY>.*)
            index = words.find("(?P<")
            endindex = words.find(">")
            name = words[index+4:endindex]
            if name not in vocab:
                vocab.append(name)
                context_general.contextdict.setdefault(name)
                print "registering context " + name


    client.emitter.on("vision_result", vision)
    client.emitter.on('recognizer_loop:utterance', utterance)
    client.emitter.on("freewill_result",freewill)
    client.emitter.on("speak",speak)
    client.emitter.on("results",results)
    client.emitter.on("context_request",requested)
    client.emitter.on("intent_failure", fail)
    client.emitter.on("register_vocab", addvocab)

    event_thread = Thread(target=connect)
    event_thread.setDaemon(True)
    event_thread.start()

    #####  #request context update from other services
    def request_update(target):
        #target = freewill / vision / all
        client.emit(Message("context_update", {'target': target}))
        pass


    while True:
        time.sleep(0.3)
        #client.emit(Message("context_request"))    #when should this be called?





main()