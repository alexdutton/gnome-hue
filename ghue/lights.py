import functools
import gi

from ghue.device.abc import Light, Colorable
from ghue.widget_page import WidgetPage

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio


class LightsPage(WidgetPage):
    notebook_label = 'Lights'

    def get_widget(self, device):
        if isinstance(device, Light):
            return LightWidget(device)


class LightWidget(Gtk.Grid):
    def __init__(self, device):
        super(LightWidget, self).__init__(halign=Gtk.Align.FILL, column_homogeneous=False)

        self.device = device
        self.device.connect('device-changed', self.on_device_changed)

        self.label = Gtk.Label(label=device.get('name'), xalign=0, halign=Gtk.Align.FILL, hexpand=True)
        self.attach(self.label, 0, 0, 1, 1)

        self.brightness = Gtk.HScale(halign=Gtk.Align.FILL, hexpand=True, adjustment=Gtk.Adjustment(lower=0, upper=254, step_increment=1),
                                     draw_value=False)
        self.brightness.set_value(device.brightness if device.on else 0)
        self.brightness.connect('value-changed', self.on_brightness_changed)
        self.attach(self.brightness, 0, 1, 3 if isinstance(device, Colorable) else 2, 1)

        self.reachable = Gtk.Image(icon_name='' if device.reachable else 'error')
        self.attach(self.reachable, 1, 0, 1, 1)

        if isinstance(device, Colorable):
            self.select_color_button = Gtk.Button(tooltip_text='Select color')
            self.select_color_button.connect('clicked', self.on_select_color)
            icon = Gio.ThemedIcon(name='gtk-select-color')
            image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
            self.select_color_button.add(image)
            self.attach(self.select_color_button, 2, 0, 1, 1)

    def on_select_color(self, *args, **kwargs):
        popover = Gtk.Popover()
        popover.set_relative_to(self.select_color_button)
        popover.set_size_request(200, -1)
        #popover.connect('closed', lambda *args: self.window.remove(popover))

        hue_scale = Gtk.HScale(adjustment=Gtk.Adjustment(lower=0, upper=65535, step_increment=1), draw_value=False)
        hue_scale.set_value(self.device.hue)
        hue_scale.connect('value-changed', self.on_hue_changed)

        sat_scale = Gtk.HScale(adjustment=Gtk.Adjustment(lower=0, upper=255, step_increment=1), draw_value=False)
        sat_scale.set_value(self.device.saturation)
        sat_scale.connect('value-changed', self.on_sat_changed)

        hsv = Gtk.HSV()
        hsv.set_color(self.device.hue / 65536. if self.device.on else 0,
                      self.device.saturation / 256.,
                      self.device.brightness / 256.)
        hsv.set_metrics(150, 15)
        hsv.connect('changed', self.on_hsv_changed)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # vbox.pack_start(Gtk.Label(label="Hue"), False, False, 0)
        # vbox.pack_start(hue_scale, False, False, 0)
        # vbox.pack_start(Gtk.Label(label="Saturation"), False, False, 0)
        # vbox.pack_start(sat_scale, False, False, 0)
        vbox.pack_start(hsv, False, False, 0)
        popover.add(vbox)
        popover.show_all()

    def on_device_changed(self, device, changed):
        if {'brightness', 'on'} & changed:
            self.brightness.set_value(device.brightness if device.on else 0)
        if 'reachable' in changed:
            self.reachable.set_from_icon_name('' if device.reachable else 'error', Gtk.IconSize.BUTTON)

    def on_brightness_changed(self, scale):
        value = int(scale.get_value())
        if value == 0:
            self.set_light({'on': False})
        else:
            self.set_light({'on': True, 'brightness': value})

    def on_brightness_changed(self, scale):
        value = int(scale.get_value())
        if value == 0:
            self.device.set({'on': False})
        else:
            self.device.set({'on': True, 'brightness': value})

    def on_hue_changed(self, scale):
        value = int(scale.get_value())
        self.device.set({'hue': value})

    def on_sat_changed(self, scale):
        value = int(scale.get_value())
        self.device.set({'saturation': value})

    def on_hsv_changed(self, hsv):
        h, s, v = hsv.get_color()
        if v == 0:
            self.device.set({'on': False})
        else:
            self.device.set({'hue': int(h * 65536),
                             'saturation': int(s * 256),
                             'brightness': int(v * 256),
                             'on': True})
