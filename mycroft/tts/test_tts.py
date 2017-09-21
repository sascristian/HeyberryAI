from mycroft.tts import TTSFactory
from mycroft.messagebus.client.ws import WebsocketClient
import thread

ws = WebsocketClient()


def connect():
    global ws
    ws.run_forever()


thread.start_new_thread(connect, ())

tts = TTSFactory.create()
tts.init(ws)
tts.execute("hello world, my names is jarbas, death to all but metal")
