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

import ssl, socket, select, json
from os.path import dirname
from threading import Thread

from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger
from mycroft.util.jarbas_services import UserManagerService
from mycroft.util.jarbas_services import ServiceBackend

from mycroft.skills.intent_service import IntentParser
from mycroft.client.server.pgp import get_own_keys, encrypt_string, decrypt_string, generate_server_key, export_key, import_key_from_ascii
from Crypto.Cipher import AES
from Crypto import Random
import logging
import sys
import base64

ws = None
parser = None
user_manager = None
service = None

NAME = "Jarbas_Server"
logger = getLogger(NAME)

gpglog = logging.getLogger("gnupg")
gpglog.setLevel("WARNING")


# List to keep track of socket descriptors
CONNECTION_LIST = []
RECV_BUFFER = 8192  # Advisable to keep it as an exponent of 2
PORT = 5000
server_socket = None

# TODO read from config
blacklisted_ips = []
whitelisted_ips = []
blacklist = True

allowed_bus_messages = ["recognizer_loop:utterance",
                        "names_response",
                        "id_update",
                        "incoming_file",
                        "vision_result",
                        "vision.faces.result",
                        "vision.feed.result",
                        "image.classification.request",
                        "style.transfer.request",
                        "class.visualization.request",
                        "face.recognition.request",
                        "object.recognition.request",
                        "client.pgp.public.request",
                        "client.pgp.public.response",
                        "client.aes.exchange_complete"
                        ]

names = {} #sock : [names]
sock_ciphers = {} #sock : {iv, cipherobject}

message_queue = {}
file_socks = {} #sock num: file object
exchange_socks = {} #sock_num, key exhcnage status


# server pgp keys
user = 'Jarbas@Jarbas.ai'
passwd = 'welcome to the mycroft collective'

ascii_public = None
key_id = None
public = []
private = []


def load_server_keys():
    global ascii_public, key_id, public, private
    public, private = get_own_keys(user)

    encrypted = encrypt_string(user, "Jarbas server key loaded")
    if not encrypted.ok:
        key = generate_server_key(user, passwd)
        encrypted = encrypt_string(user, "Jarbas server key loaded")

    decrypted = decrypt_string(encrypted, passwd)
    if not decrypted.ok:
        logger.error("Could not create own gpg key, do you have gpg installed?")
        sys.exit()
    else:
        logger.info(decrypted)
        key_id = public[0]["fingerprint"]
        ascii_public = export_key(key_id, save=False)
        logger.info(ascii_public)


class KeyExchangeService(ServiceBackend):
    def __init__(self, emitter=None, timeout=5, waiting_messages=["client.pgp.public.response", "client.aes.exchange.complete"], logger=None):
        super(KeyExchangeService, self).__init__(name="KeyExchangeService", emitter=emitter, timeout=timeout,
                                                 waiting_messages=waiting_messages, logger=logger)

    def pgp_request(self, sock_num):
        message_type = "client.pgp.public.request"
        message_data = {"public_key": ascii_public, "fingerprint": key_id, "cipher": "none"}
        message_context = {"sock_num": sock_num}
        self.send_request(message_type=message_type, message_data=message_data, message_context=message_context, client=True)
        self.wait("client.pgp.public.response")
        return self.result

    def aes_key_exchange(self, sock_num, iv=None, key=None):
        message_type = "client.aes.key"
        iv, key = self.aes_generate_pair(iv, key)
        iv = base64.b64encode(iv)
        key = base64.b64encode(key)
        sock_ciphers[sock_num]["aes_key"] = key
        sock_ciphers[sock_num]["aes_iv"] = iv
        message_data = {"aes_key": key, "iv": iv, "cipher": "pgp"}
        message_context = {"sock_num": sock_num}
        self.send_request(message_type=message_type, message_data=message_data, message_context=message_context,
                          client=True)
        self.wait("client.aes.exchange.complete")
        self.logger.info("AES Exchange result:" + str(self.result))
        return self.result


    def aes_generate_pair(self, iv=None, key=None):
        if iv is None:
            iv = Random.new().read(AES.block_size)
        if key is None:
            key = Random.get_random_bytes(32)
        return iv, key


def key_exchange(sock):
    global exchange_socks
    ip, sock_num = str(sock.getpeername()).replace("(", "").replace(")", "").replace(" ", "").split(",")
    # send pgp request
    status = "sending pgp"
    exchange_socks[sock_num] = {"sock": sock, "status": status}
    sock_ciphers[sock_num] = {}
    logger.info("Sending public pgp key to client")
    client_data = service.pgp_request(sock_num)
    client_pgp = client_data.get("public_key")
    if client_pgp is None:
        logger.error("Could not receive pgp key")
        offline_client(sock)
        exchange_socks.pop(sock_num)
        return
    logger.info("Received client public pgp key: \n" + client_pgp)
    # save user pgp key
    logger.info("importing client pgp key")
    import_result = import_key_from_ascii(client_pgp)
    fp = import_result.results[0]["fingerprint"]
    sock_ciphers[sock_num]["pgp"] = client_pgp
    sock_ciphers[sock_num]["fingerprint"] = fp
    logger.info("fingerprint: " + str(fp))
    sock_ciphers[sock_num]["user"] = client_data.get("user")

    # generate and send aes key to client
    logger.info("Initiating AES key exchange")
    status = "sending aes key"
    exchange_socks[sock_num] = {"sock": sock, "status": status}
    aes_result = service.aes_key_exchange(sock_num)
    if "status" not in aes_result.keys():
        logger.error("AES exchange failed")
        offline_client(sock)
        # TODO counter, and ban on many reconnect attempts
    else:
        logger.info("Key exchange complete")
    exchange_socks.pop(sock_num)


def handle_failure(event):
    # TODO warn user of possible lack of answer (wait for wolfram alpha x seconds first)
    logger.debug("intent failure detected")


def handle_speak(event):
    global message_queue
    target = event.context.get('destinatary', "all")
    if ":" not in target:
        return
    utterance = event.data.get('utterance', "")
    logger.debug("Answer: " + utterance + " Target: " + target)
    target, sock_num = target.split(":")
    answer_type = "speak"
    if sock_num not in message_queue.keys():
        message_queue[sock_num] = []
    logger.debug("Adding answer to answering queue")
    message_queue[sock_num].append([answer_type, event.data, event.context])


def connect():
    ws.run_forever()


# Function to broadcast messages to all connected clients
def broadcast_data(sock, message):
    # Do not send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock:
            try:
                logger.debug("Broadcasting " + message)
                socket.send(message)
            except:
                # broken socket connection may be, chat client pressed ctrl+c for example
                # offline_client(sock, addr)
                pass


# answer
def answer_data(sock, message):
    # send the message to the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket == sock:
            try:
                socket.send(message)
            except:
                # broken socket connection may be, chat client pressed ctrl+c for example
                offline_client(sock)


def offline_client(sock):
    global names
    try:
        sock.close()
        CONNECTION_LIST.remove(sock)
        # broadcast_data(sock, "Client (%s, %s) is offline" % addr)
        ip, sock_num = str(sock.getpeername()).replace("(", "").replace(")", "").replace(" ", "").split(",")
        logger.debug("Client is offline: " + str(sock.getpeername()))
        names.pop(sock_num, None)
        ws.emit(Message("user.disconnect", {"ip": ip, "sock": sock_num}))
    except:
        # already removed
        pass


# answer id
def answer_id(sock):
    # send the message to the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket == sock:
            try:
                ip, sock_num = sock.getpeername()
                logger.debug("Sending Id to Client " + str(sock.getpeername()))
                answer = get_msg(Message("id", {"id": sock_num}))
                socket.send(answer)
            except:
                # broken socket connection may be, chat client pressed ctrl+c for example
                offline_client(sock)


def get_answer(utterance, user_data, context):
    global parser
    # check if skill/intent that will trigger is authorized for this user
    intent, skill = parser.determine_intent(utterance)
    if intent in user_data["forbidden_intents"]:
        logger.warning("Intent " + intent + " is not allowed for " + user_data["nicknames"][0])
        return

    if skill in user_data["forbidden_skills"]:
        logger.warning("Skill " + skill + " is not allowed for " + user_data["nicknames"][0])
        return
    logger.debug("emitting utterance to bus: " + str(utterance))
    ws.emit(
       Message("recognizer_loop:utterance",
               {'utterances': [utterance.strip()]}, context))

    logger.debug("Waiting answer for user " + context["source"])


def get_msg(message):
    if hasattr(message, 'serialize'):
        return message.serialize()
    else:
        return json.dumps(message.__dict__)


def send_message(sock, type="speak", data=None, context=None, cipher="none"):
    global sock_ciphers
    if data is None:
        data = {}
    ip, num = str(sock.getpeername()).replace("(", "").replace(")", "").replace(" ", "").split(",")
    message = get_msg(Message(type, data, context))
    if cipher == "pgp":
        logger.debug("target pgp fingerprint: " + str(sock_ciphers[num].get("fingerprint")))
        message = encrypt_string(sock_ciphers[num].get("fingerprint"), message)
        if not message.ok:
            logger.error("Encryption failed: " + message.stderr)
            # TODO throw error
        else:
            message = str(message)
    if cipher == "aes":
        # rotate key
        iv, key = service.aes_generate_pair()
        iv = base64.b64encode(iv)
        key = base64.b64encode(key)
        sock_ciphers[num]["aes_iv"] = iv
        sock_ciphers[num]["aes_iv"] = key
        cipher = AES.new(key, AES.MODE_CFB, iv)
        context["aes_iv"] = iv
        context["aes_key"] = key
        message = get_msg(Message(type, data, context))
        message = cipher.encrypt(message)
    answer_data(sock, message)
    return message


def handle_message_request(event):
    global message_queue
    # TODO allow files
    type = event.data.get("type", "bus")
    logger.info("Request to message client received: " + type)
    cipher = event.data.get("cipher", "none")
    # merge contexts of message and message_request
    context = event.context
    if context is None:
        context = {}
    context.update(event.data.get("context", {}))
    # allow user to be requested explictly
    user_id = event.data.get("user_id")
    if user_id is None:
        user_id = event.context.get("sock_num")
        if user_id is None:
            # if not, use context
            user_id = context.get("destinatary", "")
        else:
            user_id = event.data.get("requester", "server_skills")+":"+user_id

    if ":" not in str(user_id):
        logger.error("Message_Request: invalid user_id: " + user_id + " in data: " + str(event.data) + " in context: " + str(context))
        return
    context["source"] = event.data.get("requester", "skills") + ":server"
    data = event.data.get("data", {})
    if cipher == "none" and "cipher" in data.keys():
        cipher = data["cipher"]
    sock_num = user_id.split(":")[1]
    logger.info("Message_Request: sock:" + sock_num + " with type: " + type + " with data: " + str(data))
    if sock_num not in message_queue.keys():
        message_queue[sock_num] = []
    message_queue[sock_num].append([type, data, context, cipher])
    logger.info("Added to queue")
    logger.info(message_queue)


def main():
    global ws, parser, user_manager, service
    # load pgp keys
    load_server_keys()
    # initialize websocket
    ws = WebsocketClient()
    ws.on('speak', handle_speak)
    ws.on('intent_failure', handle_failure)
    ws.on('message_request', handle_message_request)
    event_thread = Thread(target=connect)
    event_thread.setDaemon(True)
    event_thread.start()
    # initialize intent parser, usermanager, and keyexchange service
    parser = IntentParser(ws)
    user_manager = UserManagerService(ws)
    service = KeyExchangeService(ws)

    global CONNECTION_LIST, RECV_BUFFER, PORT, server_socket, message_queue, file_socks
    # start server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)

    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)

    logger.debug("Listening started on port " + str(PORT))

    # read cert and key
    cert = dirname(__file__) + "/certs/myapp.crt"
    key = dirname(__file__) + "/certs/myapp.key"

    while True:
        # Get the list sockets which are ready to be read / written through select
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, CONNECTION_LIST, [])

        for sock in write_sockets:
            # Send any queued messages to target socket
            try:
                ip, sock_num = str(sock.getpeername()).replace("(", "").replace(")", "").replace(" ", "").split(
                 ",")
            except:
                logger.error("Socket disconnected")
                offline_client(sock)
                continue
            if sock_num in message_queue.keys():
                i = 0
                logger.debug("Processing queue")
                logger.debug(message_queue)
                for type, data, context, cipher in message_queue[sock_num]:
                    if cipher == "none" and "cipher" in data.keys():
                        cipher = data["cipher"]
                    logger.debug("Answering sock " + sock_num)
                    try:
                        logger.debug("Encryption: " + cipher)
                        message = send_message(sock, type, data, context, cipher=cipher)
                        message_queue[sock_num].pop(i)
                        if len(message_queue[sock_num]) == 0:
                            message_queue[sock_num] = None
                            message_queue.pop(sock_num)
                        i += 1
                        logger.debug("Sucessfully sent data: \n" + str(message))
                    except Exception as e:
                        logger.debug("Answering sock " + sock_num + " failed with: " + str(e))

        for sock in read_sockets:
            # Handle the case in which there is a new connection received through server_socket
            if sock == server_socket:
                try:
                    sockfd, addr = server_socket.accept()
                    ip, sock_num = str(addr).replace("(", "").replace(")", "").replace(" ", "").split(",")
                    # see if blacklisted
                    if ip in blacklisted_ips and blacklist:
                        logger.warning("Blacklisted ip tried to connect: " + ip)
                        #  if blacklisted kick
                        offline_client(sockfd)
                        continue
                    elif ip not in whitelisted_ips and not blacklist:
                        logger.warning("Unknown ip tried to connect: " + ip)
                        #  if not whitelisted kick
                        offline_client(sockfd)
                        continue
                    # wrap in ssl
                    sockfd = ssl.wrap_socket(sockfd,
                                             server_side=True,
                                             certfile=cert,
                                             keyfile=key,
                                             ssl_version=ssl.PROTOCOL_TLSv1)
                    CONNECTION_LIST.append(sockfd)
                    logger.debug( "Client (%s, %s) connected" % addr )
                    key_thread = Thread(target=key_exchange, args=[sockfd])
                    key_thread.setDaemon(True)
                    key_thread.start()
                    context = {"user": sock_ciphers.get(sock_num, {}).get("user", "unknown"), "source": ip + ":" + str(sock_num)}
                    ws.emit(Message("user.connect", {"ip": ip, "sock": sock_num, "pub_key": sock_ciphers.get(sock_num, {}).get("pgp")}, context))
                    # tell client it's id
                   # answer_id(sockfd)
                except Exception as e:
                    logger.error(e)

            # Some incoming message from a client
            else:
                try:
                    ip, sock_num = str(sock.getpeername()).replace("(", "").replace(")", "").replace(" ", "").split(
                        ",")
                except:
                    logger.error("Socket disconnected")
                    offline_client(sock)
                    continue
                # performing key exchange
                if sock_num in exchange_socks:
                    status = exchange_socks[sock_num]["status"]
                    logger.debug("current status: " + status)
                    try:
                        ciphertext = sock.recv(RECV_BUFFER)
                        if not ciphertext:
                            offline_client(sock)
                            continue
                        if status == "sending pgp":
                            # receiving client pub key, encrypted with server public key
                            logger.debug("Received PGP encrypted message: " + ciphertext)
                            logger.debug("Attempting to decrypt")
                            decrypted_data = decrypt_string(ciphertext, passwd)
                            if decrypted_data.ok:
                                utterance = str(decrypted_data.data)
                                logger.debug("Decrypted message: " + utterance)
                            else:
                                logger.error("Client did not use our public key")
                                offline_client(sock)
                                continue
                            deserialized_message = Message.deserialize(utterance)
                            logger.debug("Message type: " + deserialized_message.type)

                        elif status == "sending aes key":
                            # received aes encrypted response
                            logger.debug("Received AES encrypted message: " + ciphertext)
                            logger.debug("Attempting to decrypt aes message")
                            key = sock_ciphers[sock_num]["aes_key"]
                            iv = sock_ciphers[sock_num]["aes_iv"]
                            iv = base64.b64decode(iv)
                            key = base64.b64decode(key)
                            cipher = AES.new(key, AES.MODE_CFB, iv)
                            decrypted_data = cipher.decrypt(ciphertext)[len(iv):]
                            logger.debug("Decrypted message: " + decrypted_data)
                            deserialized_message = Message.deserialize(decrypted_data)
                            logger.debug("Message type: " + deserialized_message.type)
                        ws.emit(
                            Message(deserialized_message.type, deserialized_message.data, deserialized_message.context))

                    except:
                        offline_client(sock)
                    continue

                # Data received from client, process it
                try:
                    utterance = sock.recv(RECV_BUFFER)

                    if utterance:
                        logger.debug("Received AES encrypted message: " + utterance)
                        logger.debug("Attempting to decrypt")
                        key = sock_ciphers[sock_num]["aes_key"]
                        iv = sock_ciphers[sock_num]["aes_iv"]
                        iv = base64.b64decode(iv)
                        key = base64.b64decode(key)
                        cipher = AES.new(key, AES.MODE_CFB, iv)
                        utterance = cipher.decrypt(utterance)[len(iv):]
                        logger.debug("Decryption result: " + utterance)
                        if sock_num not in file_socks:
                            logger.debug(
                                "received: " + str(utterance).strip() + " from socket: " + sock_num + " from ip: " + ip)

                            deserialized_message = Message.deserialize(utterance)
                            logger.debug("Message type: " + deserialized_message.type )
                            if deserialized_message.type in allowed_bus_messages:
                                data = deserialized_message.data
                                # build context
                                context = deserialized_message.context
                                if context is None:
                                    context = {}
                                if "source" not in context.keys():
                                    if sock_num in names.keys():
                                        context["source"] = names[sock_num][0]
                                    else:
                                        context["source"] = "unknown"
                                if "mute" not in context.keys():
                                    context["mute"] = True
                                context["source"] = str(context["source"]) + ":" + sock_num
                                context["ip"] = ip

                                # authorize user message_type
                                # get user from sock
                                user_data = user_manager.user_from_sock(sock_num)
                                # see if this user can perform this action
                                if deserialized_message.type in user_data.get("forbidden_messages",[]):
                                    logger.warning("This user is not allowed to perform this action " + str(sock_num))
                                    continue
                                user = user_data["id"]

                                context["user"] = user
                                # handle message

                                # check if message also sent files
                                if "file" in deserialized_message.data.keys():
                                    deserialized_message.data["file"] = "../tmp_file.jpg"
                                elif "feed_path" in deserialized_message.data.keys():
                                    deserialized_message.data["feed_path"] = "../tmp_file.jpg"
                                elif "path" in deserialized_message.data.keys():
                                    deserialized_message.data["path"] = "../tmp_file.jpg"

                                # pre-process message type
                                if deserialized_message.type == "names_response":
                                    for name in data["names"]:
                                        logger.debug("Setting alias: " + name + " for socket: " + sock_num)
                                        if sock_num not in names.keys():
                                            names[sock_num] = []
                                        names[sock_num].append(name)
                                    ws.emit(
                                        Message("user.names", {"names": data["names"], "sock": sock_num, "ip": ip}, context))
                                elif deserialized_message.type == "id_update":
                                    answer_id(sock)
                                elif deserialized_message.type == "recognizer_loop:utterance":
                                    utterance = data["utterances"][0]
                                    # get answer
                                    get_answer(utterance, user_data, context)
                                elif deserialized_message.type == "incoming_file":
                                    logger.info("started receiving file for " + str(sock_num))
                                    file_socks[sock_num] = open("../tmp_file.jpg", 'wb')
                                else:
                                    logger.info("no special handling provided for " + deserialized_message.type)
                                    # message is whitelisted and no special handling was provided
                                    ws.emit(Message(deserialized_message.type, deserialized_message.data, context))

                        else:
                            if utterance == "end_of_file":
                                logger.info("file received for " + str(sock_num))
                                file_socks[sock_num].close()
                                file_socks.pop(sock_num)
                            else:
                                logger.info("file chunk received for " + str(sock_num))
                                file_socks[sock_num].write(utterance)

                        ws.emit(Message("user.request", {"ip": ip, "sock": sock_num}))

                except Exception as e:
                    logger.error(e)
                    offline_client(sock)
                    continue
    server_socket.close()


if __name__ == "__main__":
    main()
