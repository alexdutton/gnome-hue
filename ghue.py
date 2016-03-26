import functools
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

import jsonpointer
import phue

class MainWindow(Gtk.Window):
    def __init__(self, bridge):
        super().__init__(title="Philips Hue", default_width=400, default_height=400)

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

        lights_window = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        self.lights_vbox = Gtk.VBox(border_width=5)
        lights_window.add(self.lights_vbox)
        self.notebook.append_page(lights_window, Gtk.Label(label='Lights'))

        self.state = {'lights': {}}
        self.light_widgets = {}
        self.refresh_from_api()

    def light_added(self, id, light_state):
        light_widget = LightWidget(self, id)
        self.lights_vbox.pack_end(light_widget, False, False, 5)
        self.light_widgets[id] = light_widget

    def light_changed(self, id, state, changed):
        self.light_widgets[id].light_changed(state, changed)

    def light_removed(self, id, last_light_state):
        light_widget = self.light_widgets.pop(id)
        self.lights_vbox.remove(light_widget)

    def refresh_from_api(self, *args):
        last_state = self.state
        self.state = self.bridge.get_api()
        for id in set(self.state['lights']) - set(last_state['lights']):
            self.light_added(id, self.state['lights'][id])
        for id in set(last_state['lights']) - set(self.state['lights']):
            self.light_removed(id, last_state['lights'][id])
        for id in set(self.state['lights']) & set(last_state['lights']):
            if self.state['lights'][id]['name'] != last_state['lights'][id]['name']:
                self.light_name_changed(id, self.state['lights'][id]['name'])
            changed = set()
            for k in self.state['lights'][id]['state']:
                if self.state['lights'][id]['state'][k] != last_state['lights'][id]['state'].get(k):
                    changed.add(k)
            if changed:
                self.light_changed(id, self.state['lights'][id]['state'], changed)

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


# class LightsPage(Gtk.ScrolledWindow):
#     def __init__(self, window):
#         self.window = window


class LightWidget(Gtk.Grid):
    def __init__(self, window, id):
        super().__init__(halign=Gtk.Align.FILL, column_homogeneous=False)
        self.window = window
        self.set_light = functools.partial(window.set_light, int(id))
        self.id = id

        self.label = Gtk.Label(label=self.state['name'], xalign=0, halign=Gtk.Align.FILL, hexpand=True)
        self.attach(self.label, 0, 0, 1, 1)

        self.brightness = Gtk.HScale(halign=Gtk.Align.FILL, hexpand=True, adjustment=Gtk.Adjustment(lower=0, upper=254, step_increment=1),
                                     draw_value=False)
        self.brightness.set_value(self.state['state']['bri'])
        self.brightness.connect('value-changed', self.on_brightness_changed)
        self.attach(self.brightness, 0, 1, 3 if 'hue' in self.state['state'] else 2, 1)

        self.reachable = Gtk.Image(icon_name='' if self.state['state']['reachable'] else 'error')
        self.attach(self.reachable, 1, 0, 1, 1)

        if 'hue' in self.state['state']:
            self.select_color_button = Gtk.Button(tooltip_text='Select color')
            self.select_color_button.connect('clicked', self.on_select_color)
            icon = Gio.ThemedIcon(name='gtk-select-color')
            image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
            self.select_color_button.add(image)
            self.attach(self.select_color_button, 2, 0, 1, 1)

    @property
    def state(self):
        return self.window.state['lights'][self.id]

    def on_select_color(self, *args, **kwargs):
        popover = Gtk.Popover()
        popover.set_relative_to(self.select_color_button)
        popover.set_size_request(200, -1)
        #popover.connect('closed', lambda *args: self.window.remove(popover))

        hue_scale = Gtk.HScale(adjustment=Gtk.Adjustment(lower=0, upper=65535, step_increment=1), draw_value=False)
        hue_scale.set_value(self.state['state']['hue'])
        hue_scale.connect('value-changed', self.on_hue_changed)

        sat_scale = Gtk.HScale(adjustment=Gtk.Adjustment(lower=0, upper=255, step_increment=1), draw_value=False)
        sat_scale.set_value(self.state['state']['sat'])
        sat_scale.connect('value-changed', self.on_sat_changed)

        vbox = Gtk.VBox()
        vbox.pack_start(Gtk.Label(label="Hue"), False, False, 0)
        vbox.pack_start(hue_scale, False, False, 0)
        vbox.pack_start(Gtk.Label(label="Saturation"), False, False, 0)
        vbox.pack_start(sat_scale, False, False, 0)
        popover.add(vbox)
        popover.show_all()


    def light_changed(self, state, changed):
        if {'bri', 'on'} & changed:
            self.brightness.set_value(state['bri'] if state['on'] else 0)
        if 'reachable' in changed:
            self.reachable.set_from_icon_name('' if state['reachable'] else 'error', Gtk.IconSize.BUTTON)

    def on_brightness_changed(self, scale):
        value = int(scale.get_value())
        if value == 0:
            self.set_light({'on': False})
        else:
            self.set_light({'on': True, 'bri': value})

    def on_brightness_changed(self, scale):
        value = int(scale.get_value())
        if value == 0:
            self.set_light({'on': False})
        else:
            self.set_light({'on': True, 'bri': value})

    def on_hue_changed(self, scale):
        value = int(scale.get_value())
        value = int(scale.get_value())
        self.set_light({'hue': value})

    def on_sat_changed(self, scale):
        value = int(scale.get_value())
        self.set_light({'sat': value})

bridge = phue.Bridge('philips-hue.local')

win = MainWindow(bridge)
win.connect('delete-event', Gtk.main_quit)
win.show_all()
Gtk.main()
