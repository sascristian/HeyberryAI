__author__ = "Jarbas"


#     upon request this service analises sentiment and outputs the following message to the messagebus
#
#    "sentiment_result", {'text': [txt], 'result': [sent], 'confidence': [conf] }
#
#   the following output in the skills service:
#   2017-01-25 08:28:19,105 - Skills - DEBUG - {"type": "sentiment_result", "data": {"confidence": ["63.2754"], "result": ["Positive"]}, "context": null}
#
#     usage: run main.py to listen for sentiment analisys request
#
#     when making a skill and confidence retrieval is intended do something of this kind:
#
#   line = "hello world im feeling happy"
#   self.emitter.emit(
#       Message("sentiment_request",
#               {'utterances': [line]}))
#
#

