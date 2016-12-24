# The att-event-engine module #
This module provides an event driven interface to the AllThingsTalk iot cloud. It allows you to execute functions upon complex conditions which are triggered by events coming from external devices or other resources.

## Overview
The library contains modules that provide the following featues:

- classes that wrap the HTTP and MQTT API's API's. These provide low level functionality like:
	- connecting/disconnecting
	- retrieving & updating assets, devices, gateways,..
	- auto generate topics for publishing and subscribing, based on higher level objects suchs as Assets, Devices, Gateways,.. 
- higher level representation of the data through classes that map to the AllThingsTalk paradigm: assets like Sensor, Actuator, Virtual, Config; Device and Gateway, and also Timer objects.
- The ability to declare mqtt query topics through higher level objects such as Asset-factories (factory.sensor and factory.Actuator)
- a network watchdog
- an application wrapper
- functions and decorators that allow you to register functions and methods as event callbacks. (When)

## installation
- manual: 
	- download package and unzip in directory
	- run `python setup.py install`
- from pip:
	- run `pip install att-event-engine`


## getting started
### application setup
The easiest way to get started is from the template project that is included in the source code (directory 'template'). 


- Just copy this over to a new folder and 
- edit the file 'rules.py'. Here you can specify all your 'when' clauses.
- also edit the file 'credentials.py'. This is where you put your AllThingsTalk account credentials used by the application. 

execute `python main.py` to run the application. 

If your rules contain any 'Parameter' objects, you can specify a value for the parameters at the command prompt in the form of param_name=value. 'main.py' will automatically assign the values to the parameters. 
example: `python main.py myParam=True`
### rules
The template's 'rules.py' contains a small example for a very basic rule:

```python
battery = factory.Sensor(name="battery")


@When([battery], lambda: battery.current.value < 20)
def battery_low():
    battery.connection.pushNotification("battery is low")
```
With this rule, you will receive a push notification whenever a device has an asset named 'battery' who's value drops below 20.

The basic principle behind the 'when' decorator is this:
- In the first parameters, specify a list of asset or timer objects that trigger the evaluation of the rule whenever their value changes.
- The second, optional parameter (a function that returns True or False) specifies the condition upon which the rule should be executed. To put it more exactly: the change of the condition from false to true. This is important, it means that, in the example above, the notification will only be sent 1 time, even though the battery reports 100 times that it is  below 20. As long as it does not go back to above 20, then the rule will not be triggered again. 
If there is no condition, then the rule will be executed for every state update.

Note: the decorator doesn't work on class methods. Use the function when_platform.registerAssetToMonitor instead. You can also use the same method for dynamically adding function callbacks to the event engine.

## status
The library itself is fairly stable, but not all functionality is supported yet by the AllThingsTalk platform, so it's occationally still required to work around issues. This is mostly the case for referencing devices as stand-alone while they are actually attached to gateways. For this reason, this library is still very much an alpha release.  

## api reference
This [doc set](/doc/index.md) has been generated from the source code. 
