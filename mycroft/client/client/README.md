# server client for mycroft

work in progress

![alt tag](https://github.com/JarbasAI/client_server_idea/blob/master/ssl.jpeg)

![alt tag](https://github.com/JarbasAI/client_server_idea/blob/master/Untitled%20Diagram.jpg)

any hosted mycroft can run mycroft_server.py

any client mycoft can run mycroft_client.py and have a cli that asks remote mycroft instead of local

change port and host in files

# requires

[PR#796](https://github.com/MycroftAI/mycroft-core/pull/796)

# server logs

            2017-05-30 21:50:46,770 - Mycroft_Server - DEBUG - Listening started on port 5000
            2017-05-30 21:50:46,779 - mycroft.messagebus.client.ws - INFO - Connected
            2017-05-30 21:50:50,604 - Mycroft_Server - DEBUG - Client (127.0.0.1, 50338) connected
            2017-05-30 21:50:50,604 - Mycroft_Server - DEBUG - Sending Id to Client (127.0.0.1, 50338)
            2017-05-30 21:50:50,612 - Mycroft_Server - DEBUG - received: {"data": {"names": ["test"], "id": "50338"}, "type": "names_response", "context": null} from socket: 50338 from ip: '127.0.0.1'
            2017-05-30 21:50:50,612 - Mycroft_Server - DEBUG - Setting alias: test for socket: 50338
            2017-05-30 21:52:40,092 - Mycroft_Server - DEBUG - received: {"data": {"utterances": ["joke\n"]}, "type": "recognizer_loop:utterance", "context": null} from socket: 50338 from ip: '127.0.0.1'
            2017-05-30 21:52:40,093 - Mycroft_Server - DEBUG - emitting utterance to bus: joke

            2017-05-30 21:52:40,094 - Mycroft_Server - DEBUG - Waiting answer for user 50338
            2017-05-30 21:52:40,094 - Mycroft_Server - DEBUG - Waiting for speech response
            2017-05-30 21:52:40,111 - Mycroft_Server - DEBUG - Speak: The Chuck Norris Eclipse plugin made alien contact. Target: 50338
            2017-05-30 21:52:40,111 - Mycroft_Server - DEBUG - Capturing speech response
            2017-05-30 21:52:40,195 - Mycroft_Server - DEBUG - answering: {"data": {"target": "50338", "mute": false, "expect_response": false, "more": false, "utterance": "The Chuck Norris Eclipse plugin made alien contact.", "metadata": {}}, "type": "speak", "context": null} to user: 50338

# client logs

            2017-05-30 21:50:50,605 - mycroft.messagebus.client.ws - INFO - Connected
            2017-05-30 21:50:50,606 - CLIClient - DEBUG - Connected to remote host. Start sending messages
            2017-05-30 21:50:50,607 - CLIClient - DEBUG - Received data: {"data": {"id": ["127.0.0.1", 50338]}, "type": "id", "context": null}
            2017-05-30 21:51:35,515 - CLIClient - DEBUG - Processing utterance: joke from source: cli
            2017-05-30 21:51:48,309 - CLIClient - DEBUG - Waiting for intent handling before asking server
            2017-05-30 21:51:48,362 - CLIClient - DEBUG - Intent failure detected, ending wait
            2017-05-30 21:51:48,409 - CLIClient - DEBUG - Asking server for answer
            2017-05-30 21:52:40,195 - CLIClient - DEBUG - Received data: {"data": {"target": "50338", "mute": false, "expect_response": false, "more": false, "utterance": "The Chuck Norris Eclipse plugin made alien contact.", "metadata": {}}, "type": "speak", "context": null}
            2017-05-30 21:52:40,199 - CLIClient - INFO - Speak: The Chuck Norris Eclipse plugin made alien contact.

            2017-05-30 23:50:31,917 - mycroft.messagebus.client.ws - INFO - Connected
            2017-05-30 23:50:31,919 - CLIClient - DEBUG - Connected to remote host. Start sending messages
            2017-05-30 23:50:31,919 - CLIClient - DEBUG - Received data: {"data": {"id": ["127.0.0.1", 51918]}, "type": "id", "context": null}
            2017-05-30 23:50:35,515 - CLIClient - DEBUG - Processing utterance: joke from source: cli
            2017-05-30 23:50:35,515 - CLIClient - DEBUG - Waiting for intent handling before asking server
            2017-05-30 23:50:35,531 - CLIClient - DEBUG - intent handled internally
            2017-05-30 23:50:35,615 - CLIClient - DEBUG - Not asking server


# Working

- check if client ip is blacklisted
- create socket per client, sends internal id to client
- server forwards client utterances to mycroft messagebus
- server captures speech response and sends to client
- client listens for server messages and emits them to personal mycroft messagebus
- set alias/names for each client in server on connect
- try to answer locally before requesting server (only on intent_failure use server)
- interface with normal clients (capture all inputs)

# TODO

server side:

- ssl
- user session
- action authorization (require password for some intents)

client side:


