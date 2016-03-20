__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

import attiotuserclient as iot

_toMonitor = {}

class Composition(object):
    """a composition of an id list and a callback function
    This type of object is returned by the overloaded operators of the Asset object, so that the same objects
     can be overloaded
    """
    def __init__(self, list, condition, left, right):
        self.monitorList = list
        self.condition = condition
        self.left = left
        self.right = right

    def __and__(self, other):
        if isinstance(other, Composition) == True:         # it's a var of another compare
            monitorList = set(self.monitorList)
            monitorList |= other.monitorList
            return Composition(monitorList, andCondCond, self, other)
        elif isinstance(other, Asset):  # monitor on every change
            monitorList = set(self.monitorList).add(other.id)
            return Composition(monitorList, andCondOnEvery, self, other)
        raise Exception("unsupported operation")

def isEqObjects(left, right):
    return left.value == right.value

def isEqObjectVal(left, right):
    return left.value == right

def isGeObjects(left, right):
    return left.value >= right.value

def isGeObjectVal(left, right):
    return left.value >= right

def isGtObjects(left, right):
    return left.value > right.value

def isGtObjectVal(left, right):
    return left.value > right

def isLtObjects(left, right):
    return left.value < right.value

def isLtObjectVal(left, right):
    return left.value < right


def addObjects(left, right):
    return left.value + right.value

def addObjectVal(left, right):
    return left.value + right

def divObjects(left, right):
    return left.value / right.value

def divObjectVal(left, right):
    return left.value / right

def mulObjects(left, right):
    return left.value * right.value

def mulObjectVal(left, right):
    return left.value * right

def subObjects(left, right):
    return left.value - right.value

def subObjectVal(left, right):
    return left.value - right

def andObjectCond(left, right):
    return left.value and right.condition(right.left, right.right)

def andObjectVal(left, right):
    return left.value and right

def andOnEvery(left, right):
    return True

def andCondCond(left, right):
    return left.condition(left.left, left.right) and right.condition(right.left, right.right)

def andCondOnEvery(left, right):
    return left.condition(left.left, left.right)

class Asset(object):
    def __init__(self, id):
        self.id = id

    def __eq__(self, other):
        if isinstance(other, Asset):
            monitorList = set([self.id, other.id])
            isEq = isEqObjects
        else:
            monitorList = set([self.id])
            isEq = isEqObjectVal
        return Composition(monitorList, isEq, self, other)

    def __ge__(self, other):
        if isinstance(other, Asset):
            monitorList = set([self.id, other.id])
            isEq = isGeObjects
        else:
            monitorList = set([self.id])
            isEq = isGeObjectVal
        return Composition(monitorList, isEq, self, other)

    def __add__(self, other):
        if isinstance(other, Asset):
            monitorList = set([self.id, other.id])
            isEq = addObjects
        else:
            monitorList = set([self.id])
            isEq = addObjectVal
        return Composition(monitorList, isEq, self, other)

    def __div__(self, other):
        if isinstance(other, Asset):
            monitorList = set([self.id, other.id])
            isEq = divObjects
        else:
            monitorList = set([self.id])
            isEq = divObjectVal
        return Composition(monitorList, isEq, self, other)

    def __mul__(self, other):
        if isinstance(other, Asset):
            monitorList = set([self.id, other.id])
            isEq = mulObjects
        else:
            monitorList = set([self.id])
            isEq = mulObjectVal
        return Composition(monitorList, isEq, self, other)

    def __sub__(self, other):
        if isinstance(other, Asset):
            monitorList = set([self.id, other.id])
            isEq = subObjects
        else:
            monitorList = set([self.id])
            isEq = subObjectVal
        return Composition(monitorList, isEq, self, other)

    def __gt__(self, other):
        if isinstance(other, Asset):
            monitorList = set([self.id, other.id])
            isEq = isGtObjects
        else:
            monitorList = set([self.id])
            isEq = isGtObjectVal
        return Composition(monitorList, isEq, self, other)

    def __lt__(self, other):
        if isinstance(other, Asset):
            monitorList = set([self.id, other.id])
            isEq = isLtObjects
        else:
            monitorList = set([self.id])
            isEq = isLtObjectVal
        return Composition(monitorList, isEq, self, other)

    def __and__(self, other):
        if isinstance(other, Composition) == True:         # it's a var of another compare
            monitorList = set(other.monitorList).add(self.id)
            doAnd = andObjectCond
        else:
            monitorList = set([self.id, other.id])
            doAnd = andOnEvery
        return Composition(monitorList, doAnd, self, other)


    @property
    def value(self):
        """get the current value of the object"""
        monitor = _toMonitor[self.id]
        if not monitor.value:
            monitor.value = iot.getAssetState(self.id)['state']['value']
        return monitor.value


    @value.setter
    def value(self, value):
        self._setValue(value)

    def _setValue(self, value):
        raise Exception("write value only supported on actuators")



class Sensor(Asset):
    """renaming of the asset class, for mapping with cloud objects"""


class Actuator(Asset):
    """an asset that adds write-value functionality to the object"""

    def _setValue(self, value):
        """send the value to the actuator"""
        iot.send(self.id, value)
