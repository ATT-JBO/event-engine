
# att Module


## att.Client Objects



### __init__ 

```Python
__init__(self)
``` 

create the object 

### addMessageCallback 

```Python
addMessageCallback(self, topic, callback)
``` 

add a callback for the specified topic.

_parameters:_

- `topic:` a string with the topic to subscribe to.
- `monitor:`  a function of format: def xxx(self, json_object) or def xxx(json_object)


_returns_: None, raise Exception 

### connect 

```Python
connect(self, username, pwd, blocking=False, apiServer='api.smartliving.io', broker='broker.smartliving.io', **kwargs)
``` 

start the mqtt client and make certain that it can receive data from the IOT platform
mqttServer: (optional): the address of the mqtt server. Only supply this value if you want to a none standard server.
port: (optional) the port number to communicate on with the mqtt server. 

### connect_broker 

```Python
connect_broker(self, username, pwd, broker='broker.smartliving.io', blocking=True)
``` 

connect to the broker

_parameters:_

- `username:` username to connect with
- `pwd:` pwd to connect with
- `broker:` name of broker
- `kwargs:` extra params for descendents.


_returns_: 

### disconnect 

```Python
disconnect(self, resumable=False)
``` 

close all connections to the cloud and reset the module
if resumable is True, then only the network connections get closed, but the connection data remains, so that
you can restart connections using the reconnect features. 

### is_connected_mqtt 

True when mqtt is connected.


_returns_: boolean 

### loop 

```Python
loop(self)
``` 

in case that the connect was called in a blocking manner, then this has to be called to start the main mqtt loop 

### on_MQTTSubscribed 

```Python
on_MQTTSubscribed(client, userdata, mid, granted_qos)
``` 



### on_MQTTmessage 

```Python
on_MQTTmessage(client, userdata, msg)
``` 



### on_connect 

```Python
on_connect(client, userdata, rc)
``` 



### reconnect 

```Python
reconnect to both broker and api server.
``` 



_returns_: None 

### removeMessageCallback 

```Python
removeMessageCallback(self, topic)
``` 



### send_command_mqtt 

```Python
send_command_mqtt(self, id, value, device=None, gateway=None)
``` 

temp solution, for when we need mqtt to send commands (ping)

_parameters:_

- id:
- value:
- device:
- gateway:


_returns_: 

### subscribe 

```Python
subscribe(self, asset, callback)
``` 

monitor for changes for that asset. For more monitor features, use 'subscribeAdv'
<type>type callback:</type> function, format: callback(json_object)

_parameters:_

- `callback:` a function that will be called when a value arrives for the specified asset.
<type>type asset:</type> dict
- `asset:` a path to an asset. The path can contain gateway, device, asset 

### subscribeAdv 

```Python
subscribeAdv(self, subscriberData, topic=None)
``` 

subscribe to topics with advanced parameter options
If the topic is not provided, it is calculated from the subscriberData.
This is for apps that also calculate the topic string, so that this isn't done unnecessarily 

### unsubscribe 

```Python
unsubscribe(self, id, level='asset')
``` 

remove all the callbacks for the specified id.

_parameters:_

- `level:` which type of item: asset, device, gateway
- `id:` the id of the item (asset, device, gateway,..) to remove 

## att.HttpClient Objects



### __init__ 

```Python
__init__(self)
``` 

create the object 

### connect_api 

```Python
connect_api(self, username, pwd, apiServer='api.smartliving.io', **kwargs)
``` 

connect to the http server

_parameters:_

- `apiServer:` The api server to connect to.
- `username:` Username
- `pwd:` password
- `kwargs:` extra arguments for descendents


_returns_: 

### createAsset 

```Python
createAsset(self, device, name, label, description, assetIs, assetType, style='Undefined')
``` 

Create or update the specified asset. Call this function after calling 'connect' for each asset that you want to use.

_parameters:_

- device:


_returns_:
- `name:` the local id of the asset
<type>type name:</type> string or number
- `label:` the label that should be used to show on the website
<type>type label:</type> basestring
- `description:` a description of the asset
<type>type description:</type> basestring
- `assetIs:` actuator, sensor, virtual, config
<type>type assetIs:</type> string
- `assetType:` the type of the asset, possible values: 'integer', 'number', 'boolean', 'text', None (defaults to string, when the asset already exists, the website will not overwrite any changes done manually on the site). Can also be a complete profile definition as a json string (see http://docs.smartliving.io/smartliving-maker/profiles/) example: '{"type": "integer", "minimum": 0}'.
<type>type assetType:</type> string
- `style:` possible values: 'Primary', 'Secondary', 'Config', 'Battery'
<type>type style:</type> basestring 

### doHTTPRequest 

```Python
doHTTPRequest(self, url, content, method='GET')
``` 

send the data and check the result
Some multi threading applications can have issues with the server closing the connection, if this happens
we try again 

### extractHttpCredentials 

```Python
extractHttpCredentials(self, data)
``` 



### getAsset 

```Python
getAsset(self, id=None, gateway=None, device=None, name=None)
``` 

get the details for the specified asset
if gateway and or device is specified, then name has to be used instead of id. 

### getAssetState 

```Python
getAssetState(self, id)
``` 

get the details for the specified asset 

### getAssets 

```Python
getAssets(self, device)
``` 

"get all the assets for a device 

### getDevice 

```Python
getDevice(self, deviceId=None, gatewayId=None, deviceName=None)
``` 

get all the devices related to a ground
either specify deviceId or gatewayId and deviceName 

### getDevices 

```Python
getDevices(self, ground)
``` 

get all the devices related to a ground 

### getGateway 

```Python
getGateway(self, id)
``` 

get the details for the specified gateway 

### getGrounds 

```Python
getGrounds(self, includeShared)
``` 

get all the grounds related to the current account.
<type>type includeShared:</type> bool

_parameters:_

- `includeShared:` when true, shared grounds will also be included 

### getOutPath 

```Python
getOutPath(self, assetId)
``` 

converts the asset id to a path of gateway id /device name / asset name or device id / asset name 

### get_history 

```Python
get_history(self, id, fromTime=None, toTime=None, page=None)
``` 

gets historical, raw data for the specified asset id.

_parameters:_

- `id:` The id of the asset
- `fromTime:` the start time of the data (if none, from start)
- `toTime:` the end time of the data (if none, to end)
- `page:` page number to retrieve (if none, first page)


_returns_: a list of data values 

### pushNotification 

```Python
pushNotification(self, message)
``` 

Send a notification to the account of the user.

_parameters:_

- `message:` the message that should be sent
<type>type message:</type> basestring


_returns_: the result of the request 

### send_command 

```Python
send_command(self, id, value, device=None, gateway=None)
``` 



### send_state 

```Python
send_state(self, id, value, device=None, gateway=None, timestamp=None)
``` 

Send a state value to a sensor

_parameters:_

- `id:` the id or name of the sensor
- `value:`  the value to send
- `device:`  optional device (if id is used as name of the sensor), must be name if gaeway is also specified, otherwise id of device.
- `gateway:` optional id of the gateway.
- `timestamp:` optional timestamp of measurement, when none, current timestamp will be used.


_returns_: 

## att.SubscriberData Objects



### __init__ 

```Python
__init__(self, connection)
``` 

create object
<type>type connection:</type> Client

_parameters:_

- `connection:` the client connection to operate within 

### getTopic 

```Python
getTopic(self, divider=None, wildcard=None, multi_wildcard=None)
``` 

generate topic

_parameters:_

- `desc:` description of the topic to make 
