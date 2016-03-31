from __future__ import absolute_import

import abc
import six

from gi.repository import GObject
from gi.types import GObjectMeta


class DeviceMeta(GObjectMeta, abc.ABCMeta):
    pass


class Device(six.with_metaclass(DeviceMeta, GObject.GObject)):
    __gsignals__ = {
        'device-changed': (GObject.SIGNAL_RUN_FIRST, None, (object,))
    }

    @property
    def reachable(self):
        return self.get('reachable')

    @abc.abstractmethod
    def set(self, items):
        pass


class Light(Device):
    pass


class Schedule(Device):
    pass


class Controlable(Device):
    @property
    def on(self):
        return self.get('on')

    @on.setter
    def on(self, value):
        self.set({'on': value})


class Dimmable(Device):
    @property
    def brightness(self):
        return self.get('brightness')

    @brightness.setter
    def brightness(self, value):
        return self.set({'brightness', value})


class Colorable(Device):
    @property
    def hue(self):
        return self.get('hue')

    @hue.setter
    def hue(self, value):
        return self.set({'hue', value})

    @property
    def saturation(self):
        return self.get('saturation')

    @saturation.setter
    def saturation(self, value):
        return self.set({'saturation', value})
