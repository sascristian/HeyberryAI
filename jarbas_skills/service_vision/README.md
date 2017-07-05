# mycroft-vision-skill

Listens to messagebus "vision_request" queries, replies with info of what is in vision field

Processes images for face detection, eye detection and smile detection

work in progress - motion detection, face recognition

Optionally applies image filters before displaying

Takes webcam pictures


# requirements

you must install opencv manually, it does not work from pip install, therefore msm incompatible

pip install imutils

requires display service to show pictures - https://github.com/JarbasAI/service_display

# usage

        Input: what do you see
        2017-05-07 16:23:45,035 - CLIClient - INFO - Speak: Here is what i see
        * shows feed (with filter if enabled)

        Input: describe what you see
        2017-05-07 16:23:45,035 - CLIClient - INFO - Speak: Here is what i see
        * shows feed (with filter if enabled)

        Input: vision data
        2017-05-07 16:29:00,117 - CLIClient - INFO - Speak: There are 0 persons on view
        2017-05-07 16:29:00,122 - CLIClient - INFO - Speak: Noone is smiling

        Input: smooth filter
        2017-05-07 16:29:49,905 - CLIClient - INFO - Speak: smooth filter enabled

        Input: skeleton filter
        2017-05-07 16:29:53,411 - CLIClient - INFO - Speak: skeleton filter enabled

        Input: thresh filter
        2017-05-07 16:29:56,608 - CLIClient - INFO - Speak: threshold filter enabled

        Input: detail filter
        2017-05-07 16:29:59,374 - CLIClient - INFO - Speak: detail filter enabled

        Input: no filter
        2017-05-07 16:30:01,273 - CLIClient - INFO - Speak: filters disabled

        Input: webcam picture
        2017-05-07 16:48:21,730 - CLIClient - INFO - Speak: saving picture
        * saves pic (with filter if enabled)
        * shows pic (with filter if enabled)

# TODO

- facerecognition interface -> https://github.com/JarbasAI/face_recog_skill
- show bounding boxes intent
- movement detection
- more filters
- distance calculation