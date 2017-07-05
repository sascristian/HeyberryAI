# converse method

give last executed intents a chance to handle utterances instead of triggering an intent


In the base MycroftSkill class, added a method like this:

        def Converse(self, transcript, lang):
            return False

In Intent Service a few things were added to handle_utterance():

        a) Track recently invoked skills. This would be a list of the Skills associated with the best_intent that comes out of Adapt.
        Whenever a Skill's intent is invoked, it gets moved/placed at the top of the list.
        This list also gets curated to remove Skills that haven't been invoked in longer than, say 5 minutes.

        b) Before going through the current code that figures out best_intent, loop through the Skills in this list and request skills main.py to call Converse method
        If one returns True, then they have handled the utterance and there is no need to do further intent processing or fallback.

In Skills main.py:

        a) added handlers to call converse method requests

        b) loop trough loaded skills list and call converse method for requested skill_id

        c) send converse method response for intent_service


# parrot skill example usage

        def converse(self, transcript, lang="en-us"):
            if self.parroting:
                if "stop" in transcript[0].lower():
                    self.parroting = False
                    self.speak("Parrot Mode Stopped")
                else:
                    # repeat back to user
                    self.speak(transcript[0], expect_response=True)
                # tell intent service you handled the utterance so it doesnt trigger an intent
                return True
            # tell intent class you did not handle the utterance and intent should be processes
            return False

# passive usage

added to skills_core a make_active method, call this on a timer to ensure converse method is called for this skill

        def timer():
            while True:
                self.make_active()
                time.sleep(60)

useful if you want to process all user utterances and possibly avoid intent triggering

        def converse(self, transcript, lang="en-us"):
            if self.authorized:
                return False
            else:
                self.speak("not authorized")
                return True

for example you may want to check what intent will trigger with intent parser and not allow it/require authorization for some users

