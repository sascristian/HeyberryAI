# global mute / unmute for mycroft

if set mycroft will not call TTS

if more clients are added handlers for this are needed

# usage

    def handle_speak_disable_intent(self, event):
        self.speak_dialog("speak_disabled")
        self.emitter.emit(
            Message("do_not_speak_flag_enable"))

    def handle_speak_enable_intent(self, event):
        self.speak_dialog("speak_enabled")
        self.emitter.emit(
            Message("do_not_speak_flag_disable"))