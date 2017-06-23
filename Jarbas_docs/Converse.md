# converse method

give last executed intents a chance to handle utterances

# parrot skill example

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