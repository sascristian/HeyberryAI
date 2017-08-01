# speech targetting

using message context to pass the following variables:
- source <- where does message come from
- destinatary <- where is message going to
- user <- who is using?
- mute <- speak out loud?

skills add:
- more_speech <- more speech expected after this? default False

Utterance:
- add "source" of message

Server:
- add "user" of message (source socket by default)

Facebook skill:
- add "user" of message, facebook name

intent service:
 - will check if destinatary is "skills", if it isn't no intent will be triggered (skills by default if none provided)
 - will make the source of message the destinatary

skills:
 - add "mute", default is False
 - add "more_speech", default is False
 - add "source", default is skill_name
 - keep local context copy, values can be added from inside skill / remain from previous calls

Clients:
 - check if destinatary is self or "all" before processing speech

# logs

        2017-07-03 07:43:11,933 - Skills - DEBUG - {"type": "recognizer_loop:utterance", "data": {"utterances": ["joke"]}, "context": {"source": "Simple_CLI_Client:36678", "user": "36678", "mute": true}}
        2017-07-03 07:43:11,940 - Skills - DEBUG - {"type": "15:JokingIntent", "data": {"JokingKeyword": "joke", "intent_type": "15:JokingIntent", "utterance": "joke", "confidence": 1.0}, "context": {"source": "skills", "user": "36678", "mute": true, "destinatary": "Simple_CLI_Client:36678"}}
        2017-07-03 07:43:11,948 - Skills - DEBUG - {"type": "speak", "data": {"expect_response": false, "utterance": "Triumphantly, Beth removed Python 2.7 from her server in 2020. 'Finally!' she said with glee, only to see the announcement for Python 4.4.", "metadata": {}}, "context": {"mute": true, "destinatary": "Simple_CLI_Client:36678", "source": "JokingSkill", "user": "36678", "more_speech": false}}



speak and speak dialog methods now have metadata field:


- metadata - {"url": "source_of_info.com"}



# usage

in my server client achitecture this is needed to ensure things go to correct place, also usefull in a facebook chat client

on message handlers message.context can be used

on skills self.context can be used to get most_recent context