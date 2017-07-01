#!/usr/bin/env python
# forked from: https://github.com/byt3bl33d3r/dumpmon

import datetime
import logging
import os
import random
import re
import sys
from StringIO import StringIO
from os.path import dirname
from threading import Thread
from time import sleep

import requests
from adapt.intent import IntentBuilder
from lxml import html

from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = "jarbas"

regexes = {
    'email': re.compile(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}', re.I),
    # 'ssn' : re.compile(r'\d{3}-?\d{2}-?\d{4}'),
    'hash32': re.compile(r'[^<A-F\d/]([A-F\d]{32})[^A-F\d]', re.I),
    'FFF': re.compile(r'FBI\s*Friday', re.I),  # will need to work on this to not match CSS
    'lulz': re.compile(r'(lulzsec|antisec)', re.I),
    'cisco_hash': re.compile(r'enable\s+secret', re.I),
    'cisco_pass': re.compile(r'enable\s+password', re.I),
    'google_api': re.compile(r'\W(AIza.{35})'),
    'honeypot': re.compile(r'<dionaea\.capture>', re.I),
    'pgp_private': re.compile(r'BEGIN PGP PRIVATE', re.I),
    'ssh_private': re.compile(r'BEGIN RSA PRIVATE', re.I),
    'db_keywords': [
        re.compile(
            r'((customers?|email|users?|members?|acc(?:oun)?ts?)([-_|/\s]?(address|name|id[^")a-zA-Z0-9_]|[-_:|/\\])))',
            re.I),
        re.compile(r'((\W?pass(wor)?d|hash)[\s|:])', re.I),
        re.compile(r'((\btarget|\bsite)\s*?:?\s*?(([a-z][\w-]+:/{1,3})?([-\w\s_/]+\.)*[\w=/?%]+))', re.I),
        # very basic URL check - may be improved later
        re.compile(r'(my\s?sql[^i_\.]|sql\s*server)', re.I),
        re.compile(r'((host|target)[-_\s]+ip:)', re.I),
        re.compile(r'(data[-_\s]*base|\Wdb)', re.I),  # added the non-word char before db.. we'll see if that helps
        re.compile(r'(table\s*?:)', re.I),
        re.compile(r'((available|current)\s*(databases?|dbs?)\W)', re.I),
        re.compile(r'(hacked\s*by)', re.I)
    ],
    # I was hoping to not have to make a blacklist, but it looks like I don't really have a choice
    'blacklist': [
        re.compile(r'(select\s+.*?from|join|declare\s+.*?\s+as\s+|update.*?set|insert.*?into)', re.I),  # SQL
        re.compile(r'(define\(.*?\)|require_once\(.*?\))', re.I),  # PHP
        re.compile(r'(function.*?\(.*?\))', re.I),
        re.compile(r'(Configuration(\.Factory|\s*file))', re.I),
        re.compile(r'((border|background)-color)', re.I),  # Basic CSS (Will need to be improved)
        re.compile(r'(Traceback \(most recent call last\))', re.I),
        re.compile(r'(java\.(util|lang|io))', re.I),
        re.compile(r'(sqlserver\.jdbc)', re.I)
    ],
    # The banlist is the list of regexes that are found in crash reports
    'banlist': [
        re.compile(r'faf\.fa\.proxies', re.I),
        re.compile(r'Technic Launcher is starting', re.I),
        re.compile(r'OTL logfile created on', re.I),
        re.compile(r'RO Game Client crashed!', re.I),
        re.compile(r'Selecting PSO2 Directory', re.I),
        re.compile(r'TDSS Rootkit', re.I),
        re.compile(r'SysInfoCrashReporterKey', re.I),
        re.compile(r'Current OS Full name: ', re.I),
        re.compile(r'Multi Theft Auto: ', re.I),
        re.compile(r'Initializing cgroup subsys cpuset', re.I),
        re.compile(r'Init vk network', re.I),
        re.compile(r'MediaTomb UPnP Server', re.I),
        re.compile(r'#EXTM3U\n#EXTINF:', re.I)
    ]
}


class DumpStats(object):
    def __init__(self):
        '''
        class Paste: Generic "Paste" object to contain attributes of a standard paste

        '''
        self.emails = 0
        self.hashes = 0
        self.num_emails = 0
        self.num_hashes = 0
        self.text = None
        self.type = None
        self.sites = None
        self.db_keywords = 0.0

    def match(self):
        '''
        Matches the paste against a series of regular expressions to determine if the paste is 'interesting'

        Sets the following attributes:
                self.emails
                self.hashes
                self.num_emails
                self.num_hashes
                self.db_keywords
                self.type

        '''

        # Get the amount of emails
        self.emails = list(set(regexes['email'].findall(self.text)))
        self.hashes = regexes['hash32'].findall(self.text)
        self.num_emails = len(self.emails)
        self.num_hashes = len(self.hashes)
        if self.num_emails > 0:
            self.sites = list(set([re.search('@(.*)$', email).group(1).lower() for email in self.emails]))
        for regex in regexes['db_keywords']:
            if regex.search(self.text):
                logging.debug('\t[+] ' + regex.search(self.text).group(1))
                self.db_keywords += round(1 / float(
                    len(regexes['db_keywords'])), 2)
        for regex in regexes['blacklist']:
            if regex.search(self.text):
                logging.debug('\t[-] ' + regex.search(self.text).group(1))
                self.db_keywords -= round(1.25 * (
                    1 / float(len(regexes['db_keywords']))), 2)

        self.type = 'db_dump'
        if regexes['cisco_hash'].search(self.text) or regexes['cisco_pass'].search(self.text):
            self.type = 'cisco'
        if regexes['honeypot'].search(self.text):
            self.type = 'honeypot'
        if regexes['google_api'].search(self.text):
            self.type = 'google_api'
        if regexes['pgp_private'].search(self.text):
            self.type = 'pgp_private'
        if regexes['ssh_private'].search(self.text):
            self.type = 'ssh_private'
        # if regexes['juniper'].search(self.text): self.type = 'Juniper'
        for regex in regexes['banlist']:
            if regex.search(self.text):
                self.type = None
                break
        return self.type


class DumpMon(object):
    def __init__(self, emitter=None, save=False, autostart=False):
        self.logger_start()
        self.emitter = emitter
        self.prev_links = []
        self.dumps = []
        self.monitor_thread = None
        if autostart:
            self.start_monitor_thread()
        self.save = save
        self.mail_num = 0
        self.pgp_num = 0
        self.ssh_num = 0
        self.cisco_num = 0
        self.api_num = 0
        self.db_dump_num = 0
        self.honeypot_num = 0
        self.mails = []

    def start_monitor_thread(self):
        self.monitor_thread = Thread(target=self.monitor)
        self.monitor_thread.setDaemon(True)
        self.monitor_thread.start()

    def stop(self):
        if self.monitor_thread is not None:
            # TODO need to search syntax for this
            # self.monitor_thread.terminate()
            pass

    def monitor(self):
        while True:
            Stats = DumpStats()
            try:
                r = requests.get('https://www.twitter.com/dumpmon')
                tree = html.fromstring(r.text)
                links = tree.xpath("//a[@class='twitter-timeline-link']//@title")
                for link in links:
                    if link not in self.prev_links:
                        if 'dumpmon.com' in link:
                            id = link.split('=')[0]
                        else:
                            id = None

                        if id is not None:
                            dump = requests.get(link).text.encode('utf-8', 'ignore')
                            if re.search('paste has been removed', dump, re.IGNORECASE):
                                self.logger.info('Dump id {} has been removed! skipping...'.format(id))
                                continue

                            dump_buffer = StringIO(dump)
                            dump_name = id[23:]

                            if id in os.listdir(dirname(__file__) + '/dumps'):
                                self.logger.info('Dump id {} is present in directory'.format(id))
                                with open(dirname(__file__) + '/dumps/' + id, 'r') as file:
                                    d_buffer = file.read(500)
                                    if d_buffer == dump_buffer.read(500):
                                        self.logger.info(
                                            'Contents of dump id {} appear to be the same! skipping...'.format(id))
                                        continue
                                    else:
                                        self.logger.info('Contents of dump id {} differ! dumping...'.format(id))
                                        dump_name = '{}_{}'.format(id,
                                                                   datetime.strftime('%Y-%m-%d_%H:%M:%S:%s'))

                            Stats.text = dump
                            dump_type = Stats.match()

                            log_output = 'New dump detected: %s' % link

                            if dump_type == 'db_dump':
                                log_output += ' Emails: %s Hashes: %s Keywords: %s' % (
                                    Stats.num_emails, Stats.num_hashes, Stats.db_keywords)
                                self.db_dump_num += 1
                                self.mail_num += int(Stats.num_emails)
                                self.mails += Stats.emails
                                if Stats.num_emails > 0 and Stats.num_hashes > 0:
                                    log_output += ' E/H: %s' % str(round(Stats.num_emails / float(Stats.num_hashes), 2))


                            elif dump_type == 'cisco':
                                log_output += ' Possible Cisco configuration file'
                                self.cisco_num += 1
                            elif dump_type == 'google_api':
                                log_output += ' Possible Google API key(s)'
                                self.api_num += 1
                            elif dump_type == 'honeypot':
                                log_output += ' Possible Dionaea Honeypot Log'
                                self.honeypot_num += 1
                            elif dump_type == 'pgp_private':
                                log_output += ' Possible PGP private key'
                                self.pgp_num += 1
                            elif dump_type == 'ssh_private':
                                log_output += ' Possible SSH private key'
                                self.ssh_num += 1
                            elif dump_type is None:
                                continue

                            path = dirname(__file__) + "/dumps/" + dump_name + "_" + dump_type + ".txt"

                            if self.save:
                                self.logger.info("Saving dump to " + path)
                                with open(path, 'w') as file:
                                    file.write(dump)
                                    file.close()

                            self.logger.info(log_output)
                            if self.emitter is not None:
                                self.emitter.emit(
                                    Message("leak_found",
                                            {'type': [dump_type], 'source': [link], 'path': [path]}))
                            new_dump = {
                                dump_name: {'stats': Stats, 'type': [dump_type], 'source': [link], 'path': [path]}}
                            self.dumps.append(new_dump)
                self.prev_links = links
                sleep(10)
            except Exception, e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                self.logger.warning((str(e), exc_type, fname, exc_tb.tb_lineno))

    def logger_start(self):
        requests_log = getLogger("requests")  # Disables "Starting new HTTP Connection (1)" log message
        requests_log.setLevel(logging.WARNING)

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        fileHandler = logging.FileHandler(dirname(__file__) + '/dumpmon.log')
        fileHandler.setFormatter(formatter)
        self.logger = getLogger('dumpmon')
        self.logger.addHandler(fileHandler)
        self.logger.setLevel(logging.INFO)
        self.logger.info('Starting...')

    def get_mails(self):
        return self.mails

    def get_dumps(self):
        return self.dumps

    def get_dump_num(self):
        return len(self.dumps)

    def get_honeypot_num(self):
        return self.honeypot_num

    def get_pgp_num(self):
        return self.pgp_num

    def get_ssh_num(self):
        return self.ssh_num

    def get_cisco_num(self):
        return self.cisco_num

    def get_db_num(self):
        return self.db_dump_num

    def get_api_num(self):
        return self.api_num

    def get_mail_num(self):
        return self.mail_num

    def reset(self):
        self.dumps = []
        self.prev_links = []
        self.db_dump_num = 0
        self.mail_num = 0
        self.pgp_num = 0
        self.ssh_num = 0
        self.cisco_num = 0
        self.api_num = 0
        self.honeypot_num = 0


class DumpmonSkill(MycroftSkill):
    def __init__(self):
        super(DumpmonSkill, self).__init__(name="DumpmonSkill")
        self.dumpmon = None
        self.reload_skill = False
        # start monitoring dumops on start up or on command?
        self.autostart = False

    def initialize(self):
        self.dumpmon = DumpMon(emitter=self.emitter, save=True, autostart=self.autostart)

        dump_intent = IntentBuilder("DumpNumIntent"). \
            require("DumpNumKeyword").build()
        self.register_intent(dump_intent, self.handle_dump_num_intent)

        mail_intent = IntentBuilder("MailNumIntent"). \
            require("MailNumKeyword").build()
        self.register_intent(mail_intent, self.handle_mail_num_intent)

        random_mail_intent = IntentBuilder("RandomHackedMailIntent"). \
            require("RandomMailKeyword").build()
        self.register_intent(random_mail_intent, self.handle_random_mail_intent)

        api_intent = IntentBuilder("APINumIntent"). \
            require("ApiNumKeyword").build()
        self.register_intent(api_intent, self.handle_api_num_intent)

        ssh_intent = IntentBuilder("SshNumIntent"). \
            require("SshNumKeyword").build()
        self.register_intent(ssh_intent, self.handle_ssh_num_intent)

        pgp_intent = IntentBuilder("PgpNumIntent"). \
            require("PgpNumKeyword").build()
        self.register_intent(pgp_intent, self.handle_pgp_num_intent)

        honeypot_intent = IntentBuilder("HoneypotNumIntent"). \
            require("HoneypotNumKeyword").build()
        self.register_intent(honeypot_intent, self.handle_honeypot_num_intent)

        db_intent = IntentBuilder("DbNumIntent"). \
            require("DbNumKeyword").build()
        self.register_intent(db_intent, self.handle_db_num_intent)

        cisco_intent = IntentBuilder("CiscoNumIntent"). \
            require("CiscoNumKeyword").build()
        self.register_intent(cisco_intent, self.handle_cisco_num_intent)

        start_intent = IntentBuilder("StartDumpmonIntent"). \
            require("StartDumpmonKeyword").build()
        self.register_intent(start_intent, self.handle_start_intent)

        reset_intent = IntentBuilder("ResetDumpmonIntent"). \
            require("ResetDumpmonKeyword").build()
        self.register_intent(reset_intent, self.handle_reset_dumpmon_intent)

    def handle_reset_dumpmon_intent(self, message):
        self.speak("Reseting dumpmon stats")
        self.dumpmon.reset()

    def handle_dump_num_intent(self, message):
        self.speak("Number of dumps found since startup is " + str(self.dumpmon.get_dump_num()))

    def handle_db_num_intent(self, message):
        self.speak("Number of leaked database found since startup is " + str(self.dumpmon.get_db_num()))

    def handle_random_mail_intent(self, message):
        try:
            self.speak("Here is a random e-mail that has been hacked " + str(random.choice(self.dumpmon.get_mails())))
        except:
            self.speak("i didnt find any leaked mail since startup")

    def handle_mail_num_intent(self, message):
        self.speak("Number of mails found since startup is " + str(self.dumpmon.get_mail_num()))

    def handle_api_num_intent(self, message):
        self.speak("Number of possible google APIs found since startup is " + str(self.dumpmon.get_api_num()))

    def handle_ssh_num_intent(self, message):
        self.speak("Number of possible ssh keys found since startup is " + str(self.dumpmon.get_ssh_num()))

    def handle_pgp_num_intent(self, message):
        self.speak("Number of possible pgp keys found since startup is " + str(self.dumpmon.get_pgp_num()))

    def handle_honeypot_num_intent(self, message):
        self.speak(
            "Number of possible Dionaea honeypots found since startup is " + str(self.dumpmon.get_honeypot_num()))

    def handle_cisco_num_intent(self, message):
        self.speak("Number of possible cisco found since startup is " + str(self.dumpmon.get_cisco_num()))

    def handle_start_intent(self, message):
        self.speak("Starting dumpmon module")
        self.dumpmon.start_monitor_thread()

    def stop(self):
        self.dumpmon.stop()


def create_skill():
    return DumpmonSkill()

# if __name__ == '__main__':
#    d = DumpMon()
#    while True:
#        pass
