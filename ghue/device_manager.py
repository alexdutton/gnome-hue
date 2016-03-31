from gi.repository import GObject


class DeviceManager(GObject.GObject):
    def __init__(self, controller):
        super(DeviceManager, self).__init__()
        self._controller = controller