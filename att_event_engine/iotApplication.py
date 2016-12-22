__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

import logging
import att
import att_event_engine.resources as resources
import sys

class IotApplication:
    """provides the main entry point for an Iot application"""
    def __init__(self, username, pwd, api, broker, appName):
        """setup app
        Must be done before any rule is declared.
        """

        self.att = att.Client()
        resources.defaultconnection = self.att
        self.att.connect(username, pwd, True, api, broker, client=appName)  # important: do before declaring the rules, otherwise the topics to monitor are not rendered correcly.

        for arg in sys.argv[1:]:
            parts = arg.split('=')
            if len(parts) != 2:
                logging.error("invalid parameter format: {}".format(parts))
            if not parts[0] in resources.parameters:
                resources.parameters[parts[0]] = parts[1]
            else:
                logging.error("parameter specified multiple times: {}, value: {}".format(parts[0], parts[1]))

    def run(self):
        """the main loop.
        Must be called when all the rules are loaded.
        """
        resources._toMonitor = {}  # small mem optimisation: after all the rules have been loaded, we can clear this cash again, it's no longer needed.
        self.att.loop()