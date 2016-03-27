from gi.repository import Gtk


class SchedulesPage(Gtk.ScrolledWindow):
    def __init__(self, window):
        super(SchedulesPage, self).__init__()
        self.window = window
        scrolled__window = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        self.vbox = Gtk.VBox(valign=Gtk.Align.START, border_width=5)
        scrolled__window.add(self.vbox)
        self.add(scrolled__window)

        self.widgets = {}

    @property
    def state(self):
        return self.window.state['schedules']

    def schedule_added(self, id, schedule):
        schedule_widget = ScheduleWidget(self, id)
        self.vbox.pack_start(schedule_widget, False, False, 5)
        self.widgets[id] = schedule_widget
        sorted_widgets = sorted(self.widgets.values(),
                               key=lambda w : w.state['description'])
        self.vbox.reorder_child(schedule_widget,
                                sorted_widgets.index(schedule_widget))

    def schedule_changed(self, id, schedule, changed):
        pass
    def schedule_removed(self, id, schedule):
        pass


class ScheduleWidget(Gtk.Grid):
    def __init__(self, page, id):
        super(ScheduleWidget, self).__init__(halign=Gtk.Align.FILL, column_homogeneous=False)
        self.id = id
        self.page = page

        self.label = Gtk.Label(label=self.state['description'], xalign=0, halign=Gtk.Align.FILL, hexpand=True)
        self.attach(self.label, 0, 0, 1, 1)

    @property
    def state(self):
        return self.page.state[self.id]