import functools
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio


class LightsPage(Gtk.ScrolledWindow):
    def __init__(self, window):
        super(LightsPage, self).__init__(hscrollbar_policy=Gtk.PolicyType.NEVER)
        self.window = window
        self.set_light = window.set_light
        scrolled__window = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        self.vbox = Gtk.VBox(valign=Gtk.Align.START, border_width=5)
        scrolled__window.add(self.vbox)
        self.add(scrolled__window)

        self.light_widgets = {}

    @property
    def state(self):
        return self.window.state['lights']

    def light_added(self, id, light_state):
        light_widget = LightWidget(self, id)
        self.vbox.pack_start(light_widget, False, False, 5)
        self.light_widgets[id] = light_widget
        sorted_lights = sorted(self.light_widgets.values(),
                               key=lambda lw : lw.state['name'])
        self.vbox.reorder_child(light_widget,
                                sorted_lights.index(light_widget))

    def light_changed(self, id, state, changed):
        self.light_widgets[id].light_changed(state, changed)

    def light_removed(self, id, last_light_state):
        light_widget = self.light_widgets.pop(id)
        self.vbox.remove(light_widget)

class LightWidget(Gtk.Grid):
    def __init__(self, lights_page, id):
        super(LightWidget, self).__init__(halign=Gtk.Align.FILL, column_homogeneous=False)

        self.lights_page = lights_page
        self.set_light = functools.partial(lights_page.set_light, int(id))
        self.id = id

        self.label = Gtk.Label(label=self.state['name'], xalign=0, halign=Gtk.Align.FILL, hexpand=True)
        self.attach(self.label, 0, 0, 1, 1)

        self.brightness = Gtk.HScale(halign=Gtk.Align.FILL, hexpand=True, adjustment=Gtk.Adjustment(lower=0, upper=254, step_increment=1),
                                     draw_value=False)
        self.brightness.set_value(self.state['state']['bri'] if self.state['state']['on'] else 0)
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
        return self.lights_page.state[self.id]

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
