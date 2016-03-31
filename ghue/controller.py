from gi.repository import GObject

from ghue.device.abc import Device
from ghue.device_manager import DeviceManager


class Controller(GObject.GObject):
    __gsignals__ = {
        'device-added': (GObject.SIGNAL_RUN_FIRST, None, (Device,)),
        'device-removed': (GObject.SIGNAL_RUN_FIRST, None, (Device,)),
        'device-manager-added': (GObject.SIGNAL_RUN_FIRST, None, (DeviceManager,)),
        'device-manager-removed': (GObject.SIGNAL_RUN_FIRST, None, (DeviceManager,)),
    }

    def __init__(self):
        super(Controller, self).__init__()
        self._device_managers = []

    def add_device_manager(self, device_manager):
        self._device_managers.append(device_manager)
        self.emit('device-manager-added', device_manager)

    def refresh_state(self):
        for device_manager in self._device_managers:
            device_manager.refresh_state()
