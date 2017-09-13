# system and crypto libs

import sys
from Crypto.Cipher import AES
from Crypto import Random
import logging
import base64
import json
import time
from os.path import dirname, exists
from threading import Thread

# websocket libs

from twisted.internet import reactor, ssl
from twisted.python import log
from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

# mycroft libs

from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger
from jarbas_utils.skill_tools import UserManagerQuery

from mycroft.skills.intent_service import IntentParser
from mycroft.client.server.pgp import get_own_keys, encrypt_string, decrypt_string, generate_server_key, export_key, \
    import_key_from_ascii
from mycroft.configuration import ConfigurationManager
from mycroft.client.server.self_signed import create_self_signed_cert
config = ConfigurationManager.get()
config = config.get("jarbas_server", {})

# logs
NAME = "Jarbas_Server"
logger = getLogger(NAME)

gpglog = logging.getLogger("gnupg")
gpglog.setLevel("WARNING")


# how to react to messages
class MyServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        logger.info("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        """
       Connection from client is opened. Fires after opening
       websockets handshake has been completed and we can send
       and receive messages.

       Register client in factory, so that it is able to track it.
       """
        self.factory.register_client(self)
        self.factory.request_client_pgp(self)
        logger.info("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            logger.info("Binary message received: {0} bytes".format(len(payload)))
        else:
            logger.info("Text message received: {0}".format(payload.decode('utf8')))

        self.factory.process_message(self, payload, isBinary)

    def onClose(self, wasClean, code, reason):
        logger.info("WebSocket connection closed: {0}".format(reason))

    def connectionLost(self, reason):
        """
       Client lost connection, either disconnected or some error.
       Remove client from list of tracked connections.
       """
        self.factory.unregister_client(self, reason=u"connection lost")
        logger.info("WebSocket connection closed: {0}".format(reason))


# server internals
class MyServerFactory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        super(MyServerFactory, self).__init__(*args, **kwargs)
        # list of clients
        self.clients = {}
        # server keys
        self.public = []
        self.private = []
        self.key_id = None
        self.ascii_public = None
        self.user = config.get("pgp_user", 'Jarbas@Jarbas.ai')
        self.passwd = config.get("pgp_passwd", 'welcome to the mycroft collective')
        self.load_server_keys()
        # mycroft_ws
        self.emitter = None
        self.emitter_thread = None
        self.create_internal_emitter()
        # mycroft utils
        self.parser = IntentParser(self.emitter)
        self.user_manager = UserManagerQuery(name="server_ClientManager",
                                             emitter=self.emitter)

        # messages to send queue
        self.message_queue = []
        self.queue_thread = Thread(target=self._queue)
        self.queue_thread.setDaemon(True)
        self.queue_thread.start()

        # allowed data
        self.ip_list = config.get("ip_list", [])
        self.ip_blacklist = config.get("ip_policy", "blacklist") == "blacklist"

        self.message_blacklist = config.get("message_policy", "blacklist") == "blacklist"
        self.bus_message_list = ["recognizer_loop:utterance",
                                 "names_response",
                                 "id_update",
                                 "incoming_file",
                                 "vision_result",
                                 "vision.faces.result",
                                 "vision.feed.result",
                                 "deep.dream.request",
                                 "image.classification.request",
                                 "style.transfer.request",
                                 "class.visualization.request",
                                 "face.recognition.request",
                                 "object.recognition.request",
                                 "client.pgp.public.request",
                                 "client.pgp.public.response",
                                 "client.aes.exchange_complete"
                                 ]
        self.bus_message_list = config.get("message_list", self.bus_message_list)

        self.file_socks = {}

    # initialize methods
    def load_server_keys(self):
        self.public, self.private = get_own_keys(self.user)

        encrypted = encrypt_string(self.user, "Jarbas server key loaded")
        if not encrypted.ok:
            key = generate_server_key(self.user, self.passwd)
            encrypted = encrypt_string(self.user, "Jarbas server key loaded")
            self.public, self.private = get_own_keys(self.user)

        decrypted = decrypt_string(encrypted, self.passwd)
        if not decrypted.ok:
            logger.error("Could not create own gpg key, do you have gpg installed?")
            sys.exit()
        else:
            logger.info(decrypted)
            self.key_id = self.public[0]["fingerprint"]
            self.ascii_public = export_key(self.key_id, save=False)
            logger.info(self.ascii_public)

    def connect_to_internal_emitter(self):
        self.emitter.run_forever()

    def create_internal_emitter(self):
        # connect to mycroft internal websocket
        self.emitter = WebsocketClient()
        self.register_internal_messages()
        self.emitter_thread = Thread(target=self.connect_to_internal_emitter)
        self.emitter_thread.setDaemon(True)
        self.emitter_thread.start()

    def register_internal_messages(self):
        self.emitter.on('speak', self.handle_speak)
        self.emitter.on('complete_intent_failure', self.handle_failure)
        self.emitter.on('client.message.request',
                        self.handle_message_to_sock_request)

    def request_client_pgp(self, client, cipher="none"):
        type, ip, sock_num = client.peer.split(":")
        # send pgp request
        logger.info("Sending public pgp key to client")
        message_type = "client.pgp.public.request"
        message_data = {"public_key": self.ascii_public, "fingerprint": self.key_id, "cipher": cipher,
                        "sock_num": sock_num}
        message_context = {"sock_num": sock_num}
        self.send_message(client, message_type, message_data, message_context, cipher)

    # utils
    def aes_generate_pair(self, iv=None, key=None):
        if iv is None:
            iv = Random.new().read(AES.block_size)
        if key is None:
            key = Random.get_random_bytes(32)
        return iv, key

    # webasocket handlers
    def register_client(self, client):
        """
       Add client to list of managed connections.
       """
        logger.info("registering client: " + str(client.peer))
        t, ip, sock = client.peer.split(":")
        # see if blacklisted
        if ip in self.ip_list and self.ip_blacklist:
            logger.warning("Blacklisted ip tried to connect: " + ip)
            self.unregister_client(client, reason=u"Blacklisted ip")
            return
        elif ip not in self.ip_list and not self.ip_blacklist:
            logger.warning("Unknown ip tried to connect: " + ip)
            #  if not whitelisted kick
            self.unregister_client(client, reason=u"Unknown ip")
            return
        self.clients[client.peer] = {"object": client, "status": "waiting pgp", "aes_key": None, "aes_iv": None,
                                     "user_object": None, "pgp": None, "fingerprint": None}

    def unregister_client(self, client, code=3078, reason=u"unregister client request"):
        """
       Remove client from list of managed connections.
       """
        logger.info("deregistering client: " + str(client.peer))
        if client.peer in self.clients.keys():
            client_data = self.clients[client.peer]
            j, ip, sock_num = client.peer.split(":")
            context = {"user": client_data.get("names", ["unknown_user"])[0],
                       "source": ip +  ":" + str(sock_num)}
            self.emitter.emit(
                Message("user.disconnect",
                        {"reason": reason, "ip": ip, "sock": sock_num,
                         "pub_key": client_data.get("pgp", None), "nicknames":
                             client_data.get("names",[])},
                        context))
            client.sendClose(code, reason)
            self.clients.pop(client.peer)

    # internals
    def _queue(self):
        while True:
            for msg in self.message_queue:
                logger.debug("Processing queue")
                if msg[4] == "none" and "cipher" in msg[2].keys():
                    msg[4] = msg[2]["cipher"]
                logger.debug("Encryption: " + msg[4])
                self.send_message(msg[0], msg[1], msg[2], msg[3], msg[4])
                self.message_queue.remove(msg)
                logger.debug("Sucessfully sent encrypted data")
            time.sleep(0.1)

    def process_message(self, client, payload, isBinary):
        """
       Process message from client
       """
        logger.info("processing message from client: " + str(client.peer))
        client_data = self.clients[client.peer]
        client_type, ip, sock_num = client.peer.split(":")
        if client_data["status"] == "waiting pgp":
            logger.info("Receiving public pgp key")
            decrypted_data = decrypt_string(payload, self.passwd)
            if decrypted_data.ok:
                utterance = str(decrypted_data.data)
                logger.info("Decrypted: " + utterance)
            else:
                logger.error("Client did not use our public key")
                # TODO error
                return
            try:
                deserialized_message = Message.deserialize(utterance)
            except Exception as e:
                logger.error("Unknown data received: " + str(e))
                # TODO error
                return
            client_data = deserialized_message.data
            client_pgp = client_data["public_key"]
            self.clients[client.peer]["names"] = client_data.get("names", ["unnamed user"])
            if client_pgp is None:
                logger.error("Could not receive pgp key")
                return
            logger.info("Received client public pgp key: \n" + client_pgp)
            # save user pgp key
            logger.info("importing client pgp key")
            import_result = import_key_from_ascii(client_pgp)
            fp = import_result.results[0]["fingerprint"]
            self.clients[client.peer]["pgp"] = client_pgp
            self.clients[client.peer]["fingerprint"] = fp
            logger.info("fingerprint: " + str(fp))
            self.clients[client.peer]["user"] = client_data.get("user")
            # generate and send aes key to client
            iv, key = self.aes_generate_pair()
            iv = base64.b64encode(iv)
            key = base64.b64encode(key)
            self.clients[client.peer]["aes_key"] = key
            self.clients[client.peer]["aes_iv"] = iv
            message_type = "client.aes.key"
            message_data = {"aes_key": key, "iv": iv, "cipher": "pgp"}
            message_context = {"sock_num": sock_num}
            logger.info("Sending AES session key to client")
            self.clients[client.peer]["status"] = "waiting AES"
            self.send_message(client, message_type, message_data, message_context, "pgp")
            return
        elif not isBinary:
            logger.error("Plaintext received, binary data always expected after pgp exchange, something is wrong!")
            self.unregister_client(client, reason=u"Plaintext received, binary data always expected after pgp exchange")
            return
        if client_data["status"] == "waiting AES":
            key = self.clients[client.peer]["aes_key"]
            iv = self.clients[client.peer]["aes_iv"]
            iv = base64.b64decode(iv)
            key = base64.b64decode(key)
            cipher = AES.new(key, AES.MODE_CFB, iv)
            message = cipher.decrypt(payload)[len(iv):]
            deserialized_message = Message.deserialize(message)
            if deserialized_message.data.get("status", "failed") == "success":
                logger.debug("Secure connection ready")
                client_data["status"] = "connected"
                context = {"user": client_data["names"][0], "source": ip + ":" + str(sock_num)}
                self.emitter.emit(
                    Message("user.connect", {"ip": ip, "sock": sock_num, "pub_key": client_data["pgp"], "nicknames": client_data["names"]},
                            context))
            else:
                logger.error("Secure connection failed")
                self.unregister_client(client, reason=u"Secure connection failed")
        elif client_data["status"] == "connected":
            # decypt AES
            key = self.clients[client.peer]["aes_key"]
            iv = self.clients[client.peer]["aes_iv"]
            iv = base64.b64decode(iv)
            key = base64.b64decode(key)
            cipher = AES.new(key, AES.MODE_CFB, iv)
            message = cipher.decrypt(payload)[len(iv):]
            deserialized_message = Message.deserialize(message)
            logger.debug(message)
            # parse message type
            self.process_message_type(client, deserialized_message)
        elif client_data["status"] == "receiving file":
            # decypt AES
            key = self.clients[client.peer]["aes_key"]
            iv = self.clients[client.peer]["aes_iv"]
            iv = base64.b64decode(iv)
            key = base64.b64decode(key)
            cipher = AES.new(key, AES.MODE_CFB, iv)
            message = cipher.decrypt(payload)[len(iv):]
            # close open file
            if message == "end_of_file":
                self.clients[client.peer]["status"] = "connected"
                logger.info("file received for " + client.peer)
                self.clients[client.peer]["file"].close()
                self.clients[client.peer].pop("extension")
                self.clients[client.peer].pop("file")
            # write file chunk
            else:
                logger.info("file chunk received for " + client.peer)
                self.clients[client.peer]["file"].write(message)
        else:
            # not supposed to happen
            logger.error("someone is doing something wrong, client status seems to be invalid: " + client_data["status"])
            self.unregister_client(client, reason=u"client status seems to be invalid: " + client_data["status"])

    def process_message_type(self, client, deserialized_message):
        logger.debug("Message type: " + deserialized_message.type)
        if (deserialized_message.type not in self.bus_message_list and self.message_blacklist) or \
                (deserialized_message.type in self.bus_message_list and not self.message_blacklist):
            data = deserialized_message.data
            logger.debug("Message data: " + str(deserialized_message.data))
            ctype, ip, sock_num = client.peer.split(":")
            # build context
            context = deserialized_message.context
            if context is None:
                context = {}
            if "source" not in context.keys():
                try:
                    context["source"] = self.clients[client.peer]["names"][0]
                except:
                    context["source"] = "unknown"
            if "mute" not in context.keys():
                context["mute"] = False
            context["source"] = str(context["source"]) + ":" + sock_num
            context["ip"] = ip
            logger.debug("Message context: " + str(context))
            # authorize user message_type
            # get user from sock
            user_data = self.user_manager.user_from_sock(sock_num)
            logger.debug("user data: " + str(user_data))
            # see if this user can perform this action
            if deserialized_message.type in user_data.get("forbidden_messages", []):
                logger.warning("This user is not allowed to perform this action " + str(sock_num))
                self.send_message(client, "speak", {"utterance": "Messages of type " + deserialized_message.type + " are not allowed for your account"}, context)
                return
            user = user_data.get("id", sock_num)
            logger.debug("user data: " + str(user_data))
            context["user"] = user
            try:
                context["user_name"] = user_data.get("nicknames", ["unknown "
                                                                "name"])[0]
            except:
                context["user_name"] = "unknown name"
            logger.debug(context)
            # check if message also sent files
            # TODO file formats
            if self.clients[client.peer].get("file_path"):
                fields = ["file", "file_path", "picture", "picture_path",
                          "pic_path", "feed", "feed_path", "dream_source",
                          "dream_seed", "path"]
                for field in fields:
                    if field in deserialized_message.data.keys():
                        deserialized_message.data[field] = self.clients[
                            client.peer]["file_path"]

            # pre-process message type
            if deserialized_message.type == "recognizer_loop:utterance":
                utterance = data["utterances"][0]
                # validate user utterance
                self.validate_user_utterance(utterance, user_data, context,
                                             client)
            elif deserialized_message.type == "incoming_file":
                logger.info("started receiving file for " + client.peer)
                self.clients[client.peer]["status"] = "receiving file"
                extension = deserialized_message.data.get("extension", ".jpg")
                path = "../" + client.peer + extension
                self.clients[client.peer]["extension"] = extension
                self.clients[client.peer]["file_path"] = path
                self.clients[client.peer]["file"] = open(path, 'wb')
            else:
                logger.info("no special handling provided for " + deserialized_message.type)
                # message is whitelisted and no special handling was provided
                self.emitter.emit(Message(deserialized_message.type, deserialized_message.data, context))
            # notify user action
            client_data = self.clients[client.peer]
            context = {"user": client_data["names"][0], "source": ip + ":" + str(sock_num)}
            try:
                self.emitter.emit(
                Message("user.request",
                        {"ip": ip, "sock": sock_num, "pub_key": client_data["pgp"], "nicknames": client_data["names"]},
                        context))
            except Exception as e:
                logger.error(e)
        else:
            logger.warning("message type not allowed: " +
                           deserialized_message.type)

    def validate_user_utterance(self, utterance, user_data, context, client):
        # check if skill/intent that will trigger is authorized for this user
        logger.info("Authorizing utterance for user")
        intent, skill = self.parser.determine_intent(utterance)
        if int(skill) == 0:
            # TODO intent failure, authorize fallback
            pass
        if intent in user_data.get("forbidden_intents", config.get(
                "forbidden_intents", [])):
            logger.warning("Intent " + intent + " is not allowed for " +
                           user_data.get("nicknames", [client.peer])[0])
            self.send_message(client, "speak", {
                "utterance": intent + " is not allowed for your account"},
                              context, cipher="aes")

            return

        if skill in user_data.get("forbidden_skills", config.get(
                "forbidden_skills", [])):
            logger.warning("Skill " + skill + " is not allowed for " + user_data.get("nicknames", [client.peer])[0])
            self.send_message(client, "speak", {
                "utterance": skill + " is not allowed for your account"},
                              context, cipher="aes")

            return
        logger.debug("emitting utterance to bus: " + str(utterance))
        self.emitter.emit(
            Message("recognizer_loop:utterance",
                    {'utterances': [utterance.strip()]}, context))

        logger.debug("Waiting answer for user " + context.get("source",
                                                              "source error!"))

    def Message_to_raw_data(self, Message):
        if hasattr(Message, 'serialize'):
            return Message.serialize()
        else:
            return json.dumps(Message.__dict__)

    def send_message(self, client, type="speak", data=None, context=None, cipher="none"):
        if data is None:
            data = {}
        logger.info("Sending message to " + str(client.peer))
        logger.info("cipher: " + cipher + " context: " + str(context) + " data: " + str(data))
        message = self.Message_to_raw_data(Message(type, data, context))
        if cipher == "pgp":
            logger.debug("target pgp fingerprint: " + self.clients[client.peer].get("fingerprint"))
            message = encrypt_string(self.clients[client.peer].get("fingerprint"), message)
            if not message.ok:
                logger.error("Encryption failed: " + message.stderr)
                # TODO throw error
            else:
                message = str(message)
                logger.debug(message)
        if cipher == "aes":
            # start encryptor
            iv = self.clients[client.peer]["aes_iv"]
            iv = base64.b64decode(iv)
            key = self.clients[client.peer]["aes_key"]
            key = base64.b64decode(key)
            cipher = AES.new(key, AES.MODE_CFB, iv)
            # generate new iv
            new_iv, key = self.aes_generate_pair()
            new_iv = base64.b64encode(new_iv)
            self.clients[client.peer]["aes_iv"] = new_iv
            context["aes_iv"] = new_iv
            # encrypt message
            message = self.Message_to_raw_data(Message(type, data, context))
            message = iv + cipher.encrypt(message)
            client.sendMessage(message, isBinary=True)
            return message
        client.sendMessage(message.encode("utf-8"))
        return message

    # mycroft handlers
    def handle_message_to_sock_request(self, event):
        # TODO allow files
        type = event.data.get("type", "bus")
        logger.info("Request to message client received: " + type)
        cipher = event.data.get("cipher", "aes")
        # merge contexts of message and message_request
        context = event.context
        if context is None:
            context = {}
        context.update(event.data.get("context", {}))
        # allow user to be requested explictly
        user_id = event.data.get("user_id")
        if user_id is None:
            user_id = context.get("sock_num")
            if user_id is None:
                # if not, use destinatary
                user_id = context.get("destinatary", "")
            else:
                user_id = event.data.get("requester", "server_skills") + ":" + user_id

        if ":" not in str(user_id):
            logger.error(
                "Message_Request: invalid user_id: " + user_id + " in data: " + str(event.data) + " in context: " + str(
                    context))
            return
        context["source"] = event.data.get("requester", "skills") + ":server"
        data = event.data.get("data", {})
        if cipher == "none" and "cipher" in data.keys():
            cipher = data["cipher"]
        sock_num = user_id.split(":")[1]
        logger.info("Message_Request: sock:" + sock_num + " with type: " + type)
        for client in self.clients:
            c, ip, sock = client.split(":")
            if sock == sock_num:
                self.message_queue.append([self.clients[client]["object"], type, data, context, cipher])
                return

    def handle_failure(self, event):
        # TODO warn user of possible lack of answer (wait for wolfram alpha x seconds first)
        logger.debug("intent failure detected")

    def handle_speak(self, event):
        target = event.context.get('destinatary', "all")
        if ":" not in target:
            return
        elif "fbchat" in target or "webbchat" in target:
            return
        utterance = event.data.get('utterance', "")
        logger.debug("Answer: " + utterance + " Target: " + target)
        target, sock_num = target.split(":")
        answer_type = "speak"
        for client in self.clients:
            c, ip, sock = client.split(":")
            if sock == sock_num:
                logger.debug("Adding answer to answering queue")
                self.message_queue.append(
                    [self.clients[client]["object"], answer_type, event.data, event.context, "aes"])
                return
        logger.error("Speak targeted to non existing client")

    def config_update(self, config=None, save=False, isSystem=False):
        if config is None:
            config = {}
        if save:
            ConfigurationManager.save(config, isSystem)
        self.emitter.emit(
            Message("configuration.patch", {"config": config}))

if __name__ == '__main__':
    # more logs
    log.startLogging(sys.stdout)

    # server
    host = config.get("host", "127.0.0.1")
    port = config.get("port", 5678)
    max_connections = config.get("max_connections", -1)
    adress = u"ws://" + host + u":" + str(port)
    cert = config.get("cert_file",
                      dirname(__file__) + '/certs/jarbas_server.crt')
    key = config.get("key_file", dirname(__file__) + '/certs/jarbas_server.key')

    factory = MyServerFactory(adress)
    factory.protocol = MyServerProtocol
    if max_connections >= 0:
        factory.setProtocolOptions(maxConnections=max_connections)

    if not exists(key) or not exists(cert):
        logger.error("ssl keys dont exist, creating self signed")
        dir = dirname(__file__) + "/certs"
        name = key.split("/")[-1].replace(".key", "")
        create_self_signed_cert(dir, name)
        cert = dir + "/" + name + ".crt"
        key = dir + "/" + name + ".key"
        logger.info("key created at: " + key)
        logger.info("crt created at: " + cert)
        # update config with new keys
        config["cert_file"] = cert
        config["key_file"] = key
        factory.config_update({"jarbas_server": config}, True)

    # SSL server context: load server key and certificate
    contextFactory = ssl.DefaultOpenSSLContextFactory(key, cert)

    reactor.listenSSL(port, factory, contextFactory)
    reactor.run()
