__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

import when_platform as whenCore

import logging
logger = logging.getLogger('when')




def When(toMonitor, condition = None):
    """decorates a function so that it will be triggered when an event arrived for an item in the toMonitor list.
    If there is a condition specified (lambda expression or function), it must evaluate to true for the function to be triggered."""
    def when_decorator(func):
        '''called when the expresion needs to be evaulated=the callback'''
        whenCore.registerMonitor(toMonitor, condition, func)
        return func                                         # the original function remains unchanged, we just needed to have a pointer to the function and build the conditions.
    return when_decorator
