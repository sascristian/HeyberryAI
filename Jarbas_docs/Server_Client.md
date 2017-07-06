Some steps were done to connect mycroft instances together, every instance can receive connections and send answers, or connect and ask answers

![ssl](https://raw.githubusercontent.com/JarbasAI/client_server_idea/master/ssl.jpeg)

# usage cases

computational server:
    - host deep dream, facebook, everything
    - clients connect for heavy processing/private skills

house server:
    - connect all your mycrofts, "kitchen", "living room", "magic mirror", use them as a single one or to relay orders

![house](https://raw.githubusercontent.com/JarbasAI/client_server_idea/master/Untitled%20Diagram.jpg)

chat room server:
    - jarbas: "tell mycroft hello"
    - server -> mycroft_to_socket_num
             -> ask_mycroft_if_jarbas_ok
    - mycroft -> is_friend(jarbas, secret_hashed)
              -> yes
    - server -> save_yes
            -> send_message (mycroft, speak: jarbas says hello)

    - mycroft -> is_friend(jarbas, secret_hashed)
            -> no
    - server -> save_no
            -> send_message (mycroft, connection.attempt.warning )
            -> send_message (jarbas, connection.refused.warning )



Or you can go wild, create the mycroft mesh collective:

 - many mycrofts all running both as server and client,
 - each "asking their parent" the answers for the questions they do not know,
 - make a protocol to transfer and validate skills between mycrofts,
 - watch it evolve by itself as masters update code


# jarbas client

- the client process connects to the messagebus
- opens a ssl connection to jarbas's server
- receives id from server
- send's names list to server
- on utterance starts monitoring responses
- if some intent triggers -> do nothing
- if intent_failure -> ask server
- if 20 seconds and no intent nor failure trigger -> ask server
- listen for requests to message server, including files
- trust all messages from server and broadcast them to client messagebus


# jarbas server

- the server process connects to the messagebus
- listens for client ssl connections
- check if ip is black/whitelisted
- check if received message types are whitelisted (unknown/blacklisted messages are discarded)
- do message pre-processing (receive files, add context)
- answer client requests
- answer internal skills message_to_client requests

# TODO

- listen for intent.execution.start/end/failure to ask server (20 secs is a placeholder)

# client LOGS

            2017-07-05 15:19:08,354 - jarbas - DEBUG - Connected to remote host. Start sending messages
            2017-07-05 15:19:08,574 - jarbas - DEBUG - Received data: {"data": {"id": 42904}, "type": "id", "context": null}
            2017-07-05 15:59:05,408 - jarbas - ERROR - Disconnected from server
            2017-07-05 15:59:05,693 - jarbas - ERROR - Unable to connect, error [Errno 111] Connection refused, retrying in 5 seconds
            2017-07-05 15:59:05,693 - jarbas - ERROR - Possible causes: Server Down, Bad key, Bad Adress
            2017-07-05 15:59:12,055 - jarbas - DEBUG - Connected to remote host. Start sending messages
            2017-07-05 15:59:12,156 - jarbas - DEBUG - Received data: {"data": {"id": 43166}, "type": "id", "context": null}
            2017-07-05 16:01:41,662 - jarbas - DEBUG - Processing utterance: describe what you see from source: cli
            2017-07-05 16:01:41,674 - jarbas - DEBUG - Waiting for intent handling before asking server
            2017-07-05 16:01:41,739 - jarbas - DEBUG - intent handled internally
            2017-07-05 16:01:41,775 - jarbas - DEBUG - Not asking server
            2017-07-05 16:01:42,542 - jarbas - INFO - Received request to message server from vision_service with type: image_classification_request with data: {u'source': u'vision_service', u'user': u'unknown', u'file': u'/home/user/jarbas_stable/JarbasAI/jarbas_skills/service_vision/feed.jpg'}
            2017-07-05 16:01:42,542 - jarbas - INFO - File requested, sending first
            sending chunk 1
            sending chunk 2
            sending chunk 3
            sending chunk 4
            sending chunk 5
            sending chunk 6
            sending chunk 7
            sending chunk 8
            sending chunk 9
            sending chunk 10
            sending chunk 11
            sending chunk 12
            sending chunk 13
            sending chunk 14
            sending chunk 15
            sending chunk 16
            sending chunk 17
            sending chunk 18
            2017-07-05 16:01:43,882 - jarbas - INFO - sending message with type: image_classification_request
            2017-07-05 16:02:00,040 - jarbas - DEBUG - Received data: {"data": {"classification": ["n01910747 jellyfish", "n04606251 wreck", "n01484850 great white shark, white shark, man-eater, man-eating shark, Carcharodon carcharias", "n01494475 hammerhead, hammerhead shark", "n01496331 electric ray, crampfish, numbfish, torpedo"]}, "type": "image_classification_result", "context": {"mute": false, "destinatary": "jarbas:43166", "source": "ImageRecognitionSkill:server", "more_speech": false}}
            2017-07-05 16:03:08,766 - jarbas - DEBUG - Processing utterance: who am i from source: cli
            2017-07-05 16:03:08,766 - jarbas - DEBUG - Waiting for intent handling before asking server
            2017-07-05 16:03:08,893 - jarbas - DEBUG - Intent failure detected, ending wait
            2017-07-05 16:03:08,967 - jarbas - DEBUG - Asking server for answer
            2017-07-05 16:03:09,151 - jarbas - DEBUG - Received data: {"data": {}, "type": "vision_request", "context": {"source": "skills:server"}}
            2017-07-05 16:03:10,111 - jarbas - INFO - Received request to message server from vision_service with type: vision_result with data: {u'distance': 0, u'smile_detected': False, u'num_persons': 0, u'master': False, u'file': u'/home/user/jarbas_stable/JarbasAI/jarbas_skills/service_vision/webcam/Wed_Jul__5_16:03:09_2017.jpg', u'movement': False}
            2017-07-05 16:03:10,111 - jarbas - INFO - File requested, sending first
            sending chunk 1
            sending chunk 2
            sending chunk 3
            sending chunk 4
            sending chunk 5
            sending chunk 6
            sending chunk 7
            sending chunk 8
            sending chunk 9
            sending chunk 10
            sending chunk 11
            sending chunk 12
            sending chunk 13
            sending chunk 14
            sending chunk 15
            sending chunk 16
            sending chunk 17
            sending chunk 18
            2017-07-05 16:03:12,282 - jarbas - INFO - sending message with type: vision_result
            2017-07-05 16:03:13,469 - jarbas - DEBUG - Received data: {"data": {"expect_response": false, "utterance": "You are 43166, according to source of message\n", "metadata": {}}, "type": "speak", "context": {"target": null, "mute": true, "destinatary": "jarbas:43166", "source": "server_skills", "user": "43166", "more_speech": false}}
            2017-07-05 16:04:10,675 - jarbas - DEBUG - Processing utterance: what am i from source: cli
            2017-07-05 16:04:10,676 - jarbas - DEBUG - Waiting for intent handling before asking server
            2017-07-05 16:04:10,789 - jarbas - DEBUG - Intent failure detected, ending wait
            2017-07-05 16:04:10,878 - jarbas - DEBUG - Asking server for answer
            2017-07-05 16:04:11,174 - jarbas - DEBUG - Received data: {"data": {"expect_response": false, "utterance": "You are jarbas user", "metadata": {}}, "type": "speak", "context": {"target": null, "mute": true, "destinatary": "jarbas:43166", "source": "server_skills", "user": "43166", "more_speech": false}}
            2017-07-05 16:04:56,585 - jarbas - DEBUG - Processing utterance: joke from source: cli
            2017-07-05 16:04:56,586 - jarbas - DEBUG - Waiting for intent handling before asking server
            2017-07-05 16:04:56,689 - jarbas - DEBUG - Intent failure detected, ending wait
            2017-07-05 16:04:56,787 - jarbas - DEBUG - Asking server for answer
            2017-07-05 16:04:57,151 - jarbas - DEBUG - Received data: {"data": {"expect_response": false, "utterance": "'It works on my machine' always holds true for Chuck Norris.", "metadata": {}}, "type": "speak", "context": {"target": null, "mute": true, "destinatary": "jarbas:43166", "source": "server_skills", "user": "43166", "more_speech": false}}
            2017-07-05 16:05:57,683 - jarbas - DEBUG - Processing utterance: dream from source: cli
            2017-07-05 16:05:57,684 - jarbas - DEBUG - Waiting for intent handling before asking server
            2017-07-05 16:05:58,066 - jarbas - DEBUG - Intent failure detected, ending wait
            2017-07-05 16:05:58,085 - jarbas - DEBUG - Asking server for answer
            2017-07-05 16:05:58,763 - jarbas - DEBUG - Received data: {"data": {"expect_response": false, "utterance": "please wait while the dream is processed", "metadata": {}}, "type": "speak", "context": {"target": null, "mute": true, "destinatary": "jarbas:43166", "source": "server_skills", "user": "43166", "more_speech": false}}
            2017-07-05 16:16:18,341 - jarbas - DEBUG - Received data: {"data": {"expect_response": false, "utterance": "Here is what i dreamed", "metadata": {"url": "http://i.imgur.com/BTCarU4.jpg", "elapsed_time": 616.5030989646912, "file": "../database/dreams/Wed_Jul__5_11:16:14_2017.jpg"}}, "type": "speak", "context": {"target": null, "mute": true, "destinatary": "jarbas:43166", "source": "server_skills", "user": "43166", "more_speech": false}}
            2017-07-05 16:16:18,577 - jarbas - DEBUG - Received data: {"data": {"elapsed_time": 616.5030989646912, "layer": "inception_3a/pool", "dream_url": "http://i.imgur.com/BTCarU4.jpg", "file": "../database/dreams/Wed_Jul__5_11:16:14_2017.jpg"}, "type": "deep_dream_result", "context": {"target": null, "mute": true, "destinatary": "jarbas:43166", "source": "server_skills:server", "user": "43166", "more_speech": false}}
