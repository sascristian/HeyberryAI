# Mycroft style transfer service

work in progress

performs style transfer using caffe, based on [this code](https://github.com/fzliu/style-transfer)

takes up to 7 hours, still testing

 # install

 you must have caffe installed, add a "caffe_path" to your config

        caffe_path = ConfigurationManager.get("caffe_path")

 run requirements.sh to download VGG16 model

 # usage


        Input: style transfer
        2017-06-28 13:52:46,483 - CLIClient - INFO - Speak: testing style transfer
        2017-06-28 13:52:46,680 - CLIClient - INFO - Speak: Starting style transfer, this may take up to 7 hours, i will let you know when ready
        2017-06-28 19:39:32,127 - CLIClient - INFO - Speak: style transfer result url: http://i.imgur.com/cVRpafO.jpg
 # logs


