# Firefox Browser Service Skill

it is a skill that keeps a webdriver instance ready to do stuff, helper class can be imported and used in any skill to control this browser

# troubles

if it complains of geckodriver, move it into usr/bin or export it into PATH

# example, querying cleverbot website

            def handle_ask_cleverbot_intent(self, message):
                ask = message.data.get("Ask")
                # get a browser control instance, optionally set to auto-start/restart browser
                browser = BrowserControl(self.emitter)#, autostart=True)
                # restart webbrowser if it is open (optionally)
                #started = browser.start_browser()
                #if not started:
                #    # TODO throw some error
                #    return
                browser.reset_elements()
                # get clevebot url
                open = browser.open_url("www.cleverbot.com")
                if open is None:
                    return
                # search this element by type and name it "input"
                browser.get_element(data="stimulus", name="input", type="name")
                # clear element named input
                #browser.clear_element("input")
                # send text to element named "input"
                browser.send_keys_to_element(text=ask, name="input", special=False)
                # send a key_press to element named "input"
                browser.send_keys_to_element(text="RETURN", name="input", special=True)

                # wait until you find element by xpath and name it sucess
                received = False
                fails = 0
                response = " "
                while response == " ":
                    while not received and fails < 5:
                        # returns false when element wasnt found
                        # this appears only after cleverbot finishes answering
                        received = browser.get_element(data=".//*[@id='snipTextIcon']", name="sucess", type="xpath")
                        fails += 1

                    # find element by xpath, name it "response"
                    browser.get_element(data=".//*[@id='line1']/span[1]", name="response", type="xpath")
                    # get text of the element named "response"
                    response = browser.get_element_text("response")

                self.speak(response)
                # clean the used elements for this session
                browser.reset_elements()
                # optionally close the browser
                #browser.close_browser()

# logs


## Usage:

        ask cleverbot what's up
