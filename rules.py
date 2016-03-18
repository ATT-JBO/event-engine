__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

import time

from when import *
from resources import Sensor, Actuator
import attiotuserclient as iot
import credentials


motionHallway = Sensor('id')
luxHallway = Sensor('id')
lightHallway = Actuator('id')

iot.connect(credentials.UserName, credentials.Pwd)                  #important: do before declaring the rules, otherwise the topics to monitor are not rendered correcly.

@When((motionHallway == True) & (luxHallway < 150))
def controlHallwayLights():
    lightHallway.value = True


@When(motionHallway == False)
def turnHallwayOff():
    lightHallway.value = False

while True:
    time.sleep(3)