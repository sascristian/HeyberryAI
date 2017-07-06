# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

import socket, select, sys, json, time, ssl
from threading import Thread
from os.path import dirname

from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger
from time import sleep

HOST = "174.59.239.227"
PORT = 5678

s = None
my_id = None
ws = None

names = ["jarbas"]
logger = getLogger(names[0])
sending_file = False
waiting = False
ask = False
detected = False
source = None

waiting_for_id = False


def update_id():
    global ws, waiting_for_id, s
    answer = get_msg(Message("id_update", {"id": "unknown"}))
    s.send(answer)
    # wait
    waiting_for_id = True
    start_time = time.time()
    elapsed = 0
    while waiting_for_id and elapsed <= 20:
        elapsed = time.time() - start_time
        time.sleep(0.1)
    waiting_for_id = False


def handle_speak(event):
    global my_id, source, ws
    utterance = event.data.get('utterance')
    mute = event.data.get('mute')
    target = event.context.get('destinatary', "none")
    if ":" in target:
        target = target.split(":")[1] #0/1 id or name doesnt matter
    if my_id is None:
        update_id()
    if my_id is None:
        logger.warning("Id is None, is messagebus bus service active?")

    # if the target was aimed at client itself, broadcast
    if (str(target) == my_id or str(target) in names) and not mute:
        logger.info("Speak: " + utterance)
        # redirect to all
        data = {'utterance': utterance,
                'expect_response': event.data.get('expect_response'),
                'mute': mute,
                'more': event.data.get('more'),
                'target': "all",
                "metadata": event.data.get('metadata')}
        # use source of last utterance as target? no guarantee its correct destiny, but all is not necessarily desirable
        #if source is not None and source != "unknown":
        #    data["target"] = source
        #    source = None
        #ws.emit(Message("speak", data))


def handle_id(event):
    global my_id, names, waiting_for_id
    # id is not supposed to be reset
    if my_id is None:
        my_id = str(event.data.get("id"))
    answer = get_msg(Message("names_response", {"names": names, "id": my_id}))
    s.send(answer)
    waiting_for_id = False


def handle_id_request(event):
    global my_id, names, ws
    ws.emit(Message("names_response", {"names": names, "id": my_id}))


def connect():
    ws.run_forever()


def get_msg(message):
    if hasattr(message, 'serialize'):
        return message.serialize()
    else:
        return json.dumps(message.__dict__)


def handle_utterance(event):
    global ask, detected, source
    source = event.data.get("source")
    if source is None:
        source = "unknown"
    logger.debug("Processing utterance: " + event.data.get("utterances")[0] + " from source: " + source)
    wait_answer()
    # ask server
    if not detected:
        logger.debug("No intent failure or execution detected for 20 seconds")
    if ask:
        logger.debug("Asking server for answer")
        answer = get_msg(event)
        s.send(answer)
    else:
        logger.debug("Not asking server")


def handle_intent_failure(event):
    global waiting, ask, detected
    if waiting:
        logger.debug("Intent failure detected, ending wait")
        ask = True
        waiting = False
        detected = True


def wait_answer():
    global waiting, ask, detected
    start = time.time()
    elapsed = 0
    logger.debug("Waiting for intent handling before asking server")
    waiting = True
    ask = True
    detected = False
    # wait maximum 20 seconds
    while waiting and elapsed < 20:
        elapsed = time.time() - start
        time.sleep(0.1)
    waiting = False


def end_wait(message):
    global waiting, ask, detected
    try:
        _message = json.loads(message)
        if "intent" in _message.get("type").lower() and _message.get("type") != "intent_failure" and waiting:
            logger.debug("intent handled internally")
            ask = False
            waiting = False
            detected = True
    except:
        pass


def infinite_connect():
    global s
    secs = 5
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((HOST, PORT))
            s = ssl.wrap_socket(s,
                            ca_certs=dirname(__file__) + "/certs/myapp.crt",
                            cert_reqs=ssl.CERT_REQUIRED)
            logger.debug('Connected to remote host. Start sending messages')
            return
        except Exception as e:
            logger.error('Unable to connect, error ' + str(e) + ', retrying in ' + str(secs) + ' seconds')
            logger.error("Possible causes: Server Down, Bad key, Bad Adress")

        sleep(secs)
        if secs < 150:
            secs = secs * 2


def handle_server_request(message):
    # send server a message
    stype = message.data.get("server_msg_type")
    requester = message.data.get("requester")
    message_type = message.data.get("message_type")
    message_data = message.data.get("message_data")
    message_context = message.context
    logger.info("Received request to message server from " + requester + " with type: " + str(message_type) + " with data: " + str(message_data))

    if stype == "file":
        logger.info("File requested, sending first")
        global sending_file
        sending_file = True
        bin_file = open(message_data["file"], "rb")
        # message_data["file"] = bin_file.read()
        answer = get_msg(Message("incoming_file", {"target":"server"}))
        s.send(answer)
        i = 0
        while True:
            i += 1
            chunk = bin_file.read(4096)
            print "sending chunk " + str(i)
            if not chunk:
                s.send("end_of_file")
                break  # EOF
            s.sendall(chunk)
        sending_file = False
        message_data.pop("file")
    message_data["source"] = requester
    logger.info("sending message with type: " + str(message_type))
    answer = get_msg(Message(message_type, message_data, message_context))
    s.send(answer)


def main():
    global ws, s, sending_file
    ws = WebsocketClient()
    ws.on('speak', handle_speak)
    ws.on('id', handle_id)
    ws.on('id_request', handle_id_request)
    ws.on('recognizer_loop:utterance', handle_utterance)
    ws.on('intent_failure', handle_intent_failure)
    ws.on("server_request", handle_server_request)
    ws.on('message', end_wait)

    event_thread = Thread(target=connect)
    event_thread.setDaemon(True)
    event_thread.start()

    # connect to remote host
    infinite_connect()


    try:
        while True:
            socket_list = [s]
            # Get the list sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

            for sock in read_sockets:
                if sending_file:
                    continue
                # incoming message from remote server
                if sock == s:
                    data = sock.recv(4096)
                    if not data:
                        logger.error('Disconnected from server')
                        infinite_connect()
                    else:
                        logger.debug("Received data: " + str(data))
                        message = Message.deserialize(data)
                        # emit data to bus
                        ws.emit(message)
            time.sleep(0.1)

    except KeyboardInterrupt, e:
        logger.exception(e)
        event_thread.exit()
        sys.exit()


if __name__ == "__main__":
    main()
