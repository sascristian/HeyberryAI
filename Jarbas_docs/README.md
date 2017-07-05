# Changes in this fork

            - in skills/core.py SKILLS_DIR is now jarbas_skills folder instead of opt
            - msm/skill manager removed from skills/main.py
            - skills now have a "make_active" method that puts them on active skill list inside intent_service
            - added intent_layer class to intent_service.py
            - blacklisted pairing and configuration skill for privacy
            - do not remove articles in normalize (too much normalization IMO)
            - do not use virtual env, opencv doesnt like it, i use a machine just for jarbas so no need, this means you must run dev_setup.sh with sudo

- [PR#783](https://github.com/MycroftAI/mycroft-core/pull/783)

            - skills have internal id, internal id used instead of name in intent messages
            - blacklisted skills now read from config
            - added priority skills to be loaded first, also read from config
            - intent service now listens for external messages
            - intent parser helper class, get intent from utterance, source skill from intent
            - skills main now listens for external messages for skill_manifest, skill_shutdown and skill_reload
            - enable and disable intent can be requested from outside

- [PR#790](https://github.com/MycroftAI/mycroft-core/pull/790)

            - adds "source" field to all utterances
            - adds "metadata" field to speak method
            - adds "more" field to speak method (know more speech is coming)
            - adds "target" field to speak method
            - adds "mute" field to speak method (do not tts flag)
            - on register intent add a handler to auto-set target and mute
            - on intent_service make the target the source of speech, check if utterance source requested mute
            - speech and cli clients check if they are the target if utterance and mute flag

- [PR#556](https://github.com/MycroftAI/mycroft-core/pull/556)

            - adds disable_speak_flag to speech and cli
            - this flag is a global mute switch, if set no tts is ever made
            - skill to mute/unmute not yet merged

- Server/Client

            Readme will be updated

            - in server mycroft/client/server run self_signed.py, copy certs/myapp.crt into mycroft/client/client/certs/myapp.crt
            - change ip in mycroft/client/client/main.py
            - run main.py from server and from client in different machines, they should communicate