#!/usr/bin/env python
# -*- coding:utf-8 -*-
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

from mycroft.configuration import ConfigurationManager

__author__ = 'jarbas', 'jcasoft'


from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from threading import Thread
from mycroft.client.webchat.self_signed import create_self_signed_cert
from os.path import exists, dirname, isfile

ws = None
max_con = -1
all_speech = False
mute_speech = True

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import tornado.options
import os.path
from tornado.options import define, options
import multiprocessing
import json
import os, sys
from subprocess import check_output


ip = check_output(['hostname', '--all-ip-addresses']).replace(" \n", "")
port = 4000
mode = "client"

clients = []
chat_id = 0

input_queue = multiprocessing.Queue()
output_queue = multiprocessing.Queue()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html', ip=ip, port=port)


class StaticFileHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('js/app.js')


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        global chat_id, clients, max_con, mute_speech
        if len(clients) > max_con and max_con > 0:
            self.write_message("Welcome to Jarbas, maximum simultaneous connections limit was reached")
            sys.exit()
        chat_id += 1
        self.id = chat_id
        self.message_context = {"source": "webchat_:" + str(self.id),
                                "user": "webchat " + str(self.id),
                                "mute": mute_speech}
        clients.append(self)
        self.write_message("Welcome to Jarbas")
        ws.on("speak", self.handle_speak)
        ws.on("message", self.handle_log)

    def on_message(self, message):
        if mode == "log":
            self.write_message("running as LOG, discarding data")
            return
        utterance = json.dumps(message)
        print("*****Utterance : ", utterance, "*****User_id: ", self.id)
        message_type = "recognizer_loop:utterance"
        message_data = {"utterances": [utterance]}
        ws.emit(Message(message_type, message_data, self.message_context))

    def handle_speak(self, event):
        target = event.context.get('destinatary', "all")
        if not all_speech:
            if ":" not in target:
                return
            elif "webchat" not in target:
                return
        utterance = event.data.get('utterance', "")
        self.write_message(utterance)

    def handle_log(self, message):
        if mode == "log":
            self.write_message(message)

    def on_close(self):
        clients.remove(self)


def connect():
    ws.run_forever()


def config_update(config=None, save=False, isSystem=False):
    global ws
    if config is None:
        config = {}
    elif save:
        ConfigurationManager.save(config, isSystem)
    ws.emit(
        Message("configuration.patch", {"config": config}))


def main():
    global ws, port, max_con, all_speech, mute_speech, mode
    ws = WebsocketClient()
    event_thread = Thread(target=connect)
    event_thread.setDaemon(True)
    event_thread.start()
    tornado.options.parse_command_line()
    config = ConfigurationManager.get().get("webchat", {})
    port = config.get("port", 4000)
    use_ssl = config.get("ssl", True)
    max_con = config.get("max_connections", -1)
    all_speech = config.get("all_speech", True)
    mute_speech = config.get("mute_speech", True)
    mode = config.get("mode", "client")
    url = "http://" + str(ip) + ":" + str(port)
    if use_ssl:
        url = "https://" + str(ip) + ":" + str(port)
        cert = config.get("cert_file",
                          dirname(__file__) + '/certs/webchat.crt')
        key = config.get("key_file", dirname(__file__) + '/certs/webchat.key')

        if not exists(key) or not exists(cert):
            print "ssl keys dont exist, creating self signed"
            dir = dirname(__file__) + "/certs"
            name = key.split("/")[-1].replace(".key", "")
            create_self_signed_cert(dir, name)
            cert = dir + "/" + name + ".crt"
            key = dir + "/" + name + ".key"
            print "key created at: " + key
            print "crt created at: " + cert
            # update config with new keys
            config["cert_file"] = cert
            config["key_file"] = key
            config["ssl"] = use_ssl
            config["port"] = port
            config["max_connections"] = max_con
            config_update({"webchat": config}, True)


    print "*********************************************************"
    print "*   Access from web browser " + url
    print "*********************************************************"

    routes = [
        tornado.web.url(r"/", MainHandler, name="main"),
        tornado.web.url(r"/static/(.*)", tornado.web.StaticFileHandler,
                        {'path': './'}),
        tornado.web.url(r"/ws", WebSocketHandler)
    ]

    settings = {
        "debug": True,
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
    }

    application = tornado.web.Application(routes, **settings)
    if use_ssl:
        httpServer = tornado.httpserver.HTTPServer(application,
                                                       ssl_options={
            "certfile": cert,
            "keyfile": key,
        })
    else:
        httpServer = tornado.httpserver.HTTPServer(application)
    tornado.options.parse_command_line()
    httpServer.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
