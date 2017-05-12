# mycroft - dumpmon skill

monitor dumpmon twitter and optionally save dumps to disk

give stats about found dumps since startup

emits to message bus a message of the format

            2017-04-27 21:54:59,276 - Skills - DEBUG - {"type": "leak_found", "data": {"source": ["http://dumpmon.com/raw/Zn2QAQCN"], "type": ["db_dump"], "path": ["/home/user/mycroft-skills/mycroft----dumped-leaks-finder----service/dumps/Zn2QAQCN_db_dump.txt"]}, "context": null}

# usage

        Input: dump number
        2017-04-27 22:04:48,204 - CLIClient - INFO - Speak: Number of dumps found since startup is 9

        Input: db number
        2017-04-27 22:04:51,201 - CLIClient - INFO - Speak: Number of leaked database found since startup is 8

        Input: mail number
        2017-04-27 22:04:54,676 - CLIClient - INFO - Speak: Number of mails found since startup is 739

        Input: cisco number
        2017-04-27 22:04:57,621 - CLIClient - INFO - Speak: Number of possible cisco found since startup is 0

        Input: ssh number
        2017-04-27 22:05:01,447 - CLIClient - INFO - Speak: Number of possible ssh keys found since startup is 0

        Input: pgp number
        2017-04-27 22:05:04,055 - CLIClient - INFO - Speak: Number of possible pgp keys found since startup is 0

        Input: google api number
        2017-04-27 22:05:07,931 - CLIClient - INFO - Speak: Number of possible google APIs found since startup is 1

        Input: dump number
        2017-04-27 22:05:16,184 - CLIClient - INFO - Speak: Number of dumps found since startup is 19

        Input: reset dumpmon
        2017-04-27 22:05:20,843 - CLIClient - INFO - Speak: Reseting dumpmon stats

        Input: mail number
        2017-04-27 22:05:25,519 - CLIClient - INFO - Speak: Number of mails found since startup is 0

        Input: honeypot number
        2017-04-27 22:05:27,678 - CLIClient - INFO - Speak: Number of possible Dionaea honeypots found since startup is 0


# more info

For a detailed overview, check out the blog post: http://raidersec.blogspot.com/2013/03/introducing-dumpmon-twitter-bot-that.html

https://twitter.com/dumpmon

forked from: https://github.com/byt3bl33d3r/dumpmon



