import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import phue

from .window import MainWindow

if __name__ == '__main__':

    bridge = phue.Bridge('philips-hue.local')

    win = MainWindow(bridge)
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    Gtk.main()
