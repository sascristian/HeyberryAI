# Changes in this fork

            - no pairing
            - no config update from mycroft.ai
            - added "intent.start", "intent.end", "intent.failed" messages
            - in skills/core.py SKILLS_DIR is now jarbas_skills folder instead of opt
            - skills now have a "make_active" method that puts them on active skill list inside intent_service
            - added IntentLayer class to intent_service.py
            - do not remove articles in normalize (too much normalization IMO)
            - added MarkovChain util
            - added art util
            - added BackendService abstract class and a bunch of services using it

            # temporary changes
            - no msm
            - do not use virtual env, opencv doesnt like it, i use a machine just for jarbas so no need, this means you must run dev_setup.sh with sudo

- [PR#859](https://github.com/MycroftAI/mycroft-core/pull/859)

            - helper class added to intent_service
            - intent from utterance
            - skill from intent
            - skill from utterance

- [PR#]()

            - priority skills are loaded first
            - read from config

- [PR#860](https://github.com/MycroftAI/mycroft-core/pull/860)

            - enable / disable intent can be requested in messagebus

- [PR#783](https://github.com/MycroftAI/mycroft-core/pull/783)

            - skills have internal id, internal id used instead of name in intent messages
            - skills main now listens for external messages for skill_manifest, skill_shutdown and skill_reload

- [PR#790](https://github.com/MycroftAI/mycroft-core/pull/790)

            - uses message context to target messages to source of utterance
            - uses message context to mute (not trigger tts)
            - uses message context to tell if more speech is expected
            - adds "metadata" field to speak method
            - clients check if they are the target of utterance before processing it
            - adds data to message context:
                - target = cli/speech/facebook - default = "all"
                - mute = trigger tts or not - default = "false"
                - more_speech = more speak messages expected- default = "False"
                - destinatary = used to track remote_client to send message to
                - source = source of message, default = source skill / source client

- [PR#556](https://github.com/MycroftAI/mycroft-core/pull/556)

            - adds disable_speak_flag to speech and cli
            - this flag is a global mute switch, if set no tts is ever made
            - skill to mute/unmute not yet merged

- Server/Client

            - client / server (a "firewall" that connects to the mycroft messagebus )
            - client connects to server, by secure websockets
            - server sends public pgp key
            - client sends public pgp encrypted with server pgp
            - server sends AES key encrypted with client pgp, client pgp key authorizes client / creates account in server
            - all communication after is AES encrypted, if plaintext received client is kicked
            - server does all kinds of processing (receiving files, requesting stuff from clients, authorizing action per client)
            - on first run a new pgp key is automatically created (client and server)

client server basically connect jabas/mycroft instances, server can work as:

            - fallback mechanism
            - chat room
            - relay
            - ...