# intent parser


it is now possible to get intents from utterances, or skills ids from intents, by using intent parser helper class



# example usage inside converse method

        from mycroft.skills.intent_service import IntentParser

        def initialize(self):
            self.intent_parser = IntentParser(self.emitter)

        def converse(self, transcript, lang="en-us"):
             # check if some of the intents will be handled
            intent, id = self.intent_parser.determine_intent(transcript[0])

            if id == 0:
                # no intent will be triggered
                pass
            elif id == self.skill_id:
                # a intent inside this skill will trigger
                pass
            elif id != self.skill_id:
                # a intent from skill with id will trigger
                # we could also get skill_id for intent by doing
                skill_id = self.intent_parser.get_skill_id(intent)
                self.intercept_flag = True

            if self.intercept_flag:
                # dont let intent class handle this utterance if you dont want to
                return True

            return False