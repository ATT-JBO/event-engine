
# when_platform Module


## Functions

### appendToMonitorList 

```Python
appendToMonitorList(callback, toMonitor)
``` 

Adds an element to the list of items that are being monitored for the specified function.

_parameters:_

- `callback:` A function that has previously been decorated with a 'When' clause.
- `toMonitor:` a resource to monitor (asset, device, gateway, timer)


_returns_: None 

### registerAssetToMonitor 

```Python
registerAssetToMonitor(asset, callbackObj)
``` 

registers an asset to be monitored. The callback object that contains the actual callback will be called when a message
arrives for the asset.
Use this function to register class methods.

_parameters:_

- `asset:` An asset object (sensor/actuator/virtual/config)
- `callbackObj:` a previously created callback object
<type>type callbackObj:</type> CallbackObject


_returns_: None 

### registerMonitor 

```Python
registerMonitor(assets, condition, callback)
``` 

registers the condition and callback for the specified list of asset id's

_parameters:_

- `assets:` list of asset objects to monitor with the same condition
- `condition:` function that evaulaties to true or false. When None, 'True' is always presumed (on every change)
- `callback:` the function to call when the condition evaulates to true after an event was raised for the specified asset. 

### removeFromMonitorList 

```Python
removeFromMonitorList(callback, toRemove)
``` 

removes an element from the list of itmes that are being monitored for the specified function.

_parameters:_

- `callback:` function that serves as callback.
- toRemove:


_returns_: 

## when_platform.CallbackObject Objects



### __init__ 

```Python
__init__(self, condition, callback)
``` 



## when_platform.MonitorObj Objects



### __init__ 

```Python
__init__(self, connection)
``` 



### onAssetValueChanged 

```Python
onAssetValueChanged(self, value)
``` 

callback for the processor part: check if the value of an actuator has changed, if so, update the group's value 
