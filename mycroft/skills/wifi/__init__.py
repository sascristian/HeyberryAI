
from os.path import dirname
import os
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from time import sleep
import NetworkManager
import dbus.mainloop.glib
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

import random

bus = dbus.SystemBus()
# Obtain handles to manager objects.
manager_bus_object = bus.get_object("org.freedesktop.NetworkManager",
                                    "/org/freedesktop/NetworkManager")
#manager = dbus.Interface(manager_bus_object,
#                         "org.freedesktop.NetworkManager")
manager_props = dbus.Interface(manager_bus_object,
                               "org.freedesktop.DBus.Properties")

__author__ = 'jarbas'

LOGGER = getLogger(__name__)

class WifiSkill(MycroftSkill):

    def __init__(self):
        super(WifiSkill, self).__init__(name="WifiSkill")

        self.scriptpath = "anonsurf"#os.path.dirname(__file__) + '/anonsurf.sh'
        # (TODO make configurable, off by default)
        #self.disablewifi()

        self.vpns=[]
        self.aps=[]

        self.blacklist = ["cryptofree_linux-tcp"]

        #populate on first run
        self.available()
        self.vpn()

        self.retrys = 120

    def initialize(self):
        self.load_data_files(dirname(__file__))

        wifi_diagnostics_intent = IntentBuilder("WifiDiagnosticsIntent"). \
            require("wifidiagnostics").build()
        self.register_intent(wifi_diagnostics_intent, self.handle_wifiDiagnostics_intent)

        wifi_enable_intent = IntentBuilder("WifiEnableIntent"). \
            require("wifienable").build()
        self.register_intent(wifi_enable_intent, self.handle_wifienable_intent)

        wifi_disable_intent = IntentBuilder("WifiDisableIntent"). \
            require("wifidisable").build()
        self.register_intent(wifi_disable_intent, self.handle_wifidisable_intent)

        ap_scan_intent = IntentBuilder("APscanIntent"). \
            require("apscan").build()
        self.register_intent(ap_scan_intent, self.handle_scanAP_intent)

        vpn_scan_intent = IntentBuilder("VPNscanIntent"). \
            require("vpnscan").build()
        self.register_intent(vpn_scan_intent, self.handle_scanVPN_intent)

        active_scan_intent = IntentBuilder("activeAPscanIntent"). \
            require("activescan").build()
        self.register_intent(active_scan_intent, self.handle_scanactive_intent)

        active_info_intent = IntentBuilder("activeAPinfoIntent"). \
            require("activesinfo").build()
        self.register_intent(active_info_intent, self.handle_APinfo_intent)

        device_info_intent = IntentBuilder("deviceinfoIntent"). \
            require("deviceinfo").build()
        self.register_intent(device_info_intent, self.handle_deviceinfo_intent)

        vpn_connect_intent = IntentBuilder("VPNconnectIntent"). \
            require("vpnconnect").build()
        self.register_intent(vpn_connect_intent, self.handle_vpnconnect_intent)

        ap_connect_intent = IntentBuilder("APconnectIntent"). \
            require("apconnect").build()
        self.register_intent(ap_connect_intent, self.handle_apconnect_intent)

        anonsurf_start_intent = IntentBuilder("AnonSurfStartIntent"). \
            require("anonsurfstart").build()
        self.register_intent(anonsurf_start_intent, self.handle_anonsurf_start_intent)

        anonsurf_stop_intent = IntentBuilder("AnonSurfStopIntent"). \
            require("anonsurfstop").build()
        self.register_intent(anonsurf_stop_intent, self.handle_anonsurf_stop_intent)

        anonsurf_restart_intent = IntentBuilder("AnonSurfreStartIntent"). \
            require("anonsurfrestart").build()
        self.register_intent(anonsurf_restart_intent, self.handle_anonsurf_restart_intent)

        anonsurf_change_intent = IntentBuilder("AnonSurfChangeIntent"). \
            require("anonsurfchange").build()
        self.register_intent(anonsurf_change_intent, self.handle_anonsurf_change_intent)

        anonsurf_status_intent = IntentBuilder("AnonSurfStatusIntent"). \
            require("anonsurfstatus").build()
        self.register_intent(anonsurf_status_intent, self.handle_anonsurf_status_intent)

    def handle_anonsurf_start_intent(self, message):
        self.speak("starting global TOR tunnel")
        os.system('gksudo '+self.scriptpath+ ' start')
        self.emit_results()

    def handle_anonsurf_stop_intent(self, message):
        self.speak("stopping global TOR tunnel")
        os.system('gksudo ' + self.scriptpath + ' stop')
        self.emit_results()

    def handle_anonsurf_status_intent(self, message):
        self.speak("checking global TOR tunnel status")
        os.system('gksudo ' + self.scriptpath + ' status')
        self.emit_results()

    def handle_anonsurf_restart_intent(self, message):
        self.speak("restarting global TOR tunnel")
        os.system('gksudo ' + self.scriptpath + ' restart')
        self.emit_results()

    def handle_anonsurf_change_intent(self, message):
        self.speak("changing global TOR tunnel circuit ")
        os.system('gksudo ' + self.scriptpath + ' change')
        self.emit_results()

    def handle_wifienable_intent(self, message):
        self.enablewifi()
        self.speak("wifi enabled")
        self.emit_results()

    def handle_wifidisable_intent(self, message):
        self.disablewifi()
        self.speak("wifi disabled")
        self.emit_results()

    def handle_wifiDiagnostics_intent(self, message):
        self.speak("Network Diagnostics")
        self.diagnostics()
        self.emit_results()
        #self.speak("wifi diagnostics printed in skills service")

    def handle_scanAP_intent(self, message):
        self.available()
        if len(self.aps) > 0:
            self.speak("The following acess points are available")
            for ap in self.aps:
                self.speak(ap)
        else:
            self.speak("No available acess points")
        self.emit_results()

    def handle_scanVPN_intent(self, message):
        self.vpn()
        if len(self.vpns) > 0:
            self.speak("The following VPN services are available")
            for vpn in self.vpns:
                self.speak(vpn)
        else:
            self.speak("No available VPN connections")
        self.emit_results()

    def handle_scanactive_intent(self, message):
        self.active()
        #self.speak("active connections printed in skills service")
        self.emit_results()

    def handle_APinfo_intent(self, message):
        self.activeinfo()
        #self.speak("active acess point info printed in skills service")
        self.emit_results()

    def handle_deviceinfo_intent(self, message):
        self.devices()
        #self.speak("network device info printed in skills service")
        self.emit_results()

    def handle_vpnconnect_intent(self, message):
        i = 0
        self.speak("Trying to connect")
        if self.isvpn():
            return
        while i < len(self.vpns):
            if self.vpns[i] not in self.blacklist:
                try:
                    flag = self.connectto(self.vpns[i])
                    if flag:  # connected
                        self.speak("connecting to VPN")
                        flag = False
                        i=0
                        while not flag and i<self.retrys:
                            flag = self.isvpn()
                            sleep(0.8)
                            i+=1
                        if flag:
                            return
                        else:
                            self.speak("couldn't connect to vpn")
                except:
                    pass
            i += 1
        self.speak("vpn connection failed")
        self.emit_results()

    def handle_apconnect_intent(self, message):
        i = 0
        self.speak("Trying to connect")
        while i < len(self.aps):
            try:
                flag =self.connectto(self.aps[i])
                if flag:#connected
                    self.speak("connecting to acess point")
                    return
            except:
                pass
            i+=1
        self.speak( "connection to acess point failed")
        self.emit_results()

    ### wireless on and off   -> refactor with network manager lib
    def enablewifi(self):
        print "enabling wifi"
        manager_props.Set("org.freedesktop.NetworkManager", "WirelessEnabled",
                          True)

    def disablewifi(self):
        # Disable Wireless (optional step)
        print "disabling WiFi"
        manager_props.Set("org.freedesktop.NetworkManager", "WirelessEnabled",
                          False)

    ### connect/disconnect to specific network
    def connectto(self, name):
        #self.enablewifi()
        """
        Activate a connection by name
        """
        # TODO refactor this shit for already scanned APs, this is old code but works
        # Find the connection
        connections = NetworkManager.Settings.ListConnections()
        # print connections
        cons = []
        ids = []
        for x in connections:
            try:
                ids.append(x.GetSettings()['connection']['id'])
                cons.append(x)
                # print x.GetSettings()['connection']['id']
            except:
                pass

        # build dict of cons
        connections = dict(zip(ids, cons))
        #
        conn = connections[name]

        # Find a suitable device
        ctype = conn.GetSettings()['connection']['type']
        print ctype
        if ctype == 'vpn':
            for dev in NetworkManager.NetworkManager.GetDevices():
                if dev.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED and dev.Managed:
                    break
            else:
                print("No active, managed device found")
                return False
        else:
            dtype = {
                '802-11-wireless': NetworkManager.NM_DEVICE_TYPE_WIFI,
                '802-3-ethernet': NetworkManager.NM_DEVICE_TYPE_ETHERNET,
                'gsm': NetworkManager.NM_DEVICE_TYPE_MODEM,
            }.get(ctype, ctype)
            devices = NetworkManager.NetworkManager.GetDevices()

            for dev in devices:
                if dev.DeviceType == dtype:
                    if dev.State == NetworkManager.NM_DEVICE_STATE_DISCONNECTED:
                        break
                    else:
                        print "cant connect to " + name
            else:
                print("No suitable and available %s device found" % ctype)
                return False
                # sys.exit(1)

        # And connect
        NetworkManager.NetworkManager.ActivateConnection(conn, dev, "/")
        return True

    def disconnect(self, name):
        for conn in NetworkManager.NetworkManager.ActiveConnections:
            settings = conn.Connection.GetSettings()['connection']
            if name == "all":
                NetworkManager.NetworkManager.DeactivateConnection(conn.object_path)
                self.speak("disconnecting from " + settings['id'])
            else:
                if settings['id'] == name:
                    NetworkManager.NetworkManager.DeactivateConnection(conn.object_path)
                    self.speak("disconnecting from " + settings['id'])
                    return

    ############## info #######
    def diagnostics(self):
        # network manager info
        c = NetworkManager.const

        print("%-30s %s" % ("Version:", NetworkManager.NetworkManager.Version))
        print("%-30s %s" % ("Hostname:", NetworkManager.Settings.Hostname))
        print("%-30s %s" % ("Can modify:", NetworkManager.Settings.CanModify))
        print("%-30s %s" % ("Networking enabled:", NetworkManager.NetworkManager.NetworkingEnabled))
        print("%-30s %s" % ("Wireless enabled:", NetworkManager.NetworkManager.WirelessEnabled))
        print("%-30s %s" % ("Wireless hw enabled:", NetworkManager.NetworkManager.WirelessHardwareEnabled))
        print("%-30s %s" % ("Wwan enabled:", NetworkManager.NetworkManager.WwanEnabled))
        print("%-30s %s" % ("Wwan hw enabled:", NetworkManager.NetworkManager.WwanHardwareEnabled))
        print("%-30s %s" % ("Wimax enabled:", NetworkManager.NetworkManager.WimaxEnabled))
        print("%-30s %s" % ("Wimax hw enabled:", NetworkManager.NetworkManager.WimaxHardwareEnabled))
        print("%-30s %s" % ("Overall state:", c('state', NetworkManager.NetworkManager.State)))

        print("")
        ### permission info
        print("Permissions")
        for perm, val in sorted(NetworkManager.NetworkManager.GetPermissions().items()):
            print("%-30s %s" % (perm[31:] + ':', val))

        print("")

        self.devices()

        print("")

        self.available()

        print("")

        self.vpn()

        print("")

        self.active()

        print("")

        self.activeinfo()

    ## scan acess points
    def available(self):
        print("Available connections")
        self.aps[:]=[]
        for conn in NetworkManager.Settings.ListConnections():
            try:
                settings = conn.GetSettings()['connection']
                if settings['type'] == "802-11-wireless":
                    print settings['id']
                    self.aps.append(settings['id'])
            except:
                pass

    def seen(self):
        print("Seen connections")
        self.aps[:] = []
        for conn in NetworkManager.Settings.ListConnections():
            try:
                settings = conn.GetSettings()['connection']
                if settings['type'] == "802-11-wireless":
                    print settings['id']
                    self.aps.append(settings['id'])
            except:
                pass

    def vpn(self):
        print("VPN connections")
        self.vpns[:] = []
        for conn in NetworkManager.Settings.ListConnections():
            try:
                settings = conn.GetSettings()['connection']
                if settings['type'] == "vpn":
                    print settings['id']
                    self.vpns.append(settings['id'])
            except:
                pass

    def active(self):
        self.speak("Active connections")
        print("%-30s %-20s %-10s %s" % ("Name", "Type", "Default", "Devices"))
        for conn in NetworkManager.NetworkManager.ActiveConnections:
            settings = conn.Connection.GetSettings()['connection']
            print("%-30s %-20s %-10s %s" % (
                settings['id'], settings['type'], conn.Default, ", ".join([x.Interface for x in conn.Devices])))
            self.speak(settings['id'])
            self.speak("connection type")
            self.speak(settings['type'])

    def devices(self):
        c = NetworkManager.const
        self.speak("Available network devices")
        print("%-10s %-19s %-20s %s" % ("Name", "State", "Driver", "Managed?"))
        for dev in NetworkManager.NetworkManager.GetDevices():
            self.speak(dev.Interface)#name
            self.speak("state")
            self.speak(c('device_state', dev.State))
            self.speak("driver")
            self.speak(dev.Driver)
            self.speak("managed")
            self.speak(dev.Managed)
            print("%-10s %-19s %-20s %s" % (dev.Interface, c('device_state', dev.State), dev.Driver, dev.Managed))

    ### info on active acess point
    def activeinfo(self):
        """
        Display detailed information about currently active connections.
        """
        c = NetworkManager.const

        for conn in NetworkManager.NetworkManager.ActiveConnections:
            settings = conn.Connection.GetSettings()

            for s in list(settings.keys()):
                if 'data' in settings[s]:
                    settings[s + '-data'] = settings[s].pop('data')

            secrets = conn.Connection.GetSecrets()
            for key in secrets:
                settings[key].update(secrets[key])

            devices = ""
            if conn.Devices:
                devices = " (on %s)" % ", ".join([x.Interface for x in conn.Devices])
            self.speak("Active connection: %s%s" % (settings['connection']['id'], devices))
            size = max([max([len(y) for y in x.keys() + ['']]) for x in settings.values()])
            format = "%%-%ds %%s" % (size + 5)
            for key, val in sorted(settings.items()):
                for name, value in val.items():
                    if str(key) != "" and str(key) != " " and str(value) != "" and str(value) != " " and "[]" not in str(value) :
                        self.speak("   %s" % key)
                   # if str(value) != "" and str(value) != " " and "[]" not in str(value):
                        self.speak(format % (name, value))
            for dev in conn.Devices:
                self.speak("Device: " + dev.Interface)
                self.speak("Type  %s" % c('device_type', dev.DeviceType))
                # print("   IPv4 address     %s" % socket.inet_ntoa(struct.pack('L', dev.Ip4Address)))
                devicedetail = dev.SpecificDevice()
                if not callable(devicedetail.HwAddress):
                    self.speak(" MAC address  %s" % devicedetail.HwAddress)
                self.speak("IPv4 config")
                self.speak("Addresses")
                for addr in dev.Ip4Config.Addresses:
                    self.speak("%s/%d -> %s" % tuple(addr))
                self.speak(" Routes")
                for route in dev.Ip4Config.Routes:
                    self.speak("%s/%d -> %s (%d)" % tuple(route))
                self.speak("Nameservers")
                for ns in dev.Ip4Config.Nameservers:
                    self.speak(" %s" % ns)

    def isvpn(self):
        # Bail out of another vpn is active
        for conn in NetworkManager.NetworkManager.ActiveConnections:
            if conn.Vpn:
                vid = conn.Connection.GetSettings()['connection']['id']
                self.speak("The vpn %s is already active" % vid)
                return True
        return False

    def stop(self):
        self.disablewifi() #not needed?

def create_skill():
    return WifiSkill()





