

import unirest

from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger

client = None

logger = getLogger("SentimentClient")

def connect():
    client.run_forever()

mashapekey = "get yours man"

def sentiment3(txt):
    #https://market.mashape.com/vivekn/sentiment-3#sentiment
    response = unirest.post("https://community-sentiment.p.mashape.com/text/",
                            headers={
                                "X-Mashape-Key": mashapekey,
                                "Content-Type": "application/x-www-form-urlencoded",
                                "Accept": "application/json"
                            },
                            params={
                                "txt": txt
                            }
                            )
    sentiment = response.body["result"]["sentiment"]
    confidence = response.body["result"]["confidence"]
    return sentiment, str(confidence)

def sentiment2(txt):
    #https://market.mashape.com/sentity/sentity-text-analytics
    txt = txt.replace(" ", "+")
    response = unirest.get("https://sentity-v1.p.mashape.com/v1/sentiment?text=" + txt,
                           headers={
                               "X-Mashape-Key": mashapekey,
                               "Accept": "application/json"
                           }
                           )
    pos = response.body["pos"]
    neg = response.body["neg"]
    confidence = " pos: " + str(pos) + " neg: " + str(neg)
    # print sentiment
    # do some processing instead of printing
    if neg < 0.5 and pos > 0.5:
        sentiment = "positive"
    elif pos < 0.5 and neg > 0.5:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    # return sentiment, confidence
    return sentiment, pos, neg

def sentiment(txt):
    #https://market.mashape.com/mtnfog/cloud-nlp
    txt = txt.replace(" ", "+")
    response = unirest.get("https://mtnfog-cloud-nlp-v1.p.mashape.com/sentiment?text=" + txt,
                           headers={
                               "X-Mashape-Key": mashapekey,
                               "Accept": "application/json"
                           }
                           )
    confidence = response.body

    if confidence > 0:
        sentiment = "positive"
    elif confidence < 0:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    # sentiment =
    return sentiment, str(confidence)

def main():
    global client
    client = WebsocketClient()
    uterancemsg = "sentiment_request"

    def sent(message):
        txt = message.data.get('utterances')[0]
        sent = "unknown"
        posconf = 0
        negconf = 0
        try:
            sent, posconf, negconf = sentiment2(txt)
            #print sent
            #print posconf
            #print negconf
            #sent, conf = sentiment3(txt)

        except:
            print "couldnt reach sentiment api"

        client.emit(
            Message("sentiment_result",
                    {'text': [txt], 'result': [sent], 'conf+': [posconf], 'conf-': [negconf]}))
        # {'text':[txt], 'result': [sent], 'confidence': [conf]}))
        logger.info("text: " + txt + " sentiment: " + sent + " confidence: +" + str(posconf) + " - " + str(negconf))


    client.emitter.on(uterancemsg, sent)
    connect()

if __name__ == '__main__':
    main()
