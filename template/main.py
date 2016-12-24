__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

import logging
logging.getLogger().setLevel(logging.INFO)

import att_event_engine.att as att
import credentials
import att_event_engine.resources as resources
import sys
from att_event_engine.nw_watchdog import Nw_Watchdog

iot = att.Client()
iot.connect(credentials.UserName, credentials.Pwd, True, credentials.Api, credentials.Broker)                  #important: do before declaring the rules, otherwise the topics to monitor are not rendered correcly.
resources.defaultconnection = iot
watchdog = Nw_Watchdog(iot, "watchdogDevice", "name of this application")

for arg in sys.argv[1:]:
    parts = arg.split('=')
    if len(parts) != 2:
        logging.error("invalid parameter format: {}".format(parts))
    if not parts[0] in resources.parameters:
        resources.parameters[parts[0]] = parts[1]
    else:
        logging.error("parameter specified multiple times: {}, value: {}".format(parts[0], parts[1]))

import rules
resources._toMonitor = {}               # small mem optimisation: after all the rules have been loaded, we can clear this cash again, it's no longer needed.
watchdog.start()
try:
    iot.loop()
finally:
    watchdog.stop()
