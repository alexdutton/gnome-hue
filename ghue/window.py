import functools
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

import jsonpointer
import phue

from .lights import LightsPage
from .schedules import SchedulesPage

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, controller):
        super(MainWindow, self).__init__(title="Philips Hue",
                                         default_width=400,
                                         default_height=400,
                                         type=Gtk.WindowType.TOPLEVEL)

        self.controller = controller

        self.header_bar = Gtk.HeaderBar(title="Philips Hue")
        self.header_bar.set_show_close_button(True)
        self.set_titlebar(self.header_bar)

        self.rediscover_button = Gtk.Button(tooltip_text="Discover new lights")
        self.rediscover_button.connect('clicked', lambda *args: self.controller.refresh_state())
        icon = Gio.ThemedIcon(name="gtk-refresh")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.rediscover_button.add(image)
        self.header_bar.pack_end(self.rediscover_button)

        self.all_off_button = Gtk.Button(tooltip_text="Turn off all lights")
        self.all_off_button.connect('clicked', self.all_off)
        icon = Gio.ThemedIcon(name="gtk-stop")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.all_off_button.add(image)
        self.header_bar.pack_end(self.all_off_button)

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        self.lights_page = LightsPage(self.controller)
        self.lights_page.add_to_notebook(self.notebook)

        self.schedules_page = SchedulesPage(self.controller)
        self.schedules_page.add_to_notebook(self.notebook)

        self.controller.refresh_state()

    def all_off(self, *args):
        phue.AllLights(self.bridge).on = False
        for id in self.state['lights']:
            if self.state['lights'][id]['state']['on']:
                self.state['lights'][id]['state']['on'] = False
                self.lights_page.light_changed(id, self.state['lights'][id]['state'], {'on'})
