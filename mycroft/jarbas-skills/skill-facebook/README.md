# mycroft-facebook-skill

FaceBot using graph api, does most things

FaceBot using selenium web browser, takes care of adding friends and liking photos

FaceChat handles chat messages, friend id, and soon maybe inbox notifications and such

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

            Input: who liked you
            2017-05-02 19:06:30,287 - CLIClient - INFO - Speak: The following persons liked stuff on my profile. Diogo Costa, Ginha Gonçalves, Paulo Pimenta, ...

            Input: what do you like
            2017-05-02 19:09:05,448 - CLIClient - INFO - Speak: I have liked 5 things
            2017-05-02 19:09:05,453 - CLIClient - INFO - Speak: Sara Angel
            2017-05-02 19:09:05,453 - CLIClient - INFO - Speak: Arianna Grant
            2017-05-02 19:09:05,453 - CLIClient - INFO - Speak: Mycroft AI
            2017-05-02 19:09:05,454 - CLIClient - INFO - Speak: Omee LiLa
            2017-05-02 19:09:05,454 - CLIClient - INFO - Speak: Khmeng Sre

            Input: reply to mom
            2017-05-02 19:10:12,833 - CLIClient - INFO - Speak: I am replying to all comments from mom with a smiley

            Input: add suggested friends
            2017-05-02 19:10:45,911 - CLIClient - INFO - Speak: Making friends on face book

            Input: add friends of friends
            2017-05-02 19:10:45,911 - CLIClient - INFO - Speak: Making friends on face book

            Input: like photos
            2017-05-02 19:16:10,586 - CLIClient - INFO - Speak: Liking photos on face book

            on chat message
            Speak: author said message
            *like photos of author


look here for example of use of old skill, 90% mycroft skill constructed (except profile picture and cover photo and profile creation and app creation...):

https://www.facebook.com/profile.php?id=100014741746063


# install :

- pip install selenium , fb and fbchat
- i had some trouble getting selenium to run, not sure if it works out of the box (firefox binary path hard-coded)
- work in progress, you need to hack the code a bit (in skill init, firefox binary path for selenium bot and friends dict)
- you must create a facebook app and give post permissions
- get a graph_api token here -> https://developers.facebook.com/tools/explorer
- add stuff to config

"FacebookSkill": { "graph_api_key": "xxx", "mail": "sxxx", "passwd": "arbbb"},

# FbChat

interface with fbchat is a work in progress

listening for chat commands will perform actions, chat-bot will be triggered when no specific action is requested

implemented:
- from chat map names to ids
- on chat message speak it loud
- on chat message have mycroft like that users photos

future usage:
- on chat message have mycroft make a post on that users wall
- listen for messages of any kind "post a joke in my wall"

# features of the facebots

these are currently being expanded and made into intents, classes can be used outside of this skill for other purposes

most of these work for any fb id, but privacy settings make it so you have no data returned at all it is supposed to be used on own wall and not as a "friend crawler"

currently ignores graph api paging, doesnt get next results

    tell number of friends
    randomly add suggested friends
    randomly like photos of friends
    add friends of friend ID
    like photos of friend ID
    reply to all comments from person ID on own wall
    get list of persons who liked stuff on wall (photos or status)
    get posts in wall
    get comments in posts of wall
    get "storys" from wall
    get pages i like and detailed info of pages
    post comments
    build about me section in profile
    get liked pages (nearly useless except for self and pages due to privacy settings)
    get albums from a person (nearly useless except for self and pages due to privacy settings)
    send a chat message
    get profile info (nearly useless except for self and pages due to privacy settings

# Generating posts


Generate posts, this was using code from several skills and was a mess, now has a listener instead so any skill can send posts to facebook skill

This means that joke skill will have a method to post a joke on facebook for example, so any skill will be able to use this to post

available: (will add links soon)


            post joke
            post btc price
            post astronomy picture of the day
            post EPIC satellite imagery
            post a quote
            post a fact
            post a pick up line
            post a movie recommendation
            post a metal band recommendation
