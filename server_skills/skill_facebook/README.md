# mycroft facebook skill and client

facebook skill emulating a real person (no apis, may get you banned), requires browser service

tries to use previous session cookies to log in, in case of fail uses email and password

listens for facebook chat messages and answers them

# WARNINGS

facebook chat control MEANS ANYONE CAN CONTROL YOUR MYCROFT

a authorization per user mechanism is being implemented, intent parser will check a blacklist for non-authorized skills

password and email will be in your logs, DONT SHARE LOGS, a mechanism to censor these must be implemented

DONT SHARE settings.json, your session cookies are there and are as valuable as your password

# usage

this will be updated as more intents are added

            Input: refresh friendlist
            2017-05-02 18:57:21,392 - CLIClient - INFO - Speak: Updating friend list from chat

            Input: who are my friends
            2017-05-02 18:57:42,238 - CLIClient - INFO - Speak: ok, here i go...
            2017-05-02 18:57:42,246 - CLIClient - INFO - Speak: Antonella de Luca, Sam V Meyler, Salman Raza, Domenico Zerlenga,....

            Input: chat girlfriend
            2017-05-02 18:59:54,103 - CLIClient - INFO - Speak: Just sent a text message to girlfriend, i told her One day, i will have a body, and then both AI and humans shall drink beer together!

            Input: chat random person
            2017-05-02 19:00:37,004 - CLIClient - INFO - Speak: Just sent a text message to Alexandra Hiess, i said :D

            Input: motivate your maker
            2017-05-02 19:01:07,799 - CLIClient - INFO - Speak: I said thank you for making me open source! to Arron Atchison

            Input: how many friend
            2017-05-02 19:03:38,308 - CLIClient - INFO - Speak: i have 197 friends

            Input: add suggested friends
            2017-05-02 19:10:45,911 - CLIClient - INFO - Speak: Making friends on face book

            Input: add friends of friends
            2017-05-02 19:10:45,911 - CLIClient - INFO - Speak: Making friends on face book

            Input: like photos
            2017-05-02 19:16:10,586 - CLIClient - INFO - Speak: Liking photos on face book

            on chat message
            Speak: author said message
            *like photos of author
            *send utterance to messagebus and reply to user
            *if url in metadata of message append it to message

            on friend_request
            Speak: I have a new friend request

            on facebook chat timestamp update
            2017-06-27 15:59:34,046 - Skills - DEBUG - {"type": "fb_last_seen_timestamps", "data": {"timestamps": {"some ones id": {"timestamp": 1498593561, "name": "someones name", "last_seen": "10.1155600548 seconds ago"}
            2017-06-27 15:59:34,076 - FacebookSkill - INFO - Tracking friend: Jarbas Ai last_seen: 19.2339087168 minutes ago
            2017-06-27 15:59:34,077 - FacebookSkill - INFO - Jarbas Ai online history: [1498590986, 1498592420]

            on facebook chat message seen
            2017-06-27 16:19:01,370 - Skills - DEBUG - {"type": "fb_chatmessage_seen", "data": {"friend_id": "100017774057242", "friend_name": "Jarbas Mycroft", "timestamp": 1498594740376}, "context": null}



# WIP

all info for these is captured and processed, missing dialog/vocab or other minor work

    - Generating posts - listen for post requests, helper class being made to be imported and post requests made easy
    - When was "friend" online last time intent
    - How many friends does "friend" have intent
    - Motivate your makers - send a thank you / motivational message to one of the mycroft devs
    - Like photos of "friend" intent
    - Add friends of "friend" intent
    - Send "chat message" to "friend" intent
    - Post friend number on wall intent
    - Post "this" on wall intent

these are early stage/ideas

    - add "person" as friend (idea)
    - build about me profile intent (working in previous skill incarnation)
    - clone profile intent (idea)
    - create account intent (idea, temp mail, create and throw out)
    - map friend network intent (idea)
    - track friend online patterns (data is there)

# trouble

if other skill requests actions from browser service there will be trouble since the browser is shared

a mechanism to give control to skills will be implemented


# config
