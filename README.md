
speech metadata carries the following by default

    {u'source_skill': 73, u'mute': False, u'target': 73, u'more': False}

- speech and cli clients check for a "mute" in speech to not speak
- speech and cli clients check if they are the target of the utterance ("all" by default)
- intent class chooses target as source of utterance
- or uses specified target

example of modified joke skill, on start calls joke intent with itself as target, since it is the target of that intent it aknowledges it instead of speaking the joke, but neither speech nor cli speak it

the "more" field is fo consumers to know if more speech is coming before doing anything with the speak message

arbitrary metadata, like source of info, can be appended to speech


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
            self.speak("Yeah, it works")
