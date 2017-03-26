import gtk
import sys
from os.path import dirname
import random
from threading import Thread
from time import sleep

from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from mycroft.util import create_signal

ws = None


def chunk_str(str, chunk_size):
    return [str[i:i + chunk_size] for i in range(0, len(str), chunk_size)]

class JarbasGUI(gtk.Window):

    def __init__(self):
        super(JarbasGUI, self).__init__()

        # mycroft data
        self.suggest_list = []
        self.current_suggest = []
        self.objectives_list = []
        self.entry = ""
        self.speech = ""
        self.greetings = ["Waiting for query","Ready to serve", "Hello", "Hello Human", "Connected", "State your purpose"]

        self.waiting = False
        self.connected = False
        ### gui

        # quit button
        self.connect("destroy", gtk.main_quit)
        # size
        self.set_size_request(450, 650)
        # set title
        self.set_title("Jarbas-AI")
        # set icon
        try:
            self.set_icon_from_file(dirname(__file__) + "/pictures/icon.png")
        except Exception, e:
            print e.message
            sys.exit(1)
        # main widget
        self.gui = self.make_gui()
        # add gui widget box to window
        self.add(self.gui)
        # show
        self.show_all()

        # ws client
        global ws
        ws = WebsocketClient()

        def connect():
            ws.run_forever()

        ws.on("speak", self.handle_speech)
        ws.on("Register_Objective", self.handle_register_objective)
        ws.on("objective_listing", self.handle_objective_update)
        event_thread = Thread(target=connect)
        event_thread.setDaemon(True)
        event_thread.start()



    ### message bus functions ###
    def handle_register_objective(self, message):
        name = message.data["name"]
        if name not in self.objectives_list:
            self.objectives_list.append(name)
            print "added objective: " + name

    def handle_objective_update(self, message):
        self.objectives_list = message.data["objectives"]
        self.waiting = False

    def handle_speech(self, message):
        self.speech = message.data.get('utterance')
        print "Jarbas said: " + self.speech
        self.waiting = False

    def request_objective_list(self):
        ws.emit(Message("objectives_request", {}))
        self.waiting = True
        self.update()

    def send_utterance(self, utterance):
        ws.emit(
            Message("recognizer_loop:utterance",
                    {'utterances': [utterance], 'source': "gui"}))

    def execute_intent(self, intent_name, params_dict=None):
        if params_dict is None:
            params_dict = {}
        ws.emit(Message(intent_name, params_dict))

    def execute_objective(self, name):
        ws.emit(Message("Execute_Objective", {"Objective": name}))

    def speak(self, utterance):
        ws.emit(Message("speak", {"utterance": utterance}))


    #### GUI #####
    def make_gui(self):

        mb = self.get_menubar_widget()

        # add menu bar to widget box
        vbox = gtk.VBox(False, 2)
        vbox.pack_start(mb, False, False, 0)

        # Connected
        #if self.connected:
        #    label = gtk.Label("Connected")
        #else:
        #    label = gtk.Label("Click Connect")
        #vbox.pack_start(label, False, False, 2)

        # CC label
        label = gtk.Label("Control Centre")
        vbox.pack_start(label, False, False, 3)
        cc = self.get_CC_widget()
        # add CC to widget box
        vbox.pack_start(cc, False, False, 3)

        # objectives label
        label = gtk.Label("Objectives")
        vbox.pack_start(label, False, False, 3)

        # get objectives widget
        obj_widget = self.get_objectives_widget()
        # add
        vbox.pack_start(obj_widget, False, False, 3)

        # suggestions label
        label = gtk.Label("Suggestions")
        vbox.pack_start(label, False, False, 3)

        # make suggestions widget
        suggestion_widget = self.get_suggestions_widget()
        # add
        vbox.pack_start(suggestion_widget, False, False, 3)

        # texst entry
        label = gtk.Label("Input")
        #vbox.pack_start(label, False, False, 3)
        entry = self.get_input_widget()
        vbox.pack_start(entry, False, False, 3)

        # face
        image = gtk.Image()
        image.set_from_file(dirname(__file__) + "/pictures/icon.jpg")
        vbox.pack_start(image, False, False, 3)

        output = self.get_output_widget()
        vbox.pack_start(output, False, False, 3)


        return vbox

    def get_output_widget(self):
        vbox = gtk.VBox(False, 2)
        label = gtk.Label("Last Speech: ")
        vbox.pack_start(label, False, False, 3)
        # split on every . ! ? ; which indicate speech pauses, remove ( ) etc.
        self.speech = self.speech.replace("etc.", "").replace("("," ").replace(")", " ")
        for s in chunk_str(self.speech, 70):
            label = gtk.Label(s)
            vbox.pack_start(label, False, False, 3)
        return vbox

    def get_input_widget(self):
        hbox = gtk.HBox(False, 2)
        #
        label = gtk.Label("Input   ")
        hbox.pack_start(label, True, False, 0)
        # receives written orders
        entry = gtk.Entry()
        entry.add_events(gtk.gdk.KEY_RELEASE_MASK)
        entry.connect("key-release-event", self.on_key_release)
        hbox.pack_start(entry, True, False, 0)
        # ok buytton
        name = "OK"
        obj = gtk.Button(name)
        # register execute objective function
        obj.connect("clicked", self.on_say, name)
        if not self.connected:
            obj.set_sensitive(False)
        # add button to container
        hbox.pack_start(obj, True, False, 0)
        return hbox

    def get_context_widget(self):
        # mood
        # last said
        # last heard
        # last action
        pass

    def get_results_widget(self):
        # monitor results messages and show last 3
        pass

    def get_log_widget(self):
        # logs from skills.main.py
        pass

    def get_face_widget(self):
        # face reacting to visemes
        # drawing area widget
        pass

    def get_CC_widget(self):
        # make CC container
        cc = gtk.HBox(True, 3)

        name = "Connect"
        obj = gtk.Button(name)
        # register execute objective function
        obj.connect("clicked", self.on_connect, name)
        # add button to container
        cc.add(obj)

        name = "Mute"
        obj = gtk.Button(name)
        # register execute objective function
        obj.connect("clicked", self.on_mute, name)
        if not self.connected:
            obj.set_sensitive(False)
        # add button to container
        cc.add(obj)

        name = "Un-mute"
        obj = gtk.Button(name)
        # register execute objective function
        obj.connect("clicked", self.on_unmute, name)
        if not self.connected:
            obj.set_sensitive(False)
        # add button to container
        cc.add(obj)

        name = "Listen"
        obj = gtk.Button(name)
        # register execute objective function
        obj.connect("clicked", self.on_listen, name)
        if not self.connected:
            obj.set_sensitive(False)
        # add button to container
        cc.add(obj)

        # make refresh
        name = "Refresh "
        obj = gtk.Button(name)
        obj.connect("clicked", self.on_refresh, name)
        if not self.connected:
            obj.set_sensitive(False)
        # add button to container
        cc.add(obj)

        return cc

    def get_objectives_widget(self):

        objectives = []

        for name in self.objectives_list:
            obj = gtk.Button(name)
            # register execute objective function
            obj.connect("clicked", self.on_execute_objective, name)
            # add button to container
            objectives.append(obj)

        obj_box = gtk.HBox(True, 3)
        row = 0
        columns = []
        temp_box = gtk.VBox(True, 3)
        for obj in objectives:
            temp_box.add(obj)
            row+=1
            if row >= 4:
                row = 0
                columns.append(temp_box)
                temp_box = gtk.VBox(True, 3)

        if len(self.objectives_list) == 0:
            obj = gtk.Button("No registered objectives")
            obj.set_sensitive(False)
            temp_box.add(obj)
        else:
            while row > 0 and row < 4:
                row += 1
                obj = gtk.Button(" code more ! ")
                obj.set_sensitive(False)
                temp_box.add(obj)
        columns.append(temp_box)

        for column in columns:
            obj_box.add(column)

        # add objective container to widget box
        halign = gtk.Alignment(0, 0, 1, 0)
        halign.add(obj_box)

        return halign

    def get_suggestions_widget(self):
        # read from disk
        f = open(dirname(__file__) + "/suggestions.txt", 'r')
        self.suggest_list = f.readlines()
        f.close()

        self.current_suggest = []

        # make suggestions container
        suggestions = gtk.VBox(True, 3)

        # choose random suggestions
        for i in range(1, 3):
            name = random.choice(self.suggest_list)
            self.current_suggest.append(name)

        # make suggestion buttons
        for name in self.current_suggest:
            suj = gtk.Button(name)
            # register execute suggestion function
            suj.connect("clicked", self.on_execute_suggestion, name)
            if not self.connected:
                suj.set_sensitive(False)
            # add button to container
            suggestions.add(suj)

        # add suggestions container to widget box
        halign = gtk.Alignment(0, 1, 1, 1)
        halign.add(suggestions)

        return halign

    def get_menubar_widget(self):
        # menu bar
        mb = gtk.MenuBar()

        # file menu
        filemenu = gtk.Menu()
        filem = gtk.MenuItem("File")
        filem.set_submenu(filemenu)

        exit = gtk.MenuItem("Exit")
        exit.connect("activate", gtk.main_quit)
        filemenu.append(exit)

        mb.append(filem)

        # help menu
        helpmenu = gtk.Menu()
        helpm = gtk.MenuItem("Help")
        helpm.set_submenu(helpmenu)

        help = gtk.MenuItem("About")
        help.connect("activate", self.on_about)
        helpmenu.append(help)

        mb.append(helpm)

        return mb

    def update(self):
        if self.connected:
            self.wait_for_bus()
            new_gui = self.make_gui()
            self.replace_widget(self.gui, new_gui)
            self.gui = new_gui
            self.show_all()

    def replace_widget(self, current, new):
        """
        Replace one widget with another.
        'current' has to be inside a container (e.g. gtk.VBox).
        """
        container = current.parent
        assert container  # is "current" inside a container widget?

        # stolen from gazpacho code (widgets/base/base.py):
        props = {}
        for pspec in gtk.container_class_list_child_properties(container):
            props[pspec.name] = container.child_get_property(current, pspec.name)

        gtk.Container.remove(container, current)
        container.add(new)

        for name, value in props.items():
            container.child_set_property(new, name, value)

    def wait_for_bus(self):
        while self.waiting:
            sleep(1)

    #### gui events ###
    def on_mute(self, widget, dummy):
        self.execute_intent("SpeakDisableIntent")

    def on_unmute(self, widget, dummy):
        self.execute_intent("SpeakEnableIntent")

    def on_listen(self, widget, dummy):
        create_signal("buttonPress")

    def on_refresh(self, widget, dummy):
        self.update()
        print "If you don't have objectives skill installed this will hang! \nWARNING: possible infinite loop"
        self.request_objective_list()

    def on_execute_objective(self, widget, name):
        print "objective: " + str(name)
        self.execute_objective(name)
        self.waiting = True
        self.update()

    def on_execute_suggestion(self, widget, name):
        print "suggestion: " + str(name)
        self.send_utterance(name)
        self.waiting = True
        self.update()

    def on_key_release(self, widget, dummy):
        self.entry = widget.get_text()

    def on_say(self, widget, dummy):
        print "text entry: " + self.entry
        if self.entry != "":
            self.send_utterance(self.entry)
            self.entry = ""
        self.waiting = True
        self.update()
        self.connected = True

    def on_about(self, widget):
        about = gtk.AboutDialog()
        about.set_program_name("Jarbas-AI")
        about.set_version("0.1")
        about.set_copyright("(c) Jarbas")
        about.set_comments("Jarbas AI - fork of mycroft-core")
        about.set_website("https://github.com/jarbasAI/jarbas-core")
        about.set_logo(gtk.gdk.pixbuf_new_from_file(dirname(__file__) +"/pictures/icon.png"))
        about.run()
        about.destroy()

    def on_connect(self, widget, dummy):

        self.speak(" connecting ")
        sleep(0.2)
        self.speak(random.choice(self.greetings))
        self.connected = True
        self.update()



JarbasGUI()
gtk.main()