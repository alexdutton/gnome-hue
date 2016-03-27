import functools
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

import jsonpointer
import phue

from .lights import LightsPage
from .schedules import SchedulesPage

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, bridge):
        super(MainWindow, self).__init__(title="Philips Hue",
                                         default_width=400,
                                         default_height=400,
                                         type=Gtk.WindowType.TOPLEVEL)

        self.bridge = bridge

        self.header_bar = Gtk.HeaderBar(title="Philips Hue")
        self.header_bar.set_show_close_button(True)
        self.set_titlebar(self.header_bar)

        self.rediscover_button = Gtk.Button(tooltip_text="Discover new lights")
        self.rediscover_button.connect('clicked', self.refresh_from_api)
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

        self.lights_page = LightsPage(self)
        self.notebook.append_page(self.lights_page,
                                  Gtk.Label(label='Lights'))

        self.schedules_page = SchedulesPage(self)
        self.notebook.append_page(self.schedules_page,
                                  Gtk.Label(label='Schedules'))

        self.state = {'lights': {},
                      'schedules': {}}
        self.refresh_from_api()

    def refresh_from_api(self, *args):
        last_state = self.state
        self.state = self.bridge.get_api()
        for id in set(self.state['lights']) - set(last_state['lights']):
            self.lights_page.light_added(id, self.state['lights'][id])
        for id in set(last_state['lights']) - set(self.state['lights']):
            self.lights_page.light_removed(id, last_state['lights'][id])
        for id in set(self.state['lights']) & set(last_state['lights']):
            if self.state['lights'][id]['name'] != last_state['lights'][id]['name']:
                self.lights_page.light_name_changed(id, self.state['lights'][id]['name'])
            changed = set()
            for k in self.state['lights'][id]['state']:
                if self.state['lights'][id]['state'][k] != last_state['lights'][id]['state'].get(k):
                    changed.add(k)
            if changed:
                self.lights_page.light_changed(id, self.state['lights'][id]['state'], changed)

        for id in set(self.state['schedules']) - set(last_state['schedules']):
            self.schedules_page.schedule_added(id, self.state['schedules'][id])
        for id in set(last_state['schedules']) - set(self.state['schedules']):
            self.schedules_page.schedule_removed(id, last_state['schedules'][id])
        for id in set(self.state['schedules']) & set(last_state['schedules']):
            for k in self.state['schedules'][id]:
                if self.state['schedules'][id][k] != last_state['schedules'][id].get(k):
                    changed.add(k)
            if changed:
                self.schedules_page.schedule_changed(id, self.state['schedules'][id], changed)


    def all_off(self, *args):
        phue.AllLights(self.bridge).on = False
        for id in self.state:
            if self.state['lights'][id]['state']['on']:
                self.state['lights'][id]['state']['on'] = False
                self.light_changed(id, self.state['lights'][id]['state'], {'on'})

    def set_light(self, *args, **kwargs):
        results = self.bridge.set_light(*args, **kwargs)[0]
        for result in results:
            if 'success' in result:
                k, v = result['success'].popitem()
                jsonpointer.set_pointer(self.state, k, v)

