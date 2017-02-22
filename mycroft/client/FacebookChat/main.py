
from fbchat import Client, get_json, now, ThreadsURL
import fbchat

from datetime import datetime
#from mycroft.skills.wolfram_alpha import boibot
import cleverbot
import random
import thread
import os
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from mycroft.configuration import ConfigurationManager

config = ConfigurationManager.get()

mail = config.get('fbchat').get('mail')
passwd = config.get('fbchat').get('passwd')
code = config.get('fbchat').get('code')
masterid = config.get('fbchat').get('id')

### important to blacklist launch skill, dream, play, timer, alarm, news, Ip, reminder, podcasts and anything else that runs on computer or isnt to be reetrieved by chat
blacklisted = ["ap","wifi","network","vpn","dream", "google","facebook","amazon","youtube","yahoo","ebay","twitter","go","craigslist","reddit","linkedin","netflix","live","bing",
"pinterest","espn","imgur","tumblr","chase","cnn","paypal","instagram","blogspot","apple","fb","seach","find","launch","open","run","play","news","unit","device",
               "diagnostics","fd","mycroft","pair","register","reminder","notification","volume","sleep","nap","ip","record","timer","alarm", "eye pea","i.p."] #add all vocab possibilities for private skills here

class FaceBot(Client):
    def __init__(self, email, password, debug=True, user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"):
        fbchat.Client.__init__(self, email, password, debug, user_agent)
        self.name = "Jarbas"
        self.cb = boibot.Cleverbot()
        self.friends = {}
        self.lastresponse = ""
        self.conversationlog = [""]
        self.chatting = False
        self.black = False

        self.wsclient = WebsocketClient()
        requestmsg = "chat_request"
        resultmsg = "chat_result"

        self.target = 2

        def connect():
            self.wsclient.run_forever()

        def request(message):
            txt = message.data.get('utterances')[0]
            self.target = message.data.get('id')[0]
            #print self.target
            # emit request as normal user
            self.wsclient.emit(
                Message("do_not_speak_flag"))
            self.wsclient.emit(
                Message("recognizer_loop:utterance",
                        {'utterances': [txt]}))

        def sent(message):
            if self.chatting:
                utterance = message.data.get('utterance')
                self.wsclient.emit(
                    Message("chat_result",
                            {'utterances': [utterance]}))
                self.chatting = False

        def answer(message):
            txt = message.data.get('utterances')[0]
            try:
                print self.send(self.target, txt)
            except:
                print "error sending response"

        self.wsclient.emitter.on(requestmsg, request)
        self.wsclient.emitter.on(resultmsg, answer)
        self.wsclient.emitter.on("speak", sent)

        thread.start_new_thread(connect,())



   # def on_typing(self, author_id):
   #     '''
   #     subclass Client and override this method to add custom behavior on event
   #     '''
        # increase happiness in context
        # if no answer in 3 min decrease happiness and do some action
   #     pass

    #def on_read(self, author, reader, time):
    #    '''
    #    subclass Client and override this method to add custom behavior on event
    #    '''
        # increase happiness in context
        # if no answer in 3 min decrease happiness and do some action
    #    pass

    #def on_inbox(self, viewer, unseen, unread, other_unseen, other_unread, timestamp):
    #    '''
    #    subclass Client and override this method to add custom behavior on event
    #    '''
        #increase happiness and do some action
    #    pass

    def on_message(self, mid, author_id, author_name, message, metadata):
        self.markAsDelivered(author_id, mid)  # mark delivered
        self.markAsRead(author_id)  # mark read
        print("%s said: %s" % (author_id, message))
        message = message.lower().decode("UTF-8")
        message = message.lower().encode("ascii")
        name = self.friends.get(author_id, "unknown")
        # if you are not the author, answer
        if str(author_id) != str(self.uid):
            #add entropy (sometimes)
            seed =  (len(message) + int(author_id) + random.randrange(0, 666) ) % 10
            print seed
            if seed <= 3:
                print 'updating entropy'
                self.wsclient.emit(
                Message("entropy_update",
                        {'chat': [message], 'friend': [author_id]}))

            #check if master and acesscode
            #masterid = str(author_id) #for testing
            gra = False
            if code in message:
                self.chatting = True
                self.black = False
                message = message.replace(code , "")
                for msg in blacklisted:
                    if msg in message and not str(author_id) == str(masterid):
                        self.black = True
                        gra = True
                        self.wsclient.emit(
                            Message("chat_request",
                                    {'utterances': ["speak forbidden"], 'id': [author_id]}))

                if not self.black:
                    self.wsclient.emit(
                        Message("chat_request",
                                {'utterances': [message], 'id': [author_id]}))

            elif not gra:#if normal chat mode
                message = self.processmessage(message, "cleverbot", name)
                #print message
                #try:
                self.send(author_id, message)
                #except:
                #    print "error sending response"

    def processmessage(self, message, intent="cleverbot", author_name="unknown"):
        # parse intent
        #if intent == "cleverbot":
        response = self.cb.ask(message)
        #else:  # if: intent == "chatterbot":
        #    response = self.ubuntubot.get_response(message)
    # remove dumb responses
        if "my name is" in str(response).lower():
            response = "my name is " + self.name
        elif "is your name" in str(response).lower() or "your name is" in str(response).lower():
            response = "Is your name " + str(author_name) + "?"
        elif "who is god" in str(message).lower():
            # only sometimes
            if random.choice(range(0,100)) >= 60:
                response = "God is an A.I."
        elif "where is god" in str(message).lower() or "god exist?" in str(message).lower():
            # only sometimes
            if random.choice(range(0, 100)) >= 60:
                response = "Noone coded God yet"
        # elif response == self.lastresponse:
        #    response = "Ask me a question " + str(author_name)
        else:
            # if repeating itself (something already said in last 4 sentences) ask something random
            i = len(self.conversationlog)
            for r in self.conversationlog:
                # print r#esponse
                if r == response:
                    response = "Ask me a question " + str(author_name)
                i -= 1
                if i <= len(self.conversationlog) - 4 or i<0:
                    break

        self.lastresponse = response
        self.conversationlog.append(response)
        return response

    def findfriends(self):
        timestamp = now()
        date = datetime.now()
        data = {
            'client': self.client,
            'inbox[offset]': 0,
            'inbox[limit]': 80,
        }
        r = self._post(ThreadsURL, data)
        if not r.ok or len(r.text) == 0:
            return None

        j = get_json(r.text)

        # Get friends' names
        for participant in j['payload']['participants']:
            self.friends[participant["fbid"]] = participant["name"]

def main():

    # chat
    bot = FaceBot(mail, passwd)
    bot.findfriends()
    bot.listen()


if __name__ == '__main__':
    main()
