
# resources Module


## Data
- `defaultconnection = None` 
- `parameters = {}` 
- `trigger = None` 
- `valueStore = {}` 

## Functions

### buildFromTopic 

```Python
buildFromTopic(path)
``` 

builds an object based on the specified topic path.

_parameters:_

- path:


_returns_: 

## resources.Actuator Objects



### create 

```Python
create(connection, device, name, label, description='', profile='string', style='Undefined')
``` 



### on_actuate 

the callback for when this actuator receives a command.


_returns_: None or the callback function that has previously been assigned to this object. 

### set_on_actuate 

the callback for when this actuator receives a command.


_returns_: None or the callback function that has previously been assigned to this object. 

## resources.Asset Objects



### __init__ 

```Python
__init__(self, id=None, gateway=None, device=None, name=None, definition=None, connection=None)
``` 



### control 

get the control attached to this asset 

### current 

```Python
current()
``` 

get the Asset that triggered the current activity


_returns_: 

### device 

Get the device that owns this asset. 

### getTopics 

```Python
getTopics(self)
``` 

inheriters have to re-implement this function. 

### profile 



### updateState 

```Python
updateState(self, value)
``` 

sends the value to the cloud in order to update the current state of the asset.

_parameters:_

- `value:` the new value


_returns_: None 

### value 

get the current value of the object 

### value_at 

get the datetime when the last value was recorded.


_returns_: datetime object or None. 

## resources.Device Objects



### __init__ 

```Python
__init__(self, id=None, name=None, gateway=None, style=None, connection=None)
``` 



### assets 



### getTopics 

```Python
getTopics(self)
``` 

inheriters have to re-implement this function. 

## resources.Gateway Objects



### __init__ 

```Python
__init__(self, id, connection=None)
``` 



## resources.IOTObject Objects



### __init__ 

```Python
__init__(self, connection=None)
``` 

create the object
<type>type connection:</type> att.HttpClient

_parameters:_

- `connection:` the att connection to use. 

### gateway 

Get the device that owns this asset. 

### getIds 

```Python
getIds(self)
``` 



### getTopics 

```Python
getTopics(self)
``` 

inheriters have to re-implement this function. 

### id 

get the name of the item 

### name 

get the name of the item 

### title 

get the title of the asset 

## resources.Parameter Objects



### __init__ 

```Python
__init__(self, name, title, description, datatype, gateway=None, device=None)
``` 

init the object parameter.

_parameters:_

- `gateway:` optional, in case of device or asset relative to a gateway
- `device:` optional, in case of asset relative to a device
- `name:` name of the parameter, Should be unique, within the application (checked), used to identify the value.
- `title:` a human readable title
- `description:` a user readable description.
- `datatype:` the datatype of the varaible. Currently supported values: 'asset', 'sensor', 'actuator', 'device', 'gateway' 

### value 

returns an object representing the value for the parameter 

## resources.Sensor Objects



### create 

```Python
create(connection, device, name, label, description='', profile='string', style='Undefined')
``` 



## resources.Virtual Objects



### create 

```Python
create(connection, device, name, label, description='', profile='string', style='Undefined')
``` 


