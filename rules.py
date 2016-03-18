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


motionHallway = Sensor('56a3ac562fc25c0e68ae7c67')
luxHallway = Sensor('56a516632fc25c0e68ae7cfc')
lightHallway = Actuator('56d30ff1f7bdc10ca85342c3')

iot.connect(credentials.UserName, credentials.Pwd)                  #important: do before declaring the rules, otherwise the topics to monitor are not rendered correcly.

@When((motionHallway == True) & (luxHallway < 150))
def controlHallwayLights():
    lightHallway.value = True


@When(motionHallway == False)
def turnHallwayOff():
    lightHallway.value = False

while True:
    time.sleep(3)