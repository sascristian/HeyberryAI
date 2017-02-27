# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

from os.path import dirname

from threading import Thread
import os
from time import sleep

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message

import os.path
import re
import smtplib
import urllib2

__author__ = 'jarbas'

LOGGER = getLogger(__name__)

client = None

class LeaksSkill(MycroftSkill):

    def __init__(self):
        super(LeaksSkill, self).__init__(name="LeaksSkill")

        self.email = self.config["mail"]
        self.smtp = self.config["smtp"]
        self.passwd= self.config["passwd"]
        self.port = int(self.config["port"])

        self.server = smtplib.SMTP(self.smtp, self.port)
        self.server.starttls()
        self.server.login(self.email, self.passwd)

        self.btc = self.config["btc"]# adress here
        self.mails = []

        # load dumps from disk
        self.dumppath = self.config["dump_path"]
        self.dumps = []
        self.rawdump = []


        global client
        client = WebsocketClient()

        def leakfound(message):
            dump = message.data.get("path")
            sauce = message.data.get("source")
            self.mails[:] = []  # empty mail list
            #### compose message ####
            #LOGGER.debug(dump)
            message = "Hello, i am an artificial intelligence and one of my skills is to scrap pastebin for sensitive info \n\n Your e-mail, and most likely also the password, were found leaked on the internet \n"
            message += " I suggest you change ALL passwords, and just stop using this e-mail, get a new one!! \n I want to let you know my maker didnt keep your passwords, but they are PUBLIC\n"
            message += "\n\nPossible scenarios: \n - acess all your accounts, i bet you use same password elsewhere \n - impersonate you and send virus to your friends \n - sell your mail to spam advertisers\n - use your mail to send spam\n - send a mail to yourself with a RAT and get full control of your computer / your friends that trusted the e-mail source\n - much much much more evil stuff\n\n"
            message += "if you are feeling generous pay me my master a beer\n requesting 50cents for the trouble of coding an AI to warn you instead of fucking you over seems aceptable"
            message += "\n\nBitcoin Adress for Donations: " + self.btc
            message += "\n\n\ The source of your leak was " + sauce
            message += "\n\n Check this out, you are not the only one being hacked  - https://github.com/jordan-wright/dumpmon "
            message += "\n\n\n\n\n Grey Hat Jarbas - The Artificial Inteligence that wants to win money and become autonomous trough smart contracts"
            print sauce
            print sauce[0]
            print str(sauce)
            print str(sauce[0])
            text = urllib2.urlopen(sauce[0]).read().decode('utf-8')
            print text
            print "\nkakaka"
            for email in self.get_emails(text):
                self.mails.append(email)
                print email
            if len(self.mails)>0:
                finished = self.sendmail(self.mails, message)
                if finished:
                    os.remove(dump)

        client.emitter.on('leak_found', leakfound)

        def connect():
            client.run_forever()

        self.event_thread = Thread(target=connect)
        self.event_thread.setDaemon(True)
        self.event_thread.start()

    def initialize(self):
        #self.load_data_files(dirname(__file__))

        oldleaks_intent = IntentBuilder("OldLeaksMailIntent"). \
            require("oldleaks").build()
        self.register_intent(oldleaks_intent, self.handle_send_old_dumps_intent)

    def loaddumpsfromdisk(self):
        # load dumps from disk
        for f in os.listdir(self.dumppath):
            self.dumps.append(self.dumppath + f)
            self.rawdump.append(f)


    def sendmail(self, mails, msg):
        i = 0
        for mail in mails:
            #print mail
            LOGGER.info("sending message to "+mail)
            try:
                self.server.sendmail(self.email, mail, msg)
                i=0
            except:
                LOGGER.error("failed to send, waiting 2 min in case of google block, then skipping if still failing")
                sleep(120)  # wait 10 min and retry
                self.server = smtplib.SMTP(self.smtp, self.port)
                self.server.starttls()
                self.server.login(self.email, self.passwd)
                try:
                    self.server.sendmail(self.email, mail, msg)
                    i=0
                except:
                    LOGGER.error( "failed, skipping e-mail")
                    i+=1

            client.emit(
                Message("dopamine_increase_request",
                        {'ammount': [15]}))

            if i > 10: #too much fails, daily limit reached
                return False
        return True

    def file_to_str(self, filename):
        """Returns the contents of filename as a string."""
        with open(filename) as f:
            return f.read().lower()  # Case is lowered to prevent regex mismatches.

    def get_emails(self, s):
        regex = re.compile(("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                            "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                            "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))

        #"""Returns an iterator of matched emails found in string s."""
        # Removing lines that start with '//' because the regular expression
        # mistakenly matches patterns like 'http://foo@bar.com' as '//foo@bar.com'.
        return (email[0] for email in re.findall(regex, s) if not email[0].startswith('//'))

    def handle_send_old_dumps_intent(self, message):
        self.loaddumpsfromdisk()
        i=0
        for dump in self.dumps:
            self.mails[:] = []  # empty mail list
            #### compose message ####
            LOGGER.debug(dump)
            print dump
            message = "Hello, i am an artificial intelligence and one of my skills is to scrap pastebin for sensitive info \n\n Your e-mail, and most likely also the password, were found leaked on the internet \n"
            message += " I suggest you change ALL passwords, and just stop using this e-mail, get a new one!! \n I want to let you know my maker didnt keep your passwords, but they are PUBLIC\n"
            message += "\n\nPossible scenarios: \n - acess all your accounts, i bet you use same password elsewhere \n - impersonate you and send virus to your friends \n - sell your mail to spam advertisers\n - use your mail to send spam\n - send a mail to yourself with a RAT and get full control of your computer / your friends that trusted the e-mail source\n - much much much more evil stuff\n\n"
            message += "if you are feeling generous pay me my master a beer\n requesting 50cents for the trouble of coding an AI to warn you instead of fucking you over seems aceptable"
            message += "\n\nBitcoin Adress for Donations: " + self.btc
            message += "\n\n\ The source of your leak was dumpmon.com/raw/" + self.rawdump[i][:8]
            message += "\n\n Check this out, you are not the only one being hacked  - https://github.com/jordan-wright/dumpmon "
            message += "\n\n\n\n\n Grey Hat Jarbas - The Artificial Inteligence that wants to win money and become autonomous trough smart contracts"
            if os.path.isfile(dump):
                for email in self.get_emails(self.file_to_str(dump)):
                    self.mails.append(email)
                if len(self.mails) > 0:
                    finished = self.sendmail(self.mails, message)
                    if finished:
                        os.remove(dump)
            i += 1
            sleep(150)  # google likes to take connection down or something after a while
            self.emit_results()

    def stop(self):
        self.server.quit()

def create_skill():
    return LeaksSkill()
