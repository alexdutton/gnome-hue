from __future__ import absolute_import

import abc
import copy

import jsonpointer
from bidict import bidict

from ghue.device.abc import Light, Dimmable, Colorable, Controlable, Schedule, Device
from ghue.device_manager import DeviceManager
from phue import Bridge


class HueDeviceManager(DeviceManager):
    def __init__(self, **kwargs):
        DeviceManager.__init__(self, kwargs.pop('controller'))
        self._bridge = kwargs.pop('bridge')
        self._state = {'lights': {}, 'schedules': {}, 'groups': {}}
        self._devices = {}

    def refresh_state(self):
        self.set_state(self._bridge.get_api())
        return self._state

    @property
    def state(self):
        return self._state

    def set_state(self, state):
        last_state = self._state
        self._state = state
        for name in ('lights', 'schedules'):
            for id in set(state[name]) - set(last_state[name]):
                self._devices[(name, id)] = _device_classes[name](self, id)
                self._controller.emit('device-added', self._devices[(name, id)])
            for id in set(last_state['lights']) - set(state['lights']):
                device = self._devices.pop((name, id))
                self._controller.emit('device-removed', device)
            for id in set(state[name]) & set(last_state[name]):
                device = self._devices[(name, id)]
                changed = set()
                for local, canonical in device.properties.items():
                    if state[name][id].get(local) != last_state[name][id].get(local):
                        changed.add(canonical)

                if 'state' in state[name][id]:
                    for local, canonical in device.state_properties.items():
                        if state[name][id]['state'].get(local) != last_state[name][id]['state'].get(local):
                            changed.add(canonical)
                if changed:
                    device.emit('device-changed', changed)

    def set_light(self, *args, **kwargs):
        results = self._bridge.set_light(*args, **kwargs)[0]
        state = copy.deepcopy(self._state)
        for result in results:
            if 'success' in result:
                k, v = result['success'].popitem()
                jsonpointer.set_pointer(state, k, v)
        self.set_state(state)


class HueDevice(Device):
    properties = bidict()
    state_properties = bidict()

    @abc.abstractproperty
    def state_key(self):
        pass

    def __init__(self, device_manager, id):
        self._device_manager, self._id = device_manager, id
        super(HueDevice, self).__init__()

    def get(self, name):
        if name in self.properties.inv:
            return self._device_manager.state[self.state_key][self._id][self.properties.inv[name]]
        elif name in self.state_properties.inv:
            return self._device_manager.state[self.state_key][self._id]['state'][self.state_properties.inv[name]]


class HueSchedule(Schedule, HueDevice):
    properties = bidict(name='name',
                        description='description')
    state_key = 'schedules'

    @property
    def sort_key(self):
        return (self.get('name'), self.get('description'))


class HueLight(Light, Controlable, HueDevice):
    properties = bidict(name='name')
    state_properties = bidict(on='on',
                              bri='brightness',
                              hue='hue',
                              sat='saturation',
                              reachable='reachable')
    state_key = 'lights'

    def __new__(cls, device_manager, id):
        state = device_manager.state['lights'][id]['state']
        if 'hue' in state:
            return super(HueLight, cls).__new__(ColorableHueLight, device_manager, id)
        elif 'bri' in state:
            return super(HueLight, cls).__new__(DimmableHueLight, device_manager, id)
        else:
            return super(HueLight, cls).__new__(HueLight, device_manager, id)

    @property
    def sort_key(self):
        return self.get('name')

    def set(self, items):
        if 'name' in items:
            self._device_manager.set_light(int(self._id), 'name', items.pop('name'))
        if items:
            self._device_manager.set_light(int(self._id), {self.state_properties.inv[k]: v for k, v in items.items()})


class DimmableHueLight(Dimmable, HueLight):
    pass


class ColorableHueLight(Colorable, DimmableHueLight):
    pass


class HueGroup(HueLight):
    state_key = 'groups'

_device_classes = {
    'lights': HueLight,
    'schedules': HueSchedule,
    'groups': HueGroup,
}
