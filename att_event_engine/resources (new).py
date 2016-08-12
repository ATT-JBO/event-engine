__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

import attiotuserclient as iot

valueStore = {}

_toMonitor = {}
"""asset defs being monitored (can reference multiple assets)"""

trigger = None
"""the asset object that triggered the current action."""

parameters = {}
"""all the parameters that were defined in this application.
When the module is loaded, this dict is first filled with the parameter values, so that the parmater object can
find it's value as soon as possible. Otherwise, it can't supply the required object when other parts of the rules are loaded
"""

class IOTObject(object):
    def __init__(self):
        self._definition = None
        self._id = None
        self._name = None
        self._gateway = None

    def _getDefinition(self):
        """inheriters have to re-implement this function."""
        return None

    def getTopics(self):
        """inheriters have to re-implement this function."""
        return None

    def getIds(self):
        if not self._id:
            definition = self._getDefinition()
            if definition:
                self._id = definition['id']
        return [self._id]

    @property
    def title(self):
        """get the title of the asset"""
        definition = self._getDefinition()
        if definition:
            return str(definition['title'])
        return None

    @property
    def gateway(self):
        """Get the device that owns this asset."""
        if self._gateway:
            if isinstance(self._gateway, basestring):
                return Gateway(self._gateway)
            else:
                return self._gateway
        else:
            definition = self._getDefinition()
            if definition and 'gateway' in definition:
                return Gateway(definition['gateway'])
            return None

    @property
    def id(self):
        if not self._id:
            definition = self._getDefinition()
            if definition:
                self._id = str(definition['id'])
        return self._id

    @property
    def name(self):
        if not self._name:
            definition = self._getDefinition()
            if definition:
                self._name = str(definition['name'])
        return self._name


class _AssetSelector:
    """a helper class for the Device.assets property, to dynamically generate asset objects and restrict to only getting values.
    This technique saves on the nr of data base calls that have to be made."""

    def __init__(self, device):
        self.device = device

    def __getitem__(self, key):
        return Asset(device=self.device, name=key)

    def __setitem__(self, key, value):
        raise Exception("assigning assets not yet supported")

class Device(IOTObject):
    """wraps a device object"""

    def __init__(self, id=None, name=None,  gateway=None, style=None):
        super(Device, self).__init__()
        if id:
            self._id = id
        elif gateway and name:
            self._gateway = gateway
            self._name = name
        else:
            raise LookupError("either id or gateway and name have to be specified")
        self._definition = None
        self._assets = None

    def _getGatewayId(self):
        if self._gateway:
            if isinstance(self._gateway, basestring):
                return self._gateway
            else:
                return self._gateway.id

    def _getDefinition(self):
        """load the json def for this object"""
        if not self._definition:
            if self._id:
                self._definition = iot.getDevice(self._id)
            else:
                self._definition = iot.getDevice(gatewayId=self._getGatewayId(), deviceName=self.name)
        return self._definition

    def getTopics(self):
        """inheriters have to re-implement this function."""
        if self._id:
            return [{'device': self._id}]
        elif self._gateway:
            return [{'device': self.name, 'gateway': self._getGatewayId()}]
        else:
            raise Exception("id or gateway have to be specified")

    @property
    def assets(self):
        if not hasattr(self, '_assets'):
            self._assets = _AssetSelector(self)
        return self._assets


class Gateway(IOTObject):
    """wraps a gateway
    """

    def __init__(self, id):
        super(Gateway, self).__init__()
        if id:
            self._id = id
        self._definition = None

    def _getDefinition(self):
        """load the json def for this object"""
        if not self._definition:
            self._definition = iot.getGateway(self._id)
        return self._definition

class Asset(IOTObject):
    def __init__(self, id=None, gateway=None, device=None, name=None, definition=None):
        super(Asset, self).__init__()
        if id:
            self._id = id
            self._gateway = None
            self._device = None
            self._name = None
        elif device and name:
            self._id = None
            self._gateway = gateway
            self._device = device
            self._name = name
        elif definition:
            self._definition = definition
            self._id = str(definition['id'])
            self._name = str(definition['name'])
            if 'deviceId' in definition:
                self._device = str(definition['deviceId'])
            else:
                self._device = None
            if 'gatewayId' in definition:
                self._gateway = str(definition['gatewayId'])
        else:
            raise LookupError("either id or device and name have to be specified")

    def _getGatewayId(self):
        if self._gateway:
            if isinstance(self._gateway, basestring):
                return self._gateway
            else:
                return self._gateway.id
        elif isinstance(self._device, Device) and self._device._gateway:
            if isinstance(self._device._gateway, basestring):
                return self._device._gateway
            else:
                return self._device._gateway.id

    def _getDeviceName(self):
        if isinstance(self._device, basestring):
            return self._device
        else:
            return self._device.name

    def _getDeviceId(self):
        if isinstance(self._device, basestring):
            return self._device
        else:
            return self._device.id

    def _getDefinition(self): 
        """the json object retrieved from the cloud."""
        if not self._definition:
            if self._id:
                self._definition = iot.getAsset(self._id)
            elif self._gateway or (self._device and hasattr(self._device, '_gateway') and self._device._gateway):
                self._definition = iot.getAsset(gateway=self._getGatewayId(), device=self._getDeviceName(), name=self._name)
                if self._definition:
                    self._id = self._definition['id']
            else:
                self._definition = iot.getAsset(device=self._getDeviceId(), name=self._name)
                if self._definition:
                    self._id = self._definition['id']
            #don't copy over the state from the definition, this appears to be cached on the server and might not contain the lasxt value.
            #if self._definition and 'state' in self._definition and not self._id in valueStore:     # copy over the state value if we don't yet have it for this asset, so we don't have to query for it 2 times.
            #    valueStore[self._id] = self._definition['state']
        return self._definition

    def getTopics(self):
        """inheriters have to re-implement this function."""
        if self._id:
            return [{'asset': self._id}]
        else:
            gateway = self._getGatewayId()
            if gateway:
                return [{'asset': self._name, 'device': self._getDeviceName(), 'gateway': gateway}]
            else:
                return [{'asset': self._name, 'device': self._getDeviceId()}]


    @property
    def value(self):
        """get the current value of the object"""
        if not self._id:                    # we need the id to access the valuestore. We can get the id from the definition if need be.
            self._getDefinition()
        if not self._id in valueStore:
            val = iot.getAssetState(self.id)
            if val:
                result = val['value']
            else:
                result = None
            valueStore[self._id] = result
        else:
            result = valueStore[self._id]
        return result


    @value.setter
    def value(self, value):
        self._setValue(value)

    def _setValue(self, value):
        raise Exception("write value only supported on actuators")

    @property
    def device(self):
        """Get the device that owns this asset."""
        if not self._device:
            definition = self._getDefinition()
            if definition and 'deviceId' in definition:
                return Device(str(definition['deviceId']))
            return None
        elif isinstance(self._device, basestring):
            return Device(self._device)
        else:
            return self._device

    @property
    def control(self):
        """get the control attached to this asset"""
        definition = self._getDefinition()
        return definition['control']

    def profile(self):
        """get the profile definition of the asset"""
        definition = self._getDefinition()
        return definition['profile']


class Sensor(Asset):
    """renaming of the asset class, for mapping with cloud objects"""


class Actuator(Asset):
    """an asset that adds write-value functionality to the object"""

    def _setValue(self, value):
        """send the value to the actuator"""
        if self._gateway or self._device:
            iot.send(self.name, value, gateway=self._gateway, device=self._device)
        else:
            iot.send(self.id, value)
        valueStore[self.id] = value



class Parameter(object):
    """
    represents a parameter value that has to be supplied by the user upon activation of the application.
    The system will set the provided value for the parameter before the condition is evaluated.
    For testing purposes, you should provide the value yourself upon initialization.

    Currently supported values are: the id of an 'asset', 'sensor', 'actuator', 'device', 'gateway'
    """

    def __init__(self, name, title, description, datatype, gateway=None, device=None):
        """
        init the object parameter.
        :param gateway: optional, in case of device or asset relative to a gateway
        :param device: optional, in case of asset relative to a device
        :param name: name of the parameter, Should be unique, within the application (checked), used to identify the value.
        :param title: a human readable title
        :param description: a user readable description.
        :param datatype: the datatype of the varaible. Currently supported values: 'asset', 'sensor', 'actuator', 'device', 'gateway'
        """
        if name in parameters and isinstance(parameters[name], Parameter):
            raise Exception('parameter with same name already exists')
        self.name = name
        self.title = title
        self.description = description
        self.datatype = datatype
        self.gateway = gateway                              # references to objects that this object should be relative towards.
        self.device = device
        if name in parameters:
            self._referenced = parameters[name]
        parameters[name] = self                                 # so that the app can find all the parameters for this rule set and ask the user to supply the values.

    def _setValue(self, value):
        """assing a value to the parameter"""
        self._referenced = value

    @property
    def value(self):
        '''returns an object representing the value for the parameter'''
        if self.datatype == 'asset':
            if not self.gateway and not self.device:
                return Asset(id=self._referenced)
            elif self.gateway:
                return Asset(name=self._referenced, device=self.device, gateway=self.gateway)
        elif self.datatype == 'sensor':
            return Sensor(id=self._referenced)
        elif self.datatype == 'actuator':
            return Actuator(id=self._referenced)
        elif self.datatype == 'device':
            if not self.gateway:
                return Device(id=self._referenced)
            else:
                return Device(name=self._referenced, gateway=self.gateway)
        elif self.datatype == 'gateway':
            return Gateway(id=self._referenced)
        elif self.datatype in ['number', 'integer', 'string', 'boolean', 'object', 'list']:       # basic data types
            return self._referenced
        else:
            raise Exception("not supported")