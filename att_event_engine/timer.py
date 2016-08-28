__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"


import errno
import httplib
from socket import error as SocketError
import attiotuserclient as iot
import resources
import json

class Timer(object):
    """provides access to a global cloud based timer iot-service"""

    def __init__(self, context, name):
        """
        Create a new timer object
        :param runAt: initial time out to run the timer at, when it is first created/setup
        :param context: the resource object in which context that the timer is activated
        :param name: the name of the timer, has to be unique within the specified context.
        """
        self.context = context
        self.name = name

    def getTopics(self, divider=iot._defaultDivider, wildcard=iot._defaultWildCard):
        if not self.context:
            return [{'name': self.name}]
        else:
            contextTopics = self.context.getTopics()
            monitor = iot.SubscriberData()
            monitor.direction = 'in'
            if not isinstance(self.context, resources.Asset):           # if it's not an asset, but a device or gateway, assign to correct level to the topic builder
                monitor.level = type(self.context).__name__.lower()
            result = []
            for topic in contextTopics:
                monitor.id = contextTopics[0]
                result.append({'name': self.name, 'context': monitor.getTopic(divider=divider, wildcard=wildcard)})        # for the timer app, always use amqp notation
            return result

    def getTopicStr(self):
        """renders 1 or more topic strings for the current object. Always returns a list"""
        result = []
        monitor = iot.SubscriberData()
        monitor.level = 'timer'
        for topic in self.getTopics(divider='.', wildcard='*'):
            monitor.id = topic
            result.append(monitor.getTopic(divider='.', wildcard='*'))             # for the timer app, always use amqp notation
        return result

    def set(self, delay):
        """
        start the timer and let it go off in 'value' amount of seconds.
        If the timer was already running, it will be restarted.
        :param delay:
        :return:
        """
        success = False
        badStatusLineCount = 0  # keep track of the amount of 'badStatusLine' exceptions we received. If too many raise to caller, otherwise retry.
        while not success:
            try:
                method = 'PUT'
                url= '/add'
                content = {'trigger type': 'date', 'duration': delay, 'callback': self.getTopicStr()[0]}
                content = json.dumps(content)
                print("HTTP " + method + ': ' + url)
                print("HTTP BODY: " + content)
                _httpClient = httplib.HTTPConnection("localhost:2000")
                _httpClient.request(method, url, content)
                response = _httpClient.getresponse()
                print(str((response.status, response.reason)))
                responseStr = response.read()
                print(responseStr)
                return response.status == 200
            except httplib.BadStatusLine:  # a bad status line is probably due to the connection being closed. If it persists, raise the exception.
                badStatusLineCount += 1
                if badStatusLineCount >= 10:
                    raise
            except (SocketError) as e:
                if e.errno != errno.ECONNRESET:  # if it's error 104 (connection reset), then we try to resend it, cause we just reconnected
                    raise

    @property
    def id(self):
        if self.context:
            return "{0}_timer_{1}".format(self.context.id, self.name)
        else:
            return "timer_{0}".format(self.name)


    @staticmethod
    def current():
        """
        get the timer that triggered the current activity
        :return:
        """
        return resources.trigger