__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"


#   Copyright 2014-2016 AllThingsTalk
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

import datetime
import logging
logger = logging.getLogger('watchdog')
import threading
from time import sleep
from att_event_engine.att import SubscriberData

_PINGFREQUENCY = 120            # every 2 minutes.

class Nw_Watchdog(threading.Thread):
    """
    allows you to add a watchdog an application to make certain that the mqtt connection remains open.
    """
    def __init__(self, client, device, assetName, on_failure):

        """
        create watchdog
        :param client: The att_event_engine.Client object that provides a connection to the cloud.
        :param device: The name of the device that represents the watchdog.
        :param on_failure: a callback function: def on_failure(), called when the self-ping fails.
        :param assetName:  name of the asset that represents the watchdog-pin.
        """
        threading.Thread.__init__(self)
        self.on_failure = on_failure
        self.watchdog_asset_id = assetName    #the asset id used by the watchdog. Change this if it interfers with your own asset id's.
        self.PingFrequency = _PINGFREQUENCY    #the frequency in seconds, that a ping is sent out (and that the system expects a ping back)

        self._nextPingAt = None      # the moment in time that the next ping should be sent.
        self._pingCounter = 0        # the count of the ping, increments every time a ping is sent.
        self._lastReceived = 0       # the ping counter that was last received.
        self._device = device
        self._client = client
        data = SubscriberData(self)
        data.id = {"device": self._device, "asset": str(self.watchdog_asset_id)}
        data.callback = self.on_ping_received
        data.toMonitor = 'command'
        data.connection = self._client
        self._client.subscribeAdv(data)

    def ping(self):
        """send a ping to the server"""
        self._pingCounter += 1                      # increment counter here so that you can call ping as many times as you want.
        self._nextPingAt = datetime.datetime.now() + datetime.timedelta(0, self.PingFrequency)
        self._client.send_command_mqtt(self.watchdog_asset_id, self._pingCounter, self._device)

    def checkPing(self):
        """check if we need to resend a ping and if we received the previous ping in time"""
        if self._nextPingAt <= datetime.datetime.now():
            if self._lastReceived != self._pingCounter:
                logger.error("ping didn't arrive in time, resetting connection")
                if self.on_failure:
                    self.on_failure()
                return False
            else:
                self.ping()

        return True

    def on_ping_received(self, value):
        """check if an incomming command was a ping from the watchdog
        :returns: if the id was that of the watchdog.
        :rtype: bool
        """
        self._lastReceived = long(value)
        logger.info("received ping: " + str(self._lastReceived))

    def stop(self):
        """
        stop the thread.
        :return:
        """
        self._is_running = False

    def run(self):
        """
        start the watchdog.
        :return:
        """
        try:
            while self._client.is_connected_mqtt == False:      # we need an mqtt connection before we can begin.
                sleep(self.PingFrequency / 3)

            self._is_running = True
            self.ping()
            while self._is_running:
                sleep(self.PingFrequency / 3)
                self._is_running = self.checkPing()
        except Exception as e:
            logger.exception("fatal failure in watchdog")




