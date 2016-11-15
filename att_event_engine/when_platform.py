__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

#platform specific (server vs user) code for the 'When' functionality

import resources as resources
from timer import Timer
import att

import logging
logger = logging.getLogger('when')

class CallbackObject(object):
    """this object contains"""
    def __init__(self, condition, callback):
        self.conditionValue = None
        self.condition = condition
        self.callback = callback

class MonitorObj(att.SubscriberData):
    """contains all the relevant data for monitoring an asset: it's value + all the callbacks that need to be called
    when the value changes"""
    def __init__(self, connection):
        super(MonitorObj, self).__init__(connection)
        self.callbacks = []
        self.callback = self.onAssetValueChanged

    def onAssetValueChanged(self, value):
        """callback for the processor part: check if the value of an actuator has changed, if so, update the group's value"""
        #global trigger
        if isinstance(value, dict) and "Id" in value:                                       # could come from the timer routine, so first check if it's an asset state change (value is json dict with 'id' in there)
            id = value['Id']
            resources.valueStore[id] = value
            resources.trigger = resources.Asset(id, self.connection)
        elif hasattr(self, 'timer'):
            resources.trigger = self.timer                  # timer is supplied by the register routine, so we have an object to work with.
        else:
            resources.trigger = None
        for callback in self.callbacks:
            try:
                if callback.condition:
                    if callback.condition():
                        if callback.conditionValue != True:
                            callback.conditionValue = True
                            callback.callback()
                    else:
                        callback.conditionValue = False
                else:
                    callback.callback()                                       #it's an 'on every change'
            except:
                logger.exception("'when' callback failed")
        resources.valueStore = {}                                           # reset the value store for the next run, don't buffer values, they can have changed by the next run.


def registerAssetToMonitor(asset, callbackObj):
    """
    registers an asset to be monitored. The callback object that contains the actual callback will be called when a message
    arrives for the asset.
    Use this function to register class methods.
    :param asset: An asset object (sensor/actuator/virtual/config)
    :param callbackObj: a previously created callback object
    :type callbackObj: CallbackObject
    :return: None
    """
    topics = asset.getTopics()
    for topic in topics:
        monitor = MonitorObj(asset.connection)
        monitor.id = topic
        monitor.direction = 'in'
        if isinstance(asset, Timer):
            monitor.level = 'timer'
            monitor.timer = asset  # keep a refernce to the timer inside the callback, so we know which one went off.
        topicStr = monitor.getTopic()
        if topicStr in resources._toMonitor:
            resources._toMonitor[topicStr].callbacks.append(callbackObj)  # we add the callback as a tupple with the condition, saves us a class decleration.
        else:
            monitor.callbacks.append(callbackObj)
            asset.connection.addMessageCallback(topicStr, monitor)
            resources._toMonitor[topicStr] = monitor

def registerMonitor(assets, condition, callback):
    """registers the condition and callback for the specified list of asset id's
    :param assets: list of asset objects to monitor with the same condition
    :param condition: function that evaulaties to true or false. When None, 'True' is always presumed (on every change)
    :param callback: the function to call when the condition evaulates to true after an event was raised for the specified asset.
    """
    if hasattr(callback, '_callbackObj'):
        callbackObj = callback._callbackObj
    else:
        callbackObj = CallbackObject(condition, callback)
        callback._callbackObj = callbackObj
    for asset in assets:
        registerAssetToMonitor(asset, callbackObj)


def appendToMonitorList(callback, toMonitor):
    """
    Adds an element to the list of items that are being monitored for the specified function.
    :param callback: A function that has previously been decorated with a 'When' clause.
    :param toMonitor: a resource to monitor (asset, device, gateway, timer)
    :return: None
    """
    callbackObj = callback._callbackObj
    registerAssetToMonitor(toMonitor, callbackObj)

def removeFromMonitorList(callback, toRemove):
    """
    removes an element from the list of itmes that are being monitored for the specified function.
    :param callback: function that serves as callback.
    :param toRemove:
    :return:
    """
    callbackObj = callback._callbackObj
    topics = toRemove.getTopics()
    for topic in topics:
        monitor = MonitorObj(toRemove.connection)
        monitor.id = topic
        monitor.direction = 'in'
        if isinstance(toRemove, Timer):
            monitor.level = 'timer'
        topicStr = monitor.getTopic()
        if topicStr in resources._toMonitor:
            resources._toMonitor[topicStr].callbacks.remove(callbackObj)
            if len(resources._toMonitor[topicStr].callbacks) == 0:
                resources._toMonitor.pop(topicStr)
                toRemove.connection.removeMessageCallback(topicStr)