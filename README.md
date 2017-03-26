# Display Service based on:

audio service from forslund
https://github.com/MycroftAI/mycroft-core/pull/433

# Changed files

mycroft.config , added displays
mycroft.skills, added displayservice.py
mycroft.skills, added display_control skill
mycroft.skills, added diplay_test skill

say: test display service to show an image using this service

# WORK IN PROGRESS - HELP WANTED

- opencv backend was working
- added pygtk backend and opencv stopped working
- cant pinpoint the change that broke this
- in add_list self.pics is a populated list, in self.show self.pics is always []
- tried a self.emitter.on in add_list, self.pics is now populated (always with first call pic)
- self.pics on emit message is always self.pics at register time! but wasnt before unhknown change!
- didnt need next and previous, so removed list altogether and directly pass pic_path into show function
- gtk backend shows picture twice, only emits one message in bus but goes twice into _show function?
- opencv is throwing a exit 139, it worked previously but i have no idea how long ago that was or what i changed

# LOGS

gtk backend log

      2017-03-27 00:01:18,329 - Skills - DEBUG - {"type": "displayTestIntent", "data": {"intent_type": "displayTestIntent", "stKeyword": "test display service", "utterance": "test display service", "confidence": 1.0, "target": null}, "context": {"target": null}}
     2017-03-27 00:01:18,341 - Skills - DEBUG - {"type": "speak", "data": {"expect_response": false, "utterance": "showing with display service"}, "context": null}
     2017-03-27 00:01:18,378 - Skills - DEBUG - {"type": "MycroftDisplayServiceShow", "data": {"picture": "/home/user/jarbas-core/mycroft/skills/display_test/test_pic.jpg", "utterance": "test display service"}, "context": null}
     2017-03-27 00:01:18,379 - Skills - DEBUG - {"type": "recognizer_loop:audio_output_start", "data": {}, "context": null}
     2017-03-27 00:01:18,380 - display_control - INFO - MycroftDisplayServiceShow
     2017-03-27 00:01:18,380 - display_control - INFO - /home/user/jarbas-core/mycroft/skills/display_test/test_pic.jpg
     2017-03-27 00:01:18,380 - display_control - INFO - opencv
     2017-03-27 00:01:18,380 - display_control - INFO - gtk
     2017-03-27 00:01:18,380 - display_control - INFO - local
     2017-03-27 00:01:18,381 - display_control - INFO - show
     2017-03-27 00:01:18,381 - display_control - INFO - stopping all displaying services
     2017-03-27 00:01:18,381 - display_control - INFO - Using default backend
     2017-03-27 00:01:18,381 - display_control - INFO - local
     2017-03-27 00:01:18,381 - display_control - INFO - Displaying
     2017-03-27 00:01:18,381 - display_control - INFO - Call pygtkServiceShow
     2017-03-27 00:01:18,382 - playback_control - INFO - lowering volume
     2017-03-27 00:01:18,385 - Skills - DEBUG - {"type": "pygtkServiceShow", "data": {"pic": "/home/user/jarbas-core/mycroft/skills/display_test/test_pic.jpg"}, "context": null}
     2017-03-27 00:01:18,385 - display_control - INFO - pygtkService._Show
     ***** close gtk window
     2017-03-27 00:02:39,142 - display_control - INFO - pygtkService._Show
     ****** new gtk window

opencv backend log

      2017-03-27 00:03:33,280 - Skills - DEBUG - {"type": "displayTestIntent", "data": {"intent_type": "displayTestIntent", "stKeyword": "test display service", "utterance": "test display service opencv", "confidence": 1.0, "target": null}, "context": {"target": null}}
     2017-03-27 00:03:33,296 - Skills - DEBUG - {"type": "speak", "data": {"expect_response": false, "utterance": "showing with display service"}, "context": null}
     2017-03-27 00:03:33,367 - Skills - DEBUG - {"type": "recognizer_loop:audio_output_start", "data": {}, "context": null}
     2017-03-27 00:03:33,385 - Skills - DEBUG - {"type": "MycroftDisplayServiceShow", "data": {"picture": "/home/user/jarbas-core/mycroft/skills/display_test/test_pic.jpg", "utterance": "test display service opencv"}, "context": null}
     2017-03-27 00:03:33,511 - display_control - INFO - MycroftDisplayServiceShow
     2017-03-27 00:03:33,511 - display_control - INFO - /home/user/jarbas-core/mycroft/skills/display_test/test_pic.jpg
     2017-03-27 00:03:33,511 - display_control - INFO - opencv
     2017-03-27 00:03:33,511 - display_control - INFO - opencv would be prefered
     2017-03-27 00:03:33,511 - display_control - INFO - show
     2017-03-27 00:03:33,512 - display_control - INFO - stopping all displaying services
     2017-03-27 00:03:33,512 - display_control - INFO - pygtkServiceStop
     2017-03-27 00:03:33,512 - display_control - INFO - Displaying
     2017-03-27 00:03:33,512 - display_control - INFO - Call OpenCVServiceShow
     2017-03-27 00:03:33,515 - Skills - DEBUG - {"type": "OpenCVServiceShow", "data": {"pic": "/home/user/jarbas-core/mycroft/skills/display_test/test_pic.jpg"}, "context": null}
     2017-03-27 00:03:33,516 - display_control - INFO - OpenCVService._Show

     Process finished with exit code 139 (interrupted by signal 11: SIGSEGV)
