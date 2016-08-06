__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

import logging
import att_event_engine.attiotuserclient as iot
import att_event_engine.resources as resources
import sys

class IotApplication:
    """provides the main entry point for an Iot application"""
    def __init__(self, username, pwd, api, broker):
        """setup app
        Must be done before any rule is declared.
        """
        for arg in sys.argv[1:]:
            parts = arg.split('=')
            if len(parts) != 2:
                logging.error("invalid parameter format: {}".format(parts))
            if not parts[0] in resources.parameters:
                resources.parameters[parts[0]] = parts[1]
            else:
                logging.error("parameter specified multiple times: {}, value: {}".format(parts[0], parts[1]))
        iot.connect(username, pwd, True, api, broker)  # important: do before declaring the rules, otherwise the topics to monitor are not rendered correcly.

    def run(self):
        """the main loop.
        Must be called when all the rules are loaded.
        """
        resources._toMonitor = {}  # small mem optimisation: after all the rules have been loaded, we can clear this cash again, it's no longer needed.
        iot.loop()