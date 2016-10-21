__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2015, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

import paho.mqtt.client as mqtt
import logging
import json
import httplib                                 # for http comm
import urllib                                   # for http params
import time
from socket import error as SocketError         # for http error handling
import errno

_mqttClient = None
_mqttConnected = False
_httpClient = None
_callbacks = {}
_get_assets_callback = None

_curHttpServer = None
_access_token = None
_refresh_token = None
_expires_in = None
_clientId = None
_brokerUser = None
_brokerPwd = None
_isLoggedIn = False                                     # keeps track if user is logged in or not, so we can show the correct errors.

_defaultDivider = '/'
_defaultWildCard = '+'
_defaultMultiWildCard = '#'


class SubscriberData(object):
    """
    id: dictionary of fields: gateway, device, asset  -> name or id
    callback: function to call when data arrived.
    direction: 'in' (from cloud to client) or 'out' (from device to cloud)
    toMonitor: 'state': changes in the value of the asset, 'command' actuator commands, 'events': device/asset/... creaated, deleted,..
    level: 'asset', 'device', 'gateway', 'ground' # 'all device-assets', 'all gateway-assets', 'all gateway-devices', 'all gateway-device-assets'
    """
    def __init__(self):
        self.id = None
        self.callback = None
        self.direction = 'in'
        self.toMonitor = 'state'
        self.level = 'asset'

    def getTopic(self, divider=_defaultDivider, wildcard=_defaultWildCard, multi_wildcard=_defaultMultiWildCard):
        """
        generate topic
        :param desc: description of the topic to make
        """
        def getId(name):
            """get the value for the id field, converting wildcards where needed"""
            val = self.id[name]
            if val in ['+', '*']:
                return wildcard
            elif val == '#':
                return multi_wildcard
            else:
                return val

        if self.level == 'asset':
            if isinstance(self.id, dict):
                if 'gateway' in self.id:
                    if 'device' in self.id:
                        return "client{0}{1}{0}{2}{0}gateway{0}{3}{0}device{0}{4}{0}asset{0}{5}{0}{6}".format(divider, _clientId, self.direction, getId('gateway'), getId('device'), getId('asset'), self.toMonitor)
                        # return "client/" + str(_clientId) + "/" + self.direction + "/gateway/" + self.id['gateway'] + "/device/" + self.id['device'] + "/asset/" + self.id['asset'] + "/" + self.toMonitor
                    else:
                        return "client{0}{1}{0}{2}{0}gateway{0}{3}{0}asset{0}{4}{0}{5}".format(divider,_clientId,self.direction,getId('gateway'),getId('asset'),self.toMonitor)
                        #return str("client/" + _clientId + "/" + self.direction + "/gateway/" + self.id['gateway'] + "/asset/" + self.id['asset'] + "/" + self.toMonitor)
                elif 'device' in self.id:
                    return "client{0}{1}{0}{2}{0}device{0}{3}{0}asset{0}{4}{0}{5}".format(divider,_clientId,self.direction,getId('device'),getId('asset'),self.toMonitor)
                    #return str("client/" + _clientId + "/" + self.direction + "/device/" + self.id['device'] + "/asset/" +self.id['asset'] + "/" + self.toMonitor)
                else:
                    return "client{0}{1}{0}{2}{0}asset{0}{3}{0}{4}".format(divider, _clientId, self.direction, getId('asset'), self.toMonitor)
            else:
                return "client{0}{1}{0}{2}{0}asset{0}{3}{0}{4}".format(divider, _clientId,self.direction,self.id, self.toMonitor)
                #return str("client/" + _clientId + "/" + self.direction + "/asset/" + self.id + "/" + self.toMonitor)  # asset is usually a unicode string, mqtt trips over this.
        elif self.level == 'timer':
            return "{1}{0}timer{0}{2}".format(divider, self.id['context'], self.id['name'])
        elif self.level == "device":
            if 'gateway' in self.id:
                return "client{0}{1}{0}{2}{0}gateway{0}{3}{0}device{0}{4}{0}{5}".format(divider, _clientId, self.direction, getId('gateway'), getId('device'), self.toMonitor)
            else:
                return "client{0}{1}{0}{2}{0}device{0}{3}{0}{4}".format(divider, _clientId, self.direction, getId('device'), self.toMonitor)
        # todo: add topic renderers for different type of topics.
        raise NotImplementedError()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    global _mqttConnected
    try:
        if rc == 0:
            _mqttConnected = True
            logging.info("Connected to mqtt broker with result code "+str(rc))
            if _callbacks:
                for topic, definitions in _callbacks.iteritems():
                    _subscribe(topic)
                    for definition in definitions:
                        # note: if definition.id is a string, then it points to a single asset, otherwise it's a path, that we can't
                        if isinstance(definition.id, basestring) and definition.level == 'asset' and definition.direction == 'in' and definition.toMonitor == 'state':    # refresh the state of all assets being monitored when reconnecting. Other events can't be refreshed.
                            curVal = getAssetState(definition.id)
                            if curVal:
                                definition.callback(curVal)
        else:
            logging.error("Failed to connect to mqtt broker: " + mqtt.connack_string(rc))
    except Exception:
        logging.exception("failed to connect")


# The callback for when a PUBLISH message is received from the server.
def on_MQTTmessage(client, userdata, msg):
    global _lastMessage
    try:
        if msg.topic in _callbacks:
            topicParts = msg.topic.split('/')
            logging.info(str(topicParts))
            if topicParts[2] == 'in':                   # data from cloud to client is always json, from device to cloud is not garanteed to be json.
                value = json.loads(msg.payload)
            else:
                value = msg.payload
            defs = _callbacks[msg.topic]
            for definition in defs:
                definition.callback(value)
    except Exception as e:
        if msg.payload:
            logging.exception("failed to process incomming message" + str(msg.payload))
        else:
            logging.exception("failed to process incomming message")

def on_MQTTSubscribed(client, userdata, mid, granted_qos):
    logging.info("Subscribed to topic, receiving data from the cloud: qos=" + str(granted_qos))

def connect(username, pwd, blocking = False, httpServer="api.smartliving.io", mqttServer="broker.smartliving.io"):
    '''start the mqtt client and make certain that it can receive data from the IOT platform
	   mqttServer: (optional): the address of the mqtt server. Only supply this value if you want to a none standard server.
	   port: (optional) the port number to communicate on with the mqtt server.
    '''
    global _brokerPwd, _brokerUser
    mqttCredentials = connectHttp(username, pwd, httpServer)
    if not "rmq:clientId" in mqttCredentials:
        logging.error("username not specified, can't connect to broker")
        raise Exception("username not specified, can't connect to broker")
    _brokerUser = mqttCredentials["rmq:clientId"] + ":" + mqttCredentials["rmq:clientId"]
    _brokerPwd = mqttCredentials["rmq:clientKey"]

    _subscribe_mqtt(mqttServer, blocking)

def reconnect(httpServer, mqttServer):
    global _httpClient, _curHttpServer
    _httpClient = httplib.HTTPConnection(httpServer)
    _curHttpServer = httpServer             #so we can reconnect if needed
    _subscribe_mqtt(mqttServer)             #subscrriptions will be made after the connection is established

def disconnect(resumable = False):
    """close all connections to the cloud and reset the module
    if resumable is True, then only the network connections get closed, but the connection data remains, so that
    you can restart connections using the reconnect features.
    """
    global  _access_token, _refresh_token, _expires_in, _mqttClient, _httpClient, _mqttConnected, _callbacks, _brokerPwd, _brokerUser, _isLoggedIn
    if not resumable:
        _isLoggedIn = False
        _access_token = None
        _refresh_token = None
        _expires_in = None
        for topic, callback in _callbacks.iteritems():
            _unsubscribe(topic)
        _callbacks = {}
        _brokerPwd = None
        _brokerUser = None
    if _mqttClient:
        _mqttClient.disconnect()
        _mqttClient = None
    _mqttConnected = False
    if _httpClient:
        _httpClient.close()
    _httpClient = None

def subscribe(asset, callback):
    """monitor for changes for that asset. For more monitor features, use 'subscribeAdv'
    :type callback: function, format: callback(json_object)
    :param callback: a function that will be called when a value arrives for the specified asset.
    :type asset: string
    :param asset: the id of the assset to monitor
    """
    data = SubscriberData()
    data.id = asset
    data.callback = callback
    topic = data.getTopic()
    if topic in _callbacks:
        _callbacks[topic].append(data)
    else:
        _callbacks[topic] = [data]
    if _mqttClient and _mqttConnected == True:
        _subscribe(topic)

def subscribeAdv(subscriberData, topic=None):
    """subscribe to topics with advanced parameter options
    If the topic is not provided, it is calculated from the subscriberData.
    This is for apps that also calculate the topic string, so that this isn't done unnecessarily
    """
    if not topic:
        topic = subscriberData.getTopic()
    if topic in _callbacks:
        _callbacks[topic].append(subscriberData)
    else:
        _callbacks[topic] = [subscriberData]
    if _mqttClient and _mqttConnected == True:
        _subscribe(topic)

def addMessageCallback(topic, monitor):
    _subscribe(topic)
    if topic in _callbacks:
        raise Exception("topic already registered")
    else:
        _callbacks[topic] = [monitor]
    _mqttClient.message_callback_add(topic, lambda client, userdata, msg: monitor.onAssetValueChanged(json.loads(msg.payload)))

def unsubscribe(id, level = 'asset'):
    """
    remove all the callbacks for the specified id.
    :param level: which type of item: asset, device, gateway
    :param id: the id of the item (asset, device, gateway,..) to remove
    """
    desc = SubscriberData()
    desc.id = id
    desc.level = level
    for direction in ['in', 'out']:
        desc.direction = direction
        for toMonitor in ['state', 'event', 'command']:
            desc.toMonitor = toMonitor
            topic = desc.getTopic()
            if topic in _callbacks:
                _callbacks.pop(topic)
                if _mqttClient and _mqttConnected == True:
                    _unsubscribe(topic)


def getOutPath(assetId):
    """converts the asset id to a path of gateway id /device name / asset name or device id / asset name"""
    result = {}
    asset = getAsset(assetId)
    result['asset'] = asset['name']
    device = getDevice(asset['deviceId'])
    if device:
        if 'gatewayId' in device and device['gatewayId']:
            result['device'] = device['name']
            result['gateway'] = device['gatewayId']
        else:
            result['device'] = device['id']
    else:
        gateway = getGateway(asset['deviceId'])
        if gateway:
            result['gateway'] = gateway['id']
        else:
            raise Exception("asset does not belong to a device or gateway")
    return result

def _subscribe(topic):
    """
        internal subscribe routine
    :param desc: description of the subscription to make
    """
    logging.info("subscribing to: " + topic)
    result = _mqttClient.subscribe(topic)                                                    #Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    logging.info(str(result))

def _unsubscribe(topic):
    logging.info("unsubscribing to: " + topic)
    result = _mqttClient.unsubscribe(topic)                                                    #Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    logging.info(str(result))

def _subscribe_mqtt(broker, blocking):
    global _mqttClient                                             # we assign to these vars first, so we need to make certain that they are declared as global, otherwise we create new local vars
    if _brokerPwd and _brokerUser:
        if _mqttClient:
            _mqttClient.disconnect()
        _mqttClient = mqtt.Client()
        _mqttClient.on_connect = on_connect
        _mqttClient.on_message = on_MQTTmessage
        _mqttClient.on_subscribe = on_MQTTSubscribed
        _mqttClient.username_pw_set(_brokerUser, _brokerPwd)

        _mqttClient.connect(broker, 1883, 60)
        if not blocking:
            _mqttClient.loop_start()
        else:
            _mqttClient.reconnect();
    else:
        raise Exception("no mqtt credentials found")


def loop():
    """in case that the connect was called in a blocking manner, then this has to be called to start the main mqtt loop"""
    _mqttClient.loop_forever()

def extractHttpCredentials(data):
    global _access_token, _refresh_token, _expires_in, _clientId
    if data:
        _access_token = str(data['access_token'])
        _refresh_token = str(data['refresh_token'])
        _expires_in = time.time() + data['expires_in']
        _clientId = str(data['rmq:clientId'])
    else:
        _access_token = None
        _refresh_token = None
        _expires_in = None
        _clientId = None

def connectHttp(username, pwd, httpServer):
    global _httpClient, _curHttpServer
    _curHttpServer = httpServer
    _httpClient = httplib.HTTPConnection(httpServer)
    loginRes = login(username, pwd)
    extractHttpCredentials(loginRes)
    return loginRes

def login(username, pwd):
    global _isLoggedIn
    url = "/login"
    body = "grant_type=password&username=" + username + "&password=" + pwd + "&client_id=maker"
    logging.info("HTTP POST: " + url)
    logging.info("HTTP BODY: " + body)
    _httpClient.request("POST", url, body, {"Content-type": "application/json", "Connection:": "Keep-alive"})
    response = _httpClient.getresponse()
    logging.info(str((response.status, response.reason)))
    jsonStr =  response.read()
    logging.info(jsonStr)
    if response.status == 200:
        _isLoggedIn = True
        return json.loads(jsonStr)
    else:
        _processError(jsonStr)

def _processError(str):
    obj = json.loads(str)
    if obj:
        if 'error_description' in obj:
            raise Exception(obj['error_description'])
        elif 'message' in obj:
            raise Exception(obj['message'])
    raise Exception(str)

def refreshToken():
    """no need for error handling, is called within doHTTPRequest, which does the error handling"""
    global _access_token, _refresh_token
    url = "/login"
    body = "grant_type=refresh_token&refresh_token=" + _refresh_token + "&client_id=dashboard"
    logging.info("HTTP POST: " + url)
    logging.info("HTTP BODY: " + body)
    _httpClient.request("POST", url, body, {"Content-type": "application/json", "Connection:" : "Keep-alive"})
    response = _httpClient.getresponse()
    logging.info(str((response.status, response.reason)))
    jsonStr =  response.read()
    logging.info(jsonStr)
    if response.status == 200:
        loginRes = json.loads(jsonStr)
    else:
        loginRes = None
    extractHttpCredentials(loginRes)

def getAsset(id=None, gateway=None, device=None, name=None):
    """get the details for the specified asset
    if gateway and or device is specified, then name has to be used instead of id.
    """
    if id:
        url = "/asset/" + id
    elif gateway:
        url = "/gateway/" + gateway
        if device:
            url += "/device/" + device
        url += "/asset/" + name
    elif device:
        url = "/device/" + device + "/asset/" + name
    else:
        raise Exception("either assetId, (deviceId and asset name) or (gatewayid, deviceName and name) have to be specified")
    return doHTTPRequest(url, "")


def createAsset(device, name, description, assetIs, assetType, style="Undefined"):
    '''Create or update the specified asset. Call this function after calling 'connect' for each asset that you want to use.
    :param name: the local id of the asset
    :type name: string or number
    :param label: the label that should be used to show on the website
    :type label: basestring
    :param description: a description of the asset
    :type description: basestring
    :param assetIs: actuator, sensor, virtual, config
    :type assetIs: string
    :param assetType: the type of the asset, possible values: 'integer', 'number', 'boolean', 'text', None (defaults to string, when the asset already exists, the website will not overwrite any changes done manually on the site). Can also be a complete profile definition as a json string (see http://docs.smartliving.io/smartliving-maker/profiles/) example: '{"type": "integer", "minimum": 0}'.
    :type assetType: string
    :param style: possible values: 'Primary', 'Secondary', 'Config', 'Battery'
    :type style: basestring
    '''

    if not device:
        raise Exception("device not specified")
    name = str(name)
    body = {'title': name, "description": description, "style": style, "is": assetIs, "deviceId": device}
    if assetType:
        if isinstance(assetType, dict):
            body["profile"] = assetType
        else:
            body["profile"] = {"type": str(assetType)}
    url = "/device/" + device + "/asset/" + name

    return doHTTPRequest(url, json.dumps(body), 'PUT')



def getAssetState(id):
    """get the details for the specified asset"""
    url = "/asset/" + id + '/state'
    result = doHTTPRequest(url, "")
    if result and 'state' in result:
        result = result['state']
    return result

def getGateway(id):
    """get the details for the specified gateway"""
    url = "/gateway/" + id
    return doHTTPRequest(url, "")

def getGrounds(includeShared):
    """get all the grounds related to the current account.
    :type includeShared: bool
    :param includeShared: when true, shared grounds will also be included
    """
    url = "/me/grounds"
    if includeShared:
        url += '?' + urllib.urlencode({'type': "shared"})
    result = doHTTPRequest(url, "")
    if result:
        return result['items']

def getDevices(ground):
    """get all the devices related to a ground"""
    url = "/ground/" + ground + "/devices"
    result = doHTTPRequest(url, "")
    if result:
        return result['items']

def getDevice(deviceId=None, gatewayId=None, deviceName=None):
    """get all the devices related to a ground
    either specify deviceId or gatewayId and deviceName
    """
    if deviceId:
        url = "/device/" + deviceId
    elif gatewayId and deviceName:
        url = "/gateway/" + gatewayId + "/device/" + deviceName
    else:
        raise Exception("either deviceId or gatewayid and deviceName have to be specified")
    return doHTTPRequest(url, "")

def getAssets(device):
    """"get all the assets for a device"""
    url = "/device/" + device
    result = doHTTPRequest(url, "")
    if result:
        return result['assets']

def pushNotification(message):
    """
    Send a notification to the account of the user.
    :param message: the message that should be sent
    :type message: basestring
    :return: the result of the request
    """
    url = "/service/push/notifications"
    content = {'message': message}
    return doHTTPRequest(url, json.dumps(content), 'POST')

def _reconnectAfterSendData():
    try:
        global _httpClient
        _httpClient.close()
        _httpClient = httplib.HTTPConnection(_curHttpServer)  # recreate the connection when something went wrong. if we don't do this and an error occured, consecutive requests will also fail.
    except:
        logging.exception("reconnect failed after _sendData produced an error")

def doHTTPRequest(url, content, method = "GET"):
    """send the data and check the result
        Some multi threading applications can have issues with the server closing the connection, if this happens
        we try again
    """
    if _isLoggedIn:
        success = False
        badStatusLineCount = 0                              # keep track of the amount of 'badStatusLine' exceptions we received. If too many raise to caller, otherwise retry.
        while not success:
            try:
                if _expires_in < time.time():               #need to refesh the token first
                    refreshToken()
                headers = {"Content-type": "application/json", "Authorization": "Bearer " + _access_token, "Connection:" : "Keep-alive"}
                logging.info("HTTP " + method + ': ' + url)
                logging.info("HTTP HEADER: " + str(headers))
                logging.info("HTTP BODY: " + content)
                _httpClient.request(method, url, content, headers)
                response = _httpClient.getresponse()
                logging.info(str((response.status, response.reason)))
                jsonStr =  response.read()
                logging.info(jsonStr)
                if response.status == 200:
                    if jsonStr: return json.loads(jsonStr)
                    else: return                                                    # get out of the ethernal loop
                elif not response.status == 200:
                    _processError(jsonStr)
            except httplib.BadStatusLine:                   # a bad status line is probably due to the connection being closed. If it persists, raise the exception.
                badStatusLineCount += 1
                if badStatusLineCount < 10:
                    _reconnectAfterSendData()
                else:
                    raise
            except (SocketError) as e:
                _reconnectAfterSendData()
                if e.errno != errno.ECONNRESET:             # if it's error 104 (connection reset), then we try to resend it, cause we just reconnected
                    raise
            except:
                _reconnectAfterSendData()
                raise
    else:
        raise Exception("Not logged in: please check your credentials")

def send(id, value, device=None, gateway=None):
    body = {"value": value }
    body = json.dumps(body)

    url = ""
    if gateway:
        url = '/gateway/' + gateway
    if device:
        url += '/device/' + device
    url += "/asset/" +  id + "/command"

    result = doHTTPRequest(url, body, "PUT")