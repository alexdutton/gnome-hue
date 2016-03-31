from gi.repository import Gtk

from ghue.device.abc import Schedule
from ghue.widget_page import WidgetPage


class SchedulesPage(WidgetPage):
    notebook_label = 'Schedules'

    def get_widget(self, device):
        if isinstance(device, Schedule):
            return ScheduleWidget(device)


class ScheduleWidget(Gtk.Grid):
    def __init__(self, device):
        super(ScheduleWidget, self).__init__(halign=Gtk.Align.FILL, column_homogeneous=False)
        self.id = id
        self.device = device

        self.label = Gtk.Label(label=device.get('description'), xalign=0, halign=Gtk.Align.FILL, hexpand=True)
        self.attach(self.label, 0, 0, 1, 1)
