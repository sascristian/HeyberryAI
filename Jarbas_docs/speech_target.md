# speech targetting

utterances in speech and cli clients now have a field "source"

when parsing intent, "source" from utterance is made "target" of intent
when parsing intent, "mute" from utterance is made "mute" of intent

speak and speak dialog methods now have fields:

- mute - True or False, is the speak method supposed to call TTS or just be logged/processed?
- metadata - {"skill_name":skill_name} - skill name auto-appended, may include any extra data
- target - where is this supposed to be spoken
- more - is more speech expected after this?

when intent is triggered, target and mute is auto-set inside skill, may be manually over-rided

cli and speech client check if they are the target of speak messages, if not they dont process it


# usage

in my server client achitecture this is needed to ensure things go to correct place, also usefull in a facebook chat client