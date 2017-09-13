from twisted.python import log
from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS
from twisted.internet.protocol import ReconnectingClientFactory

# sys and crypto
import sys, json, time
from threading import Thread
from os.path import dirname
from Crypto.Cipher import AES
from Crypto import Random
import logging
import base64

# mycroft
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger
from mycroft.client.client.pgp import get_own_keys, encrypt_string, decrypt_string, generate_client_key, export_key, import_key_from_ascii
from mycroft.configuration import ConfigurationManager

config = ConfigurationManager.get()
config = config.get("jarbas_client", {})

# ask server if no intent start or failure detected in 20 seconds
assume_failure = False

# logs
NAME = "Jarbas_Client"
logger = getLogger(NAME)

gpglog = logging.getLogger("gnupg")
gpglog.setLevel("WARNING")


class MyClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        logger.info("Server connected: {0}".format(response.peer))
        self.factory.emitter.emit(Message("server.connected"))

    def onOpen(self):
        logger.info("WebSocket connection open. Waiting server pgp key")
        self.factory.emitter.emit(Message("server.websocket.open"))

    def onMessage(self, payload, isBinary):
        logger.info("status: " + self.factory.status)
        self.factory.emitter.emit(Message("server.message.received"))
        if isBinary:
            # all encrypted data is Binary AES
            logger.info("Binary message received: {0} bytes".format(len(payload)))
            if self.factory.status != "connected":
                logger.warning("Something is wrong, receiving unexpected binary data")
                sys.exit()
            else:
                # decrypt aes message
                iv = self.factory.aes_iv
                key = self.factory.aes_key
                cipher = AES.new(key, AES.MODE_CFB, iv)
                message = cipher.decrypt(payload)[len(iv):]
                deserialized_message = Message.deserialize(message)
                logger.debug(message)
                # update iv for next message
                self.factory.aes_iv = deserialized_message.context.get("aes_iv", self.factory.aes_iv)
                self.factory.aes_iv = base64.b64decode(self.factory.aes_iv)
                # restore destinatary context
                try:
                    target, sock = deserialized_message.context.get(
                        "destinatary").split(
                        ":")
                except:
                    target = "all"
                deserialized_message.context["destinatary"] = target
                # validate server message and emit to internal bus
                if (self.factory.message_policy and deserialized_message.type not in self.factory.message_list) or (not self.factory.message_policy and deserialized_message.type in self.factory.message_list):

                    self.factory.emitter.emit(deserialized_message)
                else:
                    logger.warning("server message not allowed " + deserialized_message.type)
        else:
            data = payload
            if self.factory.status == "waiting server pgp":
                message = Message.deserialize(data)
                data = message.data
                self.factory.server_key = data.get("public_key")
                self.factory.my_id = data.get("sock_num")
                logger.debug("Received server key: \n" + self.factory.server_key)
                import_result = import_key_from_ascii(self.factory.server_key)
                self.factory.server_fp = import_result.results[0]["fingerprint"]
                msg = self.Message_to_raw_data(Message("client.pgp.public.response", {"public_key": self.factory.ascii_public, "names": self.factory.names}))
                msg = str(encrypt_string(self.factory.server_fp, msg))
                logger.debug("Sending pgp key to server: \n" + msg)
                self.sendMessage(msg.encode('utf8'))
                self.factory.status = "waiting server aes"
            elif self.factory.status == "waiting server aes":
                logger.debug("Received PGP encrypted AES key Exchange\n" + str(data))
                ciphertext = str(data)
                decrypted = decrypt_string(ciphertext, self.factory.passwd)
                if decrypted.ok:
                    message = decrypted.data
                    logger.debug("message successfully decrypted")
                    logger.debug(message)
                else:
                    logger.error("Could not decrypt message: " + str(decrypted.stderr))
                    sys.exit()
                message = Message.deserialize(message)
                data = message.data
                self.factory.aes_iv = data["iv"]
                self.factory.aes_key = data["aes_key"]
                self.factory.aes_iv = base64.b64decode(self.factory.aes_iv)
                self.factory.aes_key = base64.b64decode(self.factory.aes_key)
                msg = self.Message_to_raw_data(Message("client.aes.exchange.complete", {"status": "success"}))
                logger.debug("Sending AES encrypted acknowledgement")
                cipher = AES.new(self.factory.aes_key, AES.MODE_CFB, self.factory.aes_iv)
                msg = self.factory.aes_iv + cipher.encrypt(msg)
                self.sendMessage(msg, isBinary=True)
                self.factory.status = "connected"
                logger.debug("Key exchange complete, you are communicating securely")
                self.factory.client = self
            elif self.factory.status == "connected":
                logger.error("AES encrypted binary data expected but text received!")
                logger.debug(data)
                # TODO handle bad server
                sys.exit()
            else:
                logger.error("bad internal status: " + self.factory.status)
                # not supposed to happen
                # TODO handle bad server
                sys.exit()

    def onClose(self, wasClean, code, reason):
        logger.info("WebSocket connection closed: {0}".format(reason))
        self.factory.emitter.emit(Message("server.connection.closed"))

    def Message_to_raw_data(self, message):
        if hasattr(message, 'serialize'):
            return message.serialize()
        else:
            return json.dumps(message.__dict__)


class MyClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = MyClientProtocol

    def __init__(self, *args, **kwargs):
        super(MyClientFactory, self).__init__(*args, **kwargs)
        # mycroft_ws
        self.emitter = None
        self.emitter_thread = None
        self.create_internal_emitter()
        self.client = None
        # current session keys
        self.server_key = None
        self.server_fp = None
        self.aes_key = None
        self.aes_iv = None
        self.my_id = None
        self.names = config.get("client_names", ["jarbas_client"])

        # client pgp
        self.ascii_public = None
        self.public = []
        self.private = []
        self.key_id = None
        self.user = config.get("pgp_user", 'Jarbas@Jarbas.ai')
        self.passwd = config.get("pgp_passwd",
                                 'welcome to the mycroft collective')
        self.load_client_keys()

        # runtime flags
        self.ask = False
        self.waiting = False
        self.detected = False

        self.status = "waiting server pgp"
        self.message_policy = config.get("message_policy", "blacklist") ==  "blacklist"
        self.message_list = config.get("message_list", [])

    # initialize methods
    def load_client_keys(self):
        encrypted = encrypt_string(self.user, "Jarbas client key loaded")
        if not encrypted.ok:
            key = generate_client_key(self.user, self.passwd)
            encrypted = encrypt_string(self.user, "Newly generated Jarbas client key loaded")

        decrypted = decrypt_string(encrypted, self.passwd)
        if not decrypted.ok:
            logger.error("Could not create own gpg key, do you have gpg installed?")
        else:
            logger.info(decrypted)
            self.public, self.private = get_own_keys(self.user)
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
        self.emitter.on('recognizer_loop:utterance', self.handle_utterance)
        self.emitter.on('server.intent_failure', self.handle_intent_failure)
        self.emitter.on("server.message.request", self.handle_server_request)
        self.emitter.on('message', self.end_wait)
        self.emitter.on('intent.execution.start', self.end_wait)

    # websocket handlers
    def clientConnectionFailed(self, connector, reason):
        logger.info("Client connection failed: " + str(reason) + " .. retrying ..")
        self.status = "waiting server pgp"
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        logger.info("Client connection lost: " + str(reason) + " .. retrying ..")
        self.status = "waiting server pgp"
        self.retry(connector)

    # mycroft handlers
    def handle_server_request(self, message):
        # send server a message
        stype = message.data.get("request_type", "bus")
        requester = message.data.get("requester")
        message_type = message.data.get("message_type")
        message_data = message.data.get("message_data")
        message_context = message.context
        logger.info("Received request to message server from " + requester + " with type: " + str(
            message_type) + " with data: " + str(message_data))
        # TODO more types, type handling
        if stype == "file":
            logger.info("File requested, sending first")
            bin_file = open(message_data["file"], "rb")
            # message_data["file"] = bin_file.read()
            self.sendMessage("incoming_file", {"target": "server"})
            i = 0
            while True:
                i += 1
                chunk = bin_file.read(4096)
                logger.info("sending chunk " + str(i))
                if not chunk:
                    logger.info("Sending end_of_file")
                    self.sendRaw("end_of_file")
                    bin_file.close()
                    break  # EOF
                self.sendRaw(chunk)
        message_data["source"] = requester
        logger.info("sending message with type: " + message_type)
        self.sendMessage(message_type, message_data, message_context)

    def handle_speak(self, event):
        utterance = event.data.get('utterance')
        mute = event.data.get('mute', False)
        target = event.context.get('destinatary', "none")
        if ":" in target:
            target = target.split(":")[1]  # 0/1 id or name doesnt matter

        # if the target was aimed at client itself, log
        if (str(target) == self.my_id or str(target) in self.names) and not mute:
            logger.info("Speak: " + utterance)

    def handle_utterance(self, event):
        source = event.data.get("source", self.names[0])
        if source is None:
            source = "unknown"
        if event.context is None:
            event.context = {}
        event.context["target"] = source
        logger.debug("Processing utterance: " + event.data.get("utterances")[0] + " from source: " + source)
        self.wait_answer()
        # ask server
        if not self.detected:
            logger.debug("No intent failure or execution detected for 20 seconds")
            if assume_failure:
                self.ask = True
        if self.ask:
            logger.debug("Asking server for answer")
            if self.client is None or self.status != "connected":
                logger.error("Key exchange was not completed")

            else:
                self.sendMessage(event.type, event.data, event.context)
        else:
            logger.debug("Not asking server")

    def validate_server_message(self, deserialized_message):
        pass

    def sendRaw(self, data):
        if self.client is None:
            logger.error("Client is none")
            sys.exit()
        logger.debug("AES encrypting")
        cipher = AES.new(self.aes_key, AES.MODE_CFB, self.aes_iv)
        msg = self.aes_iv + cipher.encrypt(data)
        self.client.sendMessage(msg, isBinary=True)

    def sendMessage(self, type, data, context=None):
        if self.client is None:
            logger.error("Client is none")
            return

        if context is None:
            context = {}

        msg = self.client.Message_to_raw_data(Message(type, data, context))
        logger.debug("AES encrypting")
        cipher = AES.new(self.aes_key, AES.MODE_CFB, self.aes_iv)
        msg = self.aes_iv + cipher.encrypt(msg)
        self.client.sendMessage(msg, isBinary=True)
        self.emitter.emit(Message("server.message.sent"))

    def handle_intent_failure(self, event):
        if self.waiting:
            logger.debug("Intent failure detected, ending wait")
            self.ask = True
            self.waiting = False
            self.detected = True

    def wait_answer(self):
        start = time.time()
        elapsed = 0
        logger.debug("Waiting for intent handling before asking server")
        self.waiting = True
        self.ask = False
        self.detected = False
        # wait maximum 20 seconds
        while self.waiting and elapsed < 20:
            elapsed = time.time() - start
            time.sleep(0.1)
        self.waiting = False

    def end_wait(self, message):
        try:
            _message = json.loads(message)
            if self.waiting:
                if "intent" in _message.get("type").lower() and "failure" not in _message.get("type"):
                    logger.debug("intent handled internally")
                    self.ask = False
                    self.waiting = False
                    self.detected = True
        except:
            pass


if __name__ == '__main__':

    log.startLogging(sys.stdout)
    host = config.get("host", "174.59.239.227")
    port = config.get("port", 5678)
    adress = u"ws://" + host + u":" + str(port)
    factory = MyClientFactory(adress)
    factory.protocol = MyClientProtocol
    contextFactory = ssl.ClientContextFactory()
    reactor.connectSSL(host, port, factory, contextFactory)
    reactor.run()