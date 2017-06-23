# Changes in this fork

- in skills/core.py SKILLS_DIR is now jarbas_skills folder instead of opt

- msm/skill manager removed from skills/main.py

- skills have internal id, internal id used instead of name in intent messages

- [PR#783](https://github.com/MycroftAI/mycroft-core/pull/783)

            - blacklisted skills now read from config
            - added priority skills to be loaded first read from config
            - intent service now listens for external messages
            - intent parser helper class, get intent from utterance, source skill from intent
            - skills main now listens for external messages for skill_manifest, skill_shutdown and skill_reload
            - enable and disable intent can be requested from outside