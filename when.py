__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"


import resources
import attiotuserclient as iot

class MonitorObj(object):
    """contains all the relevant data for monitoring an asset: it's value + all the callbacks that need to be called
    when the value changes"""
    def __init__(self):
        self.toMonitor = []
        self.value = None

    def onAssetValueChanged(self, value):
        """callback for the processor part: check if the value of an actuator has changed, if so, update the group's value"""
        if 'Value' in value:
            self.value = value['Value']
        else:
            self.value = value['value']
        for callback in self.toMonitor:
            composition = callback[0]
            if composition:
                if composition.condition(composition.left, composition.right):
                    callback[1]()
            else:
                callback[1]()                                       #it's an 'on every change'


def registerMonitor(idList, condition, callback):
    """registers the condition and callback for the specified list of asset id's
    :param idList: list of strings, each string is the id of an asset to monitor
    :param condition: function that evaulaties to true or false. When None, 'True' is always presumed (on every change)
    :param callback: the function to call when the condition evaulates to true after an event was raised for the specified asset.
    """
    for id in idList:
        if id in resources._toMonitor:
            resources._toMonitor[id].toMonitor.append((condition, callback))        # we add the callback as a tupple with the condition, saves us a class decleration.
        else:
            callbackObj = MonitorObj()
            callbackObj.toMonitor.append((condition, callback))
            iot.subscribe(id, callbackObj.onAssetValueChanged)
            resources._toMonitor[id] = callbackObj

def When(condition):
    """decorates a function so that it is called when the condition is met. This condition
     has to contain (a) reference(s) to Asset objects"""
    def when_decorator(func):
        '''called when the expresion needs to be evaulated=the callback'''
        if isinstance(condition, resources.Asset):    # user requested to monitor every change of an asset.
            registerMonitor([condition.id], None, func)
        elif isinstance(condition, resources.Composition):
            registerMonitor(condition.monitorList, condition, func)
        return func                                         # the original function remains unchanged, we just needed to have a pointer to the function and build the conditions.
    return when_decorator
