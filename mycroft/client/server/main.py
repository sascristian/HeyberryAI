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


ws = None
logger = getLogger("Mycroft_Server")

# List to keep track of socket descriptors
CONNECTION_LIST = []
RECV_BUFFER = 4096  # Advisable to keep it as an exponent of 2
PORT = 5000
server_socket = None

blacklisted_ips = []
# TODO maybe add deep dream request, but i want the utterance handled internally for now /more control
allowed_bus_messages = ["recognizer_loop:utterance", "names_response", "id_update", "incoming_file", "vision_result", "image_classification_request", "face_recognition_request"]
names = {}#name, sock this name refers to
users = {}#sock, [current user of sock]

message_queue = {}
file_socks = {} #sock num: file object


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


def get_answer(utterance, context):
    logger.debug("emitting utterance to bus: " + utterance)
    ws.emit(
       Message("recognizer_loop:utterance",
               {'utterances': [utterance.strip()]}, context))

    logger.debug("Waiting answer for user " + context["source"])


def get_msg(message):
    if hasattr(message, 'serialize'):
        return message.serialize()
    else:
        return json.dumps(message.__dict__)


def send_message(sock, type="speak", data=None, context=None):
    if data is None:
        data = {}
    message = get_msg(Message(type, data, context))
    answer_data(sock, message)


def handle_message_request(event):
    global message_queue
    user_id = event.context.get("destinatary", "")
    if ":" not in user_id:
        logger.error("invalid user_id: " + user_id)
        return
    type = event.data.get("type")
    data = event.data.get("data")
    context = event.data.get("context", {})
    context["destinatary"] = "server"
    sock_num = user_id.split(":")[1]
    logger.info("Received message request for sock:" + sock_num + " with type: " + type)
    if sock_num not in message_queue.keys():
        message_queue[sock_num] = []
    message_queue[sock_num].append([type, data, context])


def main():
    global ws
    ws = WebsocketClient()
    ws.on('speak', handle_speak)
    ws.on('intent_failure', handle_failure)
    ws.on('message_request', handle_message_request)
    event_thread = Thread(target=connect)
    event_thread.setDaemon(True)
    event_thread.start()

    global CONNECTION_LIST, RECV_BUFFER, PORT, server_socket, message_queue, users, file_socks
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
        # Get the list sockets which are ready to be read through select
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, CONNECTION_LIST, [])

        for sock in write_sockets:
            ip, sock_num = str(sock.getpeername()).replace("(", "").replace(")", "").replace(" ", "").split(",")
            if sock_num in message_queue.keys():
                i = 0
                for type, data, context in message_queue[sock_num]:
                    send_message(sock, type, data, context)
                    message_queue[sock_num].pop(i)
                    # TODO remove empty sock num in queue
                    i += 1

        for sock in read_sockets:
            # New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection received through server_socket
                try:
                    sockfd, addr = server_socket.accept()
                    # wrap in ssl
                    sockfd = ssl.wrap_socket(sockfd,
                                             server_side=True,
                                             certfile=cert,
                                             keyfile=key,
                                             ssl_version=ssl.PROTOCOL_TLSv1)
                    CONNECTION_LIST.append(sockfd)
                    logger.debug( "Client (%s, %s) connected" % addr )
                    ip, sock_num = str(addr).replace("(", "").replace(")", "").replace(" ", "").split(",")
                    # see if blacklisted
                    if ip not in blacklisted_ips:
                        # tell other clients this is available
                        #broadcast_data(sockfd, "[%s:%s] is available\n" % addr, addr)
                        # tell client it's id
                        answer_id(sockfd)
                    else:
                    #  if blacklisted kick
                        offline_client(sockfd)
                except Exception as e:
                    logger.error(e)
            # Some incoming message from a client
            else:
                # Data received from client, process it
                try:
                    utterance = sock.recv(RECV_BUFFER)
                    if utterance:
                        ip, sock_num = str(sock.getpeername()).replace("(", "").replace(")", "").replace(" ", "").split(
                            ",")
                        if sock_num not in file_socks:
                            logger.debug(
                                "received: " + str(utterance).strip() + " from socket: " + sock_num + " from ip: " + ip)
                            deserialized_message = Message.deserialize(utterance)
                            if deserialized_message.type in allowed_bus_messages:
                                data = deserialized_message.data
                                # build context
                                context = deserialized_message.context
                                if context is None:
                                    context = {}
                                if "source" not in context.keys():
                                    context["source"] = "unknown"
                                if "mute" not in context.keys():
                                    context["mute"] = True
                                context["source"] += ":" + sock_num
                                # TODO authorize user
                                if sock_num in users.keys():
                                    user = users[sock_num]
                                else:
                                    user = sock_num
                                context["user"] = user
                                # handle message
                                if deserialized_message.type == "names_response":
                                    for name in data["names"]:
                                        logger.debug("Setting alias: " + name + " for socket: " + sock_num)
                                        names[name] = sock_num
                                elif deserialized_message.type == "id_update":
                                    answer_id(sock)
                                elif deserialized_message.type == "recognizer_loop:utterance":
                                    utterance = data["utterances"][0]
                                    # get answer
                                    get_answer(utterance, context)
                                elif deserialized_message.type == "incoming_file":
                                    logger.info("started receiving file for " + str(sock_num))
                                    file_socks[sock_num] = open("../tmp_file.jpg", 'wb')
                                elif deserialized_message.type == "face_recognition_request":
                                    deserialized_message.data["file"] = "../tmp_file.jpg"
                                    ws.emit(Message(deserialized_message.type, deserialized_message.data, context))
                                elif deserialized_message.type == "vision_result":
                                    deserialized_message.data["feed_path"] = "../tmp_file.jpg"
                                    ws.emit(Message(deserialized_message.type, deserialized_message.data, context))
                                elif deserialized_message.type == "image_classification_request":
                                    deserialized_message.data["file"] = "../tmp_file.jpg"
                                    ws.emit(Message(deserialized_message.type, deserialized_message.data, context))
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

                except Exception as e:
                    logger.error(e)
                    offline_client(sock)
                    continue
    server_socket.close()


if __name__ == "__main__":
    main()
