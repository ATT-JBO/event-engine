__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

import resources

class Asset(object):
    """
	The base class for factory objects that represent assets (sensors, actuators, virtuals, configs)
	"""

    def __init__(self, connection=None, id=None, name=None, device=None, gateway=None, style=None):
        self._ids = id
        self.name = name
        self.device = device
        self.gateway = gateway
        self.style = style
        self._id_pos = 0
        if connection:
            self._connection = connection
        else:
            self._connection = resources.defaultconnection

    def getTopics(self):
        """build the topic"""
        if self._ids:
            if isinstance(self._ids, basestring):
                return [{'asset': self._ids}]
            elif isinstance((self._ids, Asset)):
                return [{'asset': self._ids.id}]
            elif isinstance((self._ids, list)):
                return [{'asset': x if isinstance(x, basestring) else x.id} for x in self._ids]
            else:
                raise Exception("unsupported data format")
        elif self.style:
            "get all assets with specified style"
            # todo: query all or specified devices/gateways for assets that match the style +
        elif not self.gateway and not self.device and not self.name:
            raise LookupError("no filter values specified, can't find asset(s)")
        else:
            gateways = devices = names = None
            if self.gateway:
                if isinstance(self.gateway, basestring):
                    gateways = [self.gateway]
                elif isinstance(self.gateway, resources.Gateway):
                    gateways = [self.gateway.id]
                elif isinstance(self.gateway, list):                                           #must be a list of gateway id's or gateway objects, can be mingled.
                    gateways = [i if isinstance(i, basestring) else i.id for i in self.gateway]
                else:
                    raise Exception("invalid gateway reference, can't build topic")
            if self.device:
                if not self.device or isinstance(self.device, basestring):
                    devices = [self.device]
                elif isinstance(self.device, resources.Device):
                    if self.device._id:
                        devices = [self.device.id]
                    else:
                        devices = [self.device.name]
                elif isinstance(self.device, list):
                    devices = [i if isinstance(i, basestring) else i.id for i in self.device]
                else:
                    raise Exception("invalid device reference, can't build topic")
            if self.name:
                if not self.name or isinstance(self.name, basestring):
                    names = [self.name]
                else:
                    names = self.name
            results = []
            if gateways:
                for gateway in gateways:
                    if devices:
                        for device in devices:
                            if names:
                                for name in names:
                                    results.append({'gateway': gateway, 'device': device, 'asset': name})
                            else:
                                results.append({'gateway': gateway, 'device': device, 'asset': '+'})
                    elif names:
                        for name in names:
                            results.append({'gateway': gateway, 'asset': name, 'device': '+'})
                    else:
                        results.append({'gateway': gateway, 'device': device})
            elif devices:
                for device in devices:
                    if names:
                        for name in names:
                            results.append({'device': device, 'asset': name})
                    else:
                        results.append({'device': device, 'asset': '+'})
            elif names:
                for name in names:
                    results.append({'device': '+', 'asset': name})
            else:
                results.append({'device': '+', 'asset': '+'})
            return results

    def getIds(self):
        """return all the id's that were defined """
        if self._id:
            return self._id
        elif self.gateway:
            "query from gateway"
            raise NotImplementedError()
        elif self.device:
            "query from device"
            raise NotImplementedError()
        elif self.name:
            "get all asset with specified name"
            raise NotImplementedError()
        elif self.style:
            "get all assets with specified style"
            raise NotImplementedError()
        else:
            raise LookupError("no filter values specified, can't find asset(s)")

    def _isValid(self, asset):
        """checks if the asset mathces the filter that this factory uses"""
        if self.name:
            return asset.name == self.name
        if self._ids:
            return asset.id in self._ids
        if self.device:
            if isinstance(basestring, self.device):
                return asset.device.id == self.device
            else:
                return asset.device.id == self.device.id
        else:
            raise NotImplemented()

    @property
    def current(self):
        """get the current asset that triggered this event, if it matches this filter"""
        if resources.trigger and self._isValid(resources.trigger):
            return resources.trigger
        return None

    @property
    def connection(self):
        return self._connection

class Sensor(Asset):
    """genrates the list of assets, if required"""

    def __iter__(self):
        return self

    def next(self):
        if not self._ids:
            self._ids = self.getIds()
        if self._id_pos < len(self._ids):
            res = self._ids[self._id_pos]
            self._id_pos += 1
            return resources.Sensor(res)
        else:
            raise StopIteration()


class Actuator(Asset):
    """generates actautors"""

    def __iter__(self):
        return self

    def next(self):
        if not self._ids:
            self._ids = self.getIds()
        if self._id_pos < len(self._ids):
            res = self._ids[self._id_pos]
            self._id_pos += 1
            return resources.Actuator(res)
        else:
            raise StopIteration()