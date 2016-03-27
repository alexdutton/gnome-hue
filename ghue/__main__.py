import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import phue

from .application import GHueApplication

if __name__ == '__main__':
    GLib.set_application_name("Philips Hue")
    bridge = phue.Bridge('philips-hue.local')
    app = GHueApplication(bridge)#'gnome-hue')
    app.run(None)
