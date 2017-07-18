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
from Crypto.Cipher import AES
from Crypto import Random
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger
from time import sleep
from mycroft.client.client.pgp import get_own_keys, encrypt_string, decrypt_string, generate_client_key, export_key, import_key_from_ascii
import logging
import base64

gpglog = logging.getLogger("gnupg")
gpglog.setLevel("WARNING")

HOST = "174.59.239.227"
PORT = 5678

#HOST = "localhost"
#PORT = 5000

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

# current message session keys
server_key = None
server_fp = None
aes_key = None
aes_iv = None

# client pgp
ascii_public = None
public = []
private = []
key_id = None
user = 'JarbasClient@Jarbas.ai'
passwd = 'welcome to the mycroft collective'


def load_client_keys():
    global ascii_public, public, private, key_id
    encrypted = encrypt_string(user, "Jarbas client key loaded")
    if not encrypted.ok:
        key = generate_client_key(user, passwd)
        encrypted = encrypt_string(user, "Newly generated Jarbas client key loaded")

    decrypted = decrypt_string(encrypted, passwd)
    if not decrypted.ok:
        logger.error("Could not create own gpg key, do you have gpg installed?")
    else:
        logger.info(decrypted)
        public, private = get_own_keys(user)
        key_id = public[0]["fingerprint"]
        ascii_public = export_key(key_id, save=False)
        logger.info(ascii_public)


def handle_speak(event):
    global my_id, source, ws
    utterance = event.data.get('utterance')
    mute = event.data.get('mute')
    target = event.context.get('destinatary', "none")
    if ":" in target:
        target = target.split(":")[1] #0/1 id or name doesnt matter

    # if the target was aimed at client itself, log
    if (str(target) == my_id or str(target) in names) and not mute:
        logger.info("Speak: " + utterance)


def connect():
    ws.run_forever()


def get_msg(message):
    if hasattr(message, 'serialize'):
        return message.serialize()
    else:
        return json.dumps(message.__dict__)


def send_raw_data(Message, cipher="aes", message=True):
    if message:
        if Message.context is None:
            Message.context = {"source": names[0]}
        raw_data = get_msg(Message)
    else:
        raw_data = Message
    cipher = AES.new(aes_key, AES.MODE_CFB, aes_iv)
    ciphertext = aes_iv + cipher.encrypt(raw_data)
    s.send(ciphertext)


def handle_utterance(event):
    global ask, detected, source
    source = event.data.get("source", names[0])
    if source is None:
        source = "unknown"
    logger.debug("Processing utterance: " + event.data.get("utterances")[0] + " from source: " + source)
    wait_answer()
    # ask server
    if not detected:
        logger.debug("No intent failure or execution detected for 20 seconds")
    if ask:
        logger.debug("Asking server for answer")
        send_raw_data(event)
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
    c = 0
    while c <= 3:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((HOST, PORT))
            s = ssl.wrap_socket(s,
                            ca_certs=dirname(__file__) + "/certs/myapp.crt")

            logger.debug('Connected to remote host. Exchanging keys')
            key_exchange()
            logger.debug("Start sending messages")

            return
        except Exception as e:
            logger.error('Unable to connect, error ' + str(e) + ', retrying in ' + str(secs) + ' seconds')
            logger.error("Possible causes: Server Down, Bad key, Bad Adress")

        sleep(secs)
        if secs < 150:
            secs = secs * 2
        c +=1


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
        send_raw_data(Message("incoming_file", {"target": "server"}))
        i = 0
        while True:
            i += 1
            chunk = bin_file.read(4096)
            print "sending chunk " + str(i)
            if not chunk:
                send_raw_data("end_of_file", message=False)
                break  # EOF
            cipher = AES.new(aes_key, AES.MODE_CFB, aes_iv)
            cipherchunk = aes_iv + cipher.encrypt(chunk)
            s.sendall(cipherchunk)
        sending_file = False
    message_data["source"] = requester
    logger.info("sending message with type: " + str(message_type))
    send_raw_data(Message(message_type, message_data, message_context))


def key_exchange():
    status = "waiting for pgp"
    global aes_iv, aes_key, server_key, server_fp, my_id
    try:
        while True:
            socket_list = [s]
            # Get the list sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
            for sock in read_sockets:
                # incoming message from remote server
                if sock == s:
                    data = sock.recv(8192)
                    if not data:
                        logger.error('no data received')
                        return
                    else:
                        logger.debug("status: " + status)
                        if status == "waiting for pgp":
                            # save server key, use it to encrypt next message
                            message = Message.deserialize(data)
                            data = message.data
                            server_key = data.get("public_key")
                            my_id = data.get("sock_num")
                            logger.debug("Received server key: \n" + server_key)
                            import_result = import_key_from_ascii(server_key)
                            server_fp = import_result.results[0]["fingerprint"]
                            status = "waiting for aes"
                            msg = get_msg(Message("client.pgp.public.response", {"public_key": ascii_public, "names":names}))
                            logger.debug(msg)
                            msg = str(encrypt_string(server_fp, msg))
                            logger.debug("Sending pgp key to server: \n" + msg)
                            s.send(msg)
                            status = "waiting for aes"
                            logger.debug("Pgp key sent, waiting for initial AES key")
                        elif status == "waiting for aes":
                            logger.debug("Received PGP encrypted AES key Exchange\n" + str(data))
                            ciphertext = str(data)
                            decrypted = decrypt_string(ciphertext, passwd)
                            if decrypted.ok:
                                message = decrypted.data
                                logger.debug("message successfully decrypted")
                            else:
                                logger.error("Could not decrypt message: " + str(decrypted.stderr))
                                sys.exit()
                            message = Message.deserialize(message)
                            data = message.data
                            aes_iv = data["iv"]
                            aes_key = data["aes_key"]
                            aes_iv = base64.b64decode(aes_iv)
                            aes_key = base64.b64decode(aes_key)
                            send_raw_data(Message("client.aes.exchange.complete", {"status": "success"}))
                            logger.debug("Key exchange complete, you are communicating securely")
                            return
            time.sleep(0.1)

    except KeyboardInterrupt, e:
        logger.exception(e)
        sys.exit()


def main():
    load_client_keys()
    global ws, s, sending_file, aes_iv, aes_key
    ws = WebsocketClient()
    ws.on('speak', handle_speak)
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
                    data = sock.recv(8192)
                    if not data:
                        logger.error('Disconnected from server')
                        infinite_connect()
                        return
                    else:
                        logger.debug("Received data, decrypting")
                        cipher = AES.new(aes_key, AES.MODE_CFB, aes_iv)
                        decrypted_data = cipher.decrypt(data)[len(aes_iv):]
                        logger.debug("Data: " + decrypted_data)
                        deserialized_message = Message.deserialize(decrypted_data)
                        logger.debug("Message type: " + deserialized_message.type)
                        aes_iv = deserialized_message.context["aes_iv"]
                        # emit data to bus
                        ws.emit(deserialized_message)
            time.sleep(0.1)

    except KeyboardInterrupt, e:
        logger.exception(e)
        event_thread.exit()
        sys.exit()


if __name__ == "__main__":
    main()
