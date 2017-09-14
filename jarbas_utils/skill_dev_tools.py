from mycroft.messagebus.api import BusQuery, BusResponder
from mycroft.util.log import getLogger
import time
from mycroft.configuration import ConfigurationManager
from mycroft.messagebus.client.ws import WebsocketClient
from threading import Thread


class ResponderBackend(object):
    """
        Base class for all responder implementations. checks message source
        to see if it was a server/client request, and formats answer

        allows for example server to request webcam for face recognition

        Args:
            name: name of service (str)
            emitter: eventemitter or websocket object
            server: respond to queries from jarbas server
            client: respond to queries from clients (":client_id" in
            destinatary in message.context)

    """

    def __init__(self, name=None, emitter=None, logger=None,
                 server=True, client=True, override=True):
        """
           initialize emitter, register events, initialize internal variables
        """
        if name is None:
            self.name = "ResponderBackend"
        else:
            self.name = name
        if emitter is None:
            self.emitter = WebsocketClient()

            def connect():
                self.emitter.run_forever()
            ws_thread = Thread(target=connect)
            ws_thread.setDaemon(True)
            ws_thread.start()
        else:
            self.emitter = emitter
        self.response_type = "default.reply"
        self.responder = None
        self.server_responder = None
        self.client_responder = None
        self.callback = None
        if logger is None:
            self.logger = getLogger(self.name)
        else:
            self.logger = logger
        self.server = server
        self.client = client
        self.client_request_message = "client.message.request"
        self.server_request_message = "server.message.request"
        self.config = ConfigurationManager.get().get(self.name, {})
        if override:
            server = self.config.get("answer_server")
            if server is not None:
                self.server = server
            client = self.config.get("answer_client")
            if client is not None:
                self.client = client

    def update_response_data(self, response_data=None, response_context=None):
        if self.responder is not None:
            self.responder.update_response(response_data, response_context)
        if self.server_responder is not None:
            self.server_responder.update_response(response_data,
                                                  response_context)
        if self.client_responder is not None:
            self.client_responder.update_response(response_data,
                                                  response_context)

    def set_response_handler(self, trigger_message, callback, response_data=None,
                             response_context=None, cipher="aes"):
        """
          prepare query for sending, args:
                message_type/data/context of query to send
                waiting_messages (list) : list of extra messages to end wait
                cipher (str) : cipher to use in encryption for server/client
        """

        # update message context
        if response_context is None:
            response_context = {}
        response_context["source"] = self.name
        response_context["triggered_by"] = trigger_message

        # generate reply message
        if ".request" in trigger_message:
            self.response_type = trigger_message.replace(".request", ".reply")
        else:
            self.response_type = trigger_message + ".reply"

        self.responder = BusResponder(self.emitter, self.response_type,
                                      response_data, response_context,
                                      [])
        self._get_server_responder(response_data,
                                   response_context,
                                   cipher)
        self._get_client_responder(response_data,
                                   response_context,
                                   cipher)

        self.callback = callback
        self.emitter.on(trigger_message, self._respond)

    def _respond(self, message):
        try:
            if self.callback:
                self.callback(message)
        except Exception as e:
            self.logger.error(e)
        source = message.context.get("source", "unknown")
        destinatary = message.context.get("destinatary", "all")
        # if the message came from server send it a response
        if "server" in source and self.server:
            self.server_responder.respond(message)
            return
        # if this message came from a client sent it a response
        # filter chat (fbchat or webchat)
        if ":" in destinatary and "chat" not in destinatary and self.client:
            if destinatary.split(":")[1].isdigit():
                self.client_responder.respond(message)  # probably a socket
                return
        # respond internally
        self.responder.respond(message)

    def _get_client_responder(self, message_data, message_context,
                              cipher="aes"):
        if message_data is None:
            message_data = {}
        file_fields = ["file", "path", "dream_source", "file_path",
                       "pic_path", "picture_path", "PicturePath"]
        type = "bus"
        for field in file_fields:
            if field in message_data.keys():
                type = "file"
                message_data["file"] = message_data[field]
                break

        data = {"requester": self.name,
                "message_type": self.response_type,
                "message_data": message_data, "cipher": cipher,
                "request_type": type}

        self.client_responder = BusResponder(self.emitter,
                                             self.client_request_message,
                                             data,
                                             message_context, [])

    def _get_server_responder(self, message_data,
                              message_context, cipher="aes"):
        if message_data is None:
            message_data = {}
        file_fields = ["file", "path", "dream_source", "file_path",
                       "pic_path", "picture_path", "PicturePath"]
        type = "bus"
        for field in file_fields:
            if field in message_data.keys():
                type = "file"
                message_data["file"] = message_data[field]
                break

        data = {"requester": self.name,
                "message_type": self.response_type,
                "message_data": message_data, "cipher": cipher,
                "request_type": type}

        self.server_responder = BusResponder(self.emitter,
                                             self.server_request_message,
                                             data,
                                             message_context, [])


class QueryBackend(object):
    """
        Base class for all query implementations. waits timeout seconds for
        answer, considered answers are generated as follows

            query:
                deep.dream.request
                deep.dream
            possible responses:
                deep.dream.reply,
                deep.dream.result,
                deep.dream.response

            query:
                face.recognition.request
                face.recognition
            possible responses:
                deep.dream.reply,
                deep.dream.result,
                deep.dream.response

        Args:
            name: name of service (str)
            emitter: eventemitter or websocket object
            timeout: time in seconds to wait for response (int)
            server: send this query to jarbas server
            client: send this query to jarbas client
            override: get client and server params from config file (at name)
    """

    def __init__(self, name=None, emitter=None, timeout=5, logger=None,
                 server=False, client=False, override=True):
        """
           initialize emitter, register events, initialize internal variables
        """
        if name is None:
            self.name = "QueryBackend"
        else:
            self.name = name
        if emitter is None:
            self.emitter = WebsocketClient()

            def connect():
                self.emitter.run_forever()

            ws_thread = Thread(target=connect)
            ws_thread.setDaemon(True)
            ws_thread.start()
        else:
            self.emitter = emitter
        self.timeout = timeout
        self.query = None
        if logger is None:
            self.logger = getLogger(self.name)
        else:
            self.logger = logger
        self.server = server
        self.client = client
        self.client_request_message = "client.message.request"
        self.server_request_message = "server.message.request"
        self.waiting_messages = []
        self.elapsed_time = 0
        self.config = ConfigurationManager.get().get(self.name, {})
        if override:
            server = self.config.get("ask_server")
            if server is not None:
                self.server = server
            client = self.config.get("ask_client")
            if client is not None:
                self.client = client
        self.result = {}

    def send_request(self, message_type, message_data=None,
                     message_context=None, response_messages=None,
                     cipher="aes"):
        """
          prepare query for sending, args:
                message_type/data/context of query to send
                response_messages (list) : list of extra messages to end wait
                cipher (str) : cipher to use in encryption for server/client
        """
        if response_messages is None:
            response_messages = []
        # generate reply messages
        self.waiting_messages = response_messages
        if ".request" in message_type:
            response = message_type.replace(".request", ".reply")
            if response not in self.waiting_messages:
                self.waiting_messages.append(response)
            response = message_type.replace(".request", ".response")
            if response not in self.waiting_messages:
                self.waiting_messages.append(response)
            response = message_type.replace(".request", ".result")
            if response not in self.waiting_messages:
                self.waiting_messages.append(response)
        else:
            response = message_type + ".reply"
            if response not in self.waiting_messages:
                self.waiting_messages.append(response)
            response = message_type + ".response"
            if response not in self.waiting_messages:
                self.waiting_messages.append(response)
            response = message_type + ".result"
            if response not in self.waiting_messages:
                self.waiting_messages.append(response)

        # update message context
        if message_context is None:
            message_context = {}
        message_context["source"] = self.name
        message_context["waiting_for"] = self.waiting_messages
        start = time.time()
        self.elapsed_time = 0
        if not self.server:
            if not self.client:
                result = self._send_internal_request(message_type, message_data,
                                                   message_context)
            else:
                result = self._send_client_request(message_type, message_data,
                                                 message_context, cipher)
        else:
            result = self._send_server_request(message_type, message_data,
                                             message_context, cipher)
        self.elapsed_time = time.time() - start
        return result

    def _send_server_request(self, message_type, message_data,
                             message_context, cipher="aes"):
        if message_data is None:
            message_data = {}
        file_fields = ["file", "path", "dream_source", "file_path",
                       "pic_path", "picture_path", "PicturePath"]
        type = "bus"
        for field in file_fields:
            if field in message_data.keys():
                type = "file"
                message_data["file"] = message_data[field]
                break

        data = {"requester": self.name,
                "message_type": message_type,
                "message_data": message_data, "cipher": cipher,
                "request_type": type}

        self.query = BusQuery(self.emitter, self.server_request_message, data,
                              message_context)
        for message in self.waiting_messages[1:]:
            self.query.add_response_type(message)
        return self.query.send(self.waiting_messages[0], self.timeout)

    def _send_client_request(self, message_type, message_data,
                             message_context, cipher="aes"):
        if message_data is None:
            message_data = {}
        file_fields = ["file", "path", "dream_source", "file_path",
                       "pic_path", "picture_path", "PicturePath"]
        type = "bus"
        for field in file_fields:
            if field in message_data.keys():
                type = "file"
                message_data["file"] = message_data[field]
                break

        data = {"requester": self.name,
                "message_type": message_type,
                "message_data": message_data, "cipher": cipher,
                "request_type": type}

        self.query = BusQuery(self.emitter, self.client_request_message,
                              data,
                              message_context)
        for message in self.waiting_messages[1:]:
            self.query.add_response_type(message)
        return self.query.send(self.waiting_messages[0], self.timeout)

    def _send_internal_request(self, message_type, message_data,
                               message_context):
        self.query = BusQuery(self.emitter, message_type, message_data,
                              message_context)
        for message in self.waiting_messages[1:]:
            self.query.add_response_type(message)
        return self.query.send(self.waiting_messages[0], self.timeout)

    def get_result(self, context=False, type=False):
        """
            return last processed result, data, context or type
        """
        if self.query is None:
            return None
        if type:
            return self.query.get_response_type()
        if context:
            return self.query.get_response_context()
        return self.query.get_response_data()
