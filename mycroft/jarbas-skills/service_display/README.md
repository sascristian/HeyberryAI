# mycroft display service

This service is intended to be imported by other skills in order to abstract picture display

It makes no sense for all skills that display pictures to do so in completely different fashions,
this skill allows user to select display library, and in the future maybe even a remote screen

More backends can be added any time to services folder of this skill

webbrowser is used by default because everyone has a browser, webbrowser lib already is a dependency of the core, and if no browser exists the lib uses the default system image program

work in progress is opencv and gtk backends also included

# usage

Inside a skill you are developing import the service module by doing

        import sys
        from os.path import dirname
        # add skills folder to import path
        sys.path.append(dirname(dirname(__file__)))
        # import display service
        # you can do a try/except block to check if display is installed and tell user to install it otherwise
        from service_display.displayservice import DisplayService


Instead of importing you can just recreate the simple interface, but you will lose future updates to it

        from mycroft.messagebus.message import Message
        class DisplayService():
            def __init__(self, emitter):
                self.emitter = emitter

            def show(self, pic="", utterance=''):
                self.emitter.emit(Message('MycroftDisplayServiceShow',
                                          data={'picture': pic,
                                                'utterance': utterance}))


In initialize do

        self.display_service = DisplayService(self.emitter)

When actually showing the picture do

        self.display_service.show(pic_path, utterance)

The utterance will be parsed to select a backend, if no backend is specified default is used

# config

Add any display backends to the config by doing this

            "Displays": {
                "backends": {
                  "local": {
                    "type": "browser",
                    "active": true
                  },
                  "gtk": {
                    "type": "pygtk",
                    "active": false
                  },
                  "opencv": {
                    "type": "opencv",
                    "active": false
                  },
                  "browser": {
                    "type": "browser",
                    "active": true
                  }
                },
                "default-backend": "local"
              },

by default webbowser is used to open pictures (already a dependency of core), more backends can be added to show images in a different way

it is planned to add the possibility of showing in remote screens, so in the above config you could have living room, desktop, kitchen...



# install

packaged as a skill to be msm compatible and for easy install, install as if it was a normal skill