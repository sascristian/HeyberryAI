# context manager service

listens on message bus for signals and keeps track of context

requests context update from services

on request emits current context to bus

# relevant signals

        Listens to:
        
        speak - last spoken sentence
        recognizer_loop:utterance - last heard/received sentence
        results - context for results property from skills
        intent_failure - context for number of un-recognized intents
        freewill_result - context from freewill service
        vision_result - context from vision service
        register_vocab - context for all regex expressions in skills
        skill_loaded - context for available skills
        register_intent - context for registered intents
        
        Responds to:
        
        context_request - emits full context 
        context_key_request - emits result of requested context
        context_key_override - changes context to desired value
        
        Emits:
        
        context_key_result - Message("context_key_result", {'key': key, "result":result }))
        context_result - Message("context_result", {'dictionary': self.context_dict}))


# usage

run main.py

# install

clone repo into mycroft-core folder

Warning: updates core.py to add results property 
Warning: updates wikipedia skill to add example usage of results

# implementing in skills

Using wikipedia skill has example

for regex context registering when handling intent add the following 
        
        title = message.data.get("ArticleTitle")
        self.add_result("ArticleTitle",title)

the ArticleTitle context is now updated with the user inputed value

all emitted results are also added has context, so if we do

        self.add_result("Multiple_Options", options)

context for Multiple_Options will now be updated with the provided options
 
the following results are automagically added  when they exist
            
         "skill_name"
         "speak"
         "dialog" 

only last speak/dialog call will be logged, this can be over-ridden at any time by manualy keeping track and calling add_result with new string

only when you want the results are emitted, so you need the following call when your results are ready, usually at the end of intent handling

        self.emit_results()
        
if some other skill (disambiguation skill?) you need to get a previous context you just need to implement the following messagebus signal
        
        self.emitter.on("context_key_result", process)
        self.emitter.emit(Message("context_key_request", {'key': "ArticleTitle"}))
        
        def process():
            title = message.data.get["result]
            #do stuff


#author

jarbas

#aknowledgments

Thx mycroft team