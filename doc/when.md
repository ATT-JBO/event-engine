
# when Module


## Functions

### When 

```Python
When(toMonitor, condition=None)
``` 

decorates a function so that it will be triggered when an event arrived for an item in the toMonitor list.
If there is a condition specified (lambda expression or function), it must evaluate to true for the function to be triggered. 

### appendToMonitorList 

```Python
appendToMonitorList(func, toMonitor)
``` 

Adds an element to the list of items that are being monitored for the specified function.

_parameters:_

- `func:` A function that has previously been decorated with a 'When' clause.
- `toMonitor:` a resource to monitor (asset, device, gateway, timer)


_returns_: None 
