https://github.com/MycroftAI/mycroft-core/issues/790

- speech and cli clients check for a "mute" in speech to not speak
- speech and cli clients check if they are the target of the utterance before processing it
- intent class makes the target the source of utterance
- on register intent add a handler just to set target and mute flag on receiving intent message
- receive intent message (with target and mute flag), store target in self.target and call intent handler
- on speak method add self.target and self.muted to metadata if none was provided

speech metadata carries the following by default

    {u'source_skill': skill_id/name, u'mute': False, u'target': source_of_utterance, u'more': False}

the "more" field is for consumers to know if more speech is coming before doing anything with the speak message

arbitrary metadata, like source of info, can be appended to speech

# usage

example of modified joke skill, on start calls joke intent with itself as target, since it is the target of that intent it aknowledges it instead of speaking the joke, but neither speech nor cli speak it

    def initialize(self):
        intent = IntentBuilder("JokingIntent").require("JokingKeyword").build()
        self.register_intent(intent, self.handle_intent)

        self.emitter.on("speak", self.consume_speak)

        self.emitter.emit(Message(self.name+":"+"JokingIntent", {"target": self.name}))

    def consume_speak(self, message):
        utterance = message.data.get("utterance")
        metadata = message.data.get("metadata")
        target = metadata.get("target")
        if target == self.name:
            self.speak("Yeah, it works", metadata={"target": "all"})

# logs

            2017-05-24 18:35:38,730 - Skills - DEBUG - {"type": "73:JokingIntent", "data": {"confidence": 1.0, "target": "cli", "mute": false, "intent_type": "73:JokingIntent", "JokingKeyword": "joke", "utterance": "joke"}, "context": {"target": "cli"}}
            2017-05-24 18:35:38,736 - Skills - DEBUG - {"type": "speak", "data": {"expect_response": false, "utterance": "Chuck Norris can install a 64-bit operating system on 32-bit machines.", "metadata": {"source_skill": 73, "mute": false, "target": "cli", "more": false}}, "context": null}

# Facebbok chat coming soon with this
