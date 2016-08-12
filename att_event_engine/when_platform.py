__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

#platform specific (server vs user) code for the 'When' functionality

import resources as resources
from timer import Timer
import attiotuserclient as iot

import logging
logger = logging.getLogger('when')

class CallbackObject(object):
    """this object contains"""
    def __init__(self, condition, callback):
        self.conditionValue = None
        self.condition = condition
        self.callback = callback

class MonitorObj(iot.SubscriberData):
    """contains all the relevant data for monitoring an asset: it's value + all the callbacks that need to be called
    when the value changes"""
    def __init__(self):
        super(MonitorObj, self).__init__()
        self.callbacks = []
        self.callback = self.onAssetValueChanged

    def onAssetValueChanged(self, value):
        """callback for the processor part: check if the value of an actuator has changed, if so, update the group's value"""
        #global trigger
        if isinstance(value, dict) and "Id" in value:                                       # could come from the timer routine
            id = value['Id']
            resources.valueStore[id] = value['Value']
            resources.trigger = resources.Asset(id)
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


def registerMonitor(assets, condition, callback):
    """registers the condition and callback for the specified list of asset id's
    :param assets: list of asset objects to monitor with the same condition
    :param condition: function that evaulaties to true or false. When None, 'True' is always presumed (on every change)
    :param callback: the function to call when the condition evaulates to true after an event was raised for the specified asset.
    """
    callbackObj = CallbackObject(condition, callback)
    for asset in assets:
        topics = asset.getTopics()
        for topic in topics:
            monitor = MonitorObj()
            monitor.id = topic
            monitor.direction = 'in'
            if isinstance(asset, Timer):
                monitor.level = 'timer'
            topicStr = monitor.getTopic()
            if topicStr in resources._toMonitor:
                resources._toMonitor[topicStr].callbacks.append(callbackObj)  # we add the callback as a tupple with the condition, saves us a class decleration.
            else:
                monitor.callbacks.append(callbackObj)
                iot.addMessageCallback(topicStr, monitor)
                resources._toMonitor[topicStr] = monitor
