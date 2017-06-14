from os.path import dirname
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display


class SeleniumCleverbot():
    def __init__(self, bot="cleverbot", binary="/usr/lib/firefox-esr/firefox-esr"):
        display = Display(visible=0, size=(800, 600))
        display.start()
        self.bots = ["cleverbot", "boibot", "eviebot", "chimbot", "williambot", "pewdiebot"]
        if bot in self.bots:
            self.bot = bot
        else:
            self.bot = "cleverbot"
        self.restart()

    def available_bots(self):
        return self.bots

    def restart(self, bot=None):
        try:
            self.close()
        except:
            pass #no selenium session open
        if bot is None or bot not in self.bots:
            bot = self.bot
        self.url = "http://" + bot + ".com"
        self.browser = webdriver.Firefox()
        self.browser.get(self.url)
        self.log = []

    def ask(self, text):

        input_for_bot = self.browser.find_element_by_name("stimulus")
        input_for_bot.send_keys(text)
        input_for_bot.send_keys(Keys.RETURN)
        time.sleep(8) #this is the time to wait for the typing of cleverbot, longer answers may be cut short
        elem = self.browser.find_element_by_xpath(".//*[@id='line1']/span[1]")
        response = elem.text
        # failsafe, sometimes this happens
        empty = ["", " ", "\n"]
        while response in empty:
            response = self.ask("ask me a question")
        self.log.append(text)
        self.log.append(response)
        return response

    def close(self):
        self.browser.close()


cb = SeleniumCleverbot()#"williambot")
text = "are you siri?"
print "bot1: " + text
for i in range(0, 100):
    text = cb.ask(text)
    print "bot2: " + text
    text = cb.ask(text)
    print "bot1: " + text