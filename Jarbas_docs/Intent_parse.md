# intent parser

        from mycroft.skills.intent_service import IntentParser

        def initialize(self):
            self.intent_parser = IntentParser(self.emitter)

        def converse(self, transcript, lang="en-us"):
             # check if some of the intents will be handled
            intent, id = self.intent_parser.determine_intent(transcript[0])

            if id == 0:
                # no intent will be triggered
                pass
            elif id != self.skill_id:
                # no longer inside this conversation
                skill_id = self.intent_parser.get_skill_id(intent)
                # utterance will trigger skill_id
                self.intercept_flag = True

            if self.intercept_flag:
                # dont let intent class handle this utterance if you dont want to
                return True

            return False