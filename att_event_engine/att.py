__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"

import logging
import json
import httplib                                 # for http comm
import urllib                                   # for http params
import time
from socket import error as SocketError         # for http error handling
import errno
import datetime
import paho.mqtt.client as mqtt
import types as types                          # to check on type info


class HttpClient(object):
    """base object for clients
    Describes the public interface.
    """

    def __init__(self):
        """
        create the object
        """
        self._httpClient = None
        self._curHttpServer = None
        self._isLoggedIn = False
        self._access_token = None
        self._refresh_token = None
        self._expires_in = None
        self._clientId = None


    def connect_api(self, username, pwd, apiServer="api.smartliving.io", **kwargs):
        """
        connect to the http server
        :param apiServer: The api server to connect to.
        :param username: Username
        :param pwd: password
        :param kwargs: extra arguments for descendents
        :return:
        """
        self._curHttpServer = apiServer
        self._httpClient = httplib.HTTPConnection(apiServer)
        loginRes = self._login(username, pwd)
        self.extractHttpCredentials(loginRes)
        return loginRes

    def _login(self, username, pwd):
        url = "/login"
        body = "grant_type=password&username=" + username + "&password=" + pwd + "&client_id=maker"
        logging.info("HTTP POST: " + url)
        logging.info("HTTP BODY: " + body)
        self._httpClient.request("POST", url, body, {"Content-type": "application/json"})
        response = self._httpClient.getresponse()
        logging.info(str((response.status, response.reason)))
        jsonStr = response.read()
        logging.info(jsonStr)
        if response.status == 200:
            self._isLoggedIn = True
            return json.loads(jsonStr)
        else:
            self._processError(jsonStr)

    def extractHttpCredentials(self, data):
        if data:
            self._access_token = str(data['access_token'])
            self._refresh_token = str(data['refresh_token'])
            self._expires_in = time.time() + data['expires_in']
            self._clientId = str(data['rmq:clientId'])
        else:
            self._access_token = None
            self._refresh_token = None
            self._expires_in = None
            self._clientId = None

    def _refreshToken(self):
        """no need for error handling, is called within doHTTPRequest, which does the error handling"""
        url = "/login"
        body = "grant_type=refresh_token&refresh_token=" + self._refresh_token + "&client_id=dashboard"
        logging.info("HTTP POST: " + url)
        logging.info("HTTP BODY: " + body)
        self._httpClient.request("POST", url, body, {"Content-type": "application/json"})
        response = self._httpClient.getresponse()
        logging.info(str((response.status, response.reason)))
        jsonStr = response.read()
        logging.info(jsonStr)
        if response.status == 200:
            loginRes = json.loads(jsonStr)
        else:
            loginRes = None
        self.extractHttpCredentials(loginRes)

    def getAsset(self, id=None, gateway=None, device=None, name=None):
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
            raise Exception(
                "either assetId, (deviceId and asset name) or (gatewayid, deviceName and name) have to be specified")
        return self.doHTTPRequest(url, "")

    def createAsset(self, device, name, description, assetIs, assetType, style="Undefined"):
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

        return self.doHTTPRequest(url, json.dumps(body), 'PUT')

    def getAssetState(self, id):
        """get the details for the specified asset"""
        url = "/asset/" + id + '/state'
        result = self.doHTTPRequest(url, "")
        if result and 'state' in result:
            result = result['state']
        return result

    def getGateway(self, id):
        """get the details for the specified gateway"""
        url = "/gateway/" + id
        return self.doHTTPRequest(url, "")

    def getGrounds(self, includeShared):
        """get all the grounds related to the current account.
        :type includeShared: bool
        :param includeShared: when true, shared grounds will also be included
        """
        url = "/me/grounds"
        if includeShared:
            url += '?' + urllib.urlencode({'type': "shared"})
        result = self.doHTTPRequest(url, "")
        if result:
            return result['items']

    def getDevices(self, ground):
        """get all the devices related to a ground"""
        url = "/ground/" + ground + "/devices"
        result = self.doHTTPRequest(url, "")
        if result:
            return result['items']

    def getDevice(self, deviceId=None, gatewayId=None, deviceName=None):
        """get all the devices related to a ground
        either specify deviceId or gatewayId and deviceName
        """
        if deviceId:
            url = "/device/" + deviceId
        elif gatewayId and deviceName:
            url = "/gateway/" + gatewayId + "/device/" + deviceName
        else:
            raise Exception("either deviceId or gatewayid and deviceName have to be specified")
        return self.doHTTPRequest(url, "")

    def getAssets(self, device):
        """"get all the assets for a device"""
        url = "/device/" + device
        result = self.doHTTPRequest(url, "")
        if result:
            return result['assets']

    def pushNotification(self, message):
        """
        Send a notification to the account of the user.
        :param message: the message that should be sent
        :type message: basestring
        :return: the result of the request
        """
        url = "/service/push/notifications"
        content = {'message': message}
        return self.doHTTPRequest(url, json.dumps(content), 'POST')

    def getOutPath(self, assetId):
        """converts the asset id to a path of gateway id /device name / asset name or device id / asset name"""
        result = {}
        asset = self.getAsset(assetId)
        result['asset'] = asset['name']
        device = self.getDevice(asset['deviceId'])
        if device:
            if 'gatewayId' in device and device['gatewayId']:
                result['device'] = device['name']
                result['gateway'] = device['gatewayId']
            else:
                result['device'] = device['id']
        else:
            gateway = self.getGateway(asset['deviceId'])
            if gateway:
                result['gateway'] = gateway['id']
            else:
                raise Exception("asset does not belong to a device or gateway")
        return result

    def _reconnectAfterSendData(self):
        try:
            self._httpClient.close()
            self._httpClient = httplib.HTTPConnection(self._curHttpServer)  # recreate the connection when something went wrong. if we don't do this and an error occured, consecutive requests will also fail.
        except:
            logging.exception("reconnect failed after _sendData produced an error")

    def doHTTPRequest(self, url, content, method="GET"):
        """send the data and check the result
            Some multi threading applications can have issues with the server closing the connection, if this happens
            we try again
        """
        if self._isLoggedIn:
            success = False
            badStatusLineCount = 0  # keep track of the amount of 'badStatusLine' exceptions we received. If too many raise to caller, otherwise retry.
            while not success:
                try:
                    if self._expires_in < time.time():  # need to refesh the token first
                        self._refreshToken()
                    headers = {"Content-type": "application/json", "Authorization": "Bearer " + self._access_token}
                    logging.info("HTTP " + method + ': ' + url)
                    logging.info("HTTP HEADER: " + str(headers))
                    logging.info("HTTP BODY: " + content)
                    self._httpClient.request(method, url, content, headers)
                    response = self._httpClient.getresponse()
                    logging.info(str((response.status, response.reason)))
                    jsonStr = response.read()
                    logging.info(jsonStr)
                    if response.status == 200:
                        if jsonStr:
                            return json.loads(jsonStr)
                        else:
                            return  # get out of the ethernal loop
                    elif not response.status == 200:
                        self._processError(jsonStr)
                except httplib.BadStatusLine:  # a bad status line is probably due to the connection being closed. If it persists, raise the exception.
                    badStatusLineCount += 1
                    if badStatusLineCount < 10:
                        self._reconnectAfterSendData()
                    else:
                        raise
                except (SocketError) as e:
                    self._reconnectAfterSendData()
                    if e.errno != errno.ECONNRESET:  # if it's error 104 (connection reset), then we try to resend it, cause we just reconnected
                        raise
                except:
                    self._reconnectAfterSendData()
                    raise
        else:
            raise Exception("Not logged in: please check your credentials")

    def send_command(self, id, value, device=None, gateway=None):
        body = {"value": value}
        body = json.dumps(body)

        url = ""
        if gateway:
            url = '/gateway/' + gateway
        if device:
            url += '/device/' + device
        url += "/asset/" + id + "/command"

        self.doHTTPRequest(url, body, "PUT")

    def send_state(self, id, value, device=None, gateway=None, timestamp = None):
        """
        Send a state value to a sensor
        :param id: the id or name of the sensor
        :param value:  the value to send
        :param device:  optional device (if id is used as name of the sensor), must be name if gaeway is also specified, otherwise id of device.
        :param gateway: optional id of the gateway.
        :param timestamp: optional timestamp of measurement, when none, current timestamp will be used.
        :return:
        """
        body = {"value": value, "at": timestamp if not None else datetime.datetime.now()}
        body = json.dumps(body)
        url = ""
        if gateway:
            url = '/gateway/' + gateway
        if device:
            url += '/device/' + device
        url += "/asset/" + id + "/state"

        self.doHTTPRequest(url, body, "PUT")

    @staticmethod
    def _processError(str):
        if str:
            try:
                obj = json.loads(str)
                if obj:
                    if 'error_description' in obj:
                        raise Exception(obj['error_description'])
                    elif 'message' in obj:
                        raise Exception(obj['message'])
            except:
                logging.exception("failed to extract error message")
        raise Exception(str)


class SubscriberData(object):
    """
    id: dictionary of fields: gateway, device, asset  -> name or id
    callback: function to call when data arrived.
    direction: 'in' (from cloud to client) or 'out' (from device to cloud)
    toMonitor: 'state': changes in the value of the asset, 'command' actuator commands, 'events': device/asset/... creaated, deleted,..
    level: 'asset', 'device', 'gateway', 'ground' # 'all device-assets', 'all gateway-assets', 'all gateway-devices', 'all gateway-device-assets'
    """
    def __init__(self, connection):
        """
        create object
        :type connection: Client
        :param connection: the client connection to operate within
        """
        self.id = None
        self.callback = None
        self.direction = 'in'
        self.toMonitor = 'state'
        self.level = 'asset'
        self.connection = connection

    def getTopic(self, divider=None, wildcard=None, multi_wildcard=None):
        """
        generate topic
        :param desc: description of the topic to make
        """
        if divider == None:
            divider = self.connection.divider
        if wildcard == None:
            wildcard = self.connection.wildcard
        if multi_wildcard == None:
            multi_wildcard = self.connection.multi_wildcard
        def getId(name):
            """get the value for the id field, converting wildcards where needed"""
            val = self.id[name]
            if val in ['+', '*']:
                return self.connection.wildcard
            elif val == '#':
                return self.connection.multi_wildcard
            else:
                return val

        if self.level == 'asset':
            if isinstance(self.id, dict):
                if 'gateway' in self.id:
                    if 'device' in self.id:
                        return "client{0}{1}{0}{2}{0}gateway{0}{3}{0}device{0}{4}{0}asset{0}{5}{0}{6}".format(divider, self.connection._clientId, self.direction, getId('gateway'), getId('device'), getId('asset'), self.toMonitor)
                        # return "client/" + str(_clientId) + "/" + self.direction + "/gateway/" + self.id['gateway'] + "/device/" + self.id['device'] + "/asset/" + self.id['asset'] + "/" + self.toMonitor
                    else:
                        return "client{0}{1}{0}{2}{0}gateway{0}{3}{0}asset{0}{4}{0}{5}".format(divider,self.connection._clientId,self.direction,getId('gateway'),getId('asset'),self.toMonitor)
                        #return str("client/" + _clientId + "/" + self.direction + "/gateway/" + self.id['gateway'] + "/asset/" + self.id['asset'] + "/" + self.toMonitor)
                elif 'device' in self.id:
                    return "client{0}{1}{0}{2}{0}device{0}{3}{0}asset{0}{4}{0}{5}".format(divider,self.connection._clientId,self.direction,getId('device'),getId('asset'),self.toMonitor)
                    #return str("client/" + _clientId + "/" + self.direction + "/device/" + self.id['device'] + "/asset/" +self.id['asset'] + "/" + self.toMonitor)
                else:
                    return "client{0}{1}{0}{2}{0}asset{0}{3}{0}{4}".format(divider, self.connection._clientId, self.direction, getId('asset'), self.toMonitor)
            else:
                return "client{0}{1}{0}{2}{0}asset{0}{3}{0}{4}".format(divider, self.connection._clientId,self.direction,self.id, self.toMonitor)
                #return str("client/" + _clientId + "/" + self.direction + "/asset/" + self.id + "/" + self.toMonitor)  # asset is usually a unicode string, mqtt trips over this.
        elif self.level == 'timer':
            return "{1}{0}timer{0}{2}".format(divider, self.id['context'], self.id['name'])
        elif self.level == "device":
            if 'gateway' in self.id:
                return "client{0}{1}{0}{2}{0}gateway{0}{3}{0}device{0}{4}{0}{5}".format(divider, self.connection._clientId, self.direction, getId('gateway'), getId('device'), self.toMonitor)
            else:
                return "client{0}{1}{0}{2}{0}device{0}{3}{0}{4}".format(divider, self.connection._clientId, self.direction, getId('device'), self.toMonitor)
        # todo: add topic renderers for different type of topics.
        raise NotImplementedError()

class Client(HttpClient):
    """
    a client that provides both http and mqtt connections.
    """

    def __init__(self):
        """
        create the object
        """
        super(Client, self).__init__()
        self.divider = '/'
        self.wildcard = '+'
        self.multi_wildcard = '#'
        self._callbacks = {}
        self._mqttClient = None
        self._mqttConnected = False
        self._brokerPwd = None
        self._brokerUser = None
        self._broker = None
        self._blocking = True

    def connect(self, username, pwd, blocking=False, apiServer="api.smartliving.io", broker="broker.smartliving.io"):
        '''start the mqtt client and make certain that it can receive data from the IOT platform
    	   mqttServer: (optional): the address of the mqtt server. Only supply this value if you want to a none standard server.
    	   port: (optional) the port number to communicate on with the mqtt server.
        '''
        mqttCredentials = self.connect_api(username, pwd, apiServer)
        if not "rmq:clientId" in mqttCredentials:
            logging.error("username not specified, can't connect to broker")
            raise Exception("username not specified, can't connect to broker")
        self._brokerUser = mqttCredentials["rmq:clientId"] + ":" + mqttCredentials["rmq:clientId"]
        self._brokerPwd = mqttCredentials["rmq:clientKey"]
        self._broker = broker
        self._blocking = blocking
        self._connect_mqtt()

    def reconnect(self):
        """
        reconnect to both broker and api server.
        :return: None
        """
        if self._httpClient:
            self._httpClient.close()
        self._httpClient = httplib.HTTPConnection(self._curHttpServer)
        self._connect_mqtt()

    def disconnect(self, resumable=False):
        """close all connections to the cloud and reset the module
        if resumable is True, then only the network connections get closed, but the connection data remains, so that
        you can restart connections using the reconnect features.
        """
        if not resumable:
            self._isLoggedIn = False
            self._access_token = None
            self._refresh_token = None
            self._expires_in = None
            for topic, callback in self._callbacks.iteritems():
                self._unsubscribe(topic)
            self._callbacks = {}
            self._brokerPwd = None
            self._brokerUser = None
        if self._mqttClient:
            self._mqttClient.disconnect()
            self._mqttClient = None
        self._mqttConnected = False
        if self._httpClient:
            self._httpClient.close()
        self._httpClient = None

    def connect_broker(self, username, pwd, broker="broker.smartliving.io", blocking=True):
        """
        connect to the broker
        :param username: username to connect with
        :param pwd: pwd to connect with
        :param broker: name of broker
        :param kwargs: extra params for descendents.
        :return:
        """
        self._brokerUser = username
        self._brokerPwd = pwd
        self.self._broker = broker
        self._blocking = blocking
        self._connect_mqtt()

    def _connect_mqtt(self):
        if self._brokerPwd and self._brokerUser:
            if self._mqttClient:
                self._mqttClient.disconnect()
            self._mqttClient = mqtt.Client()
            self._mqttClient.on_connect = self.on_connect
            self._mqttClient.user_data_set(self)                            # pass self to the callback functions (on_connect, on_mqttmessage,...)
            self._mqttClient.on_message = self.on_MQTTmessage
            self._mqttClient.on_subscribe = self.on_MQTTSubscribed
            self._mqttClient.username_pw_set(self._brokerUser, self._brokerPwd)

            self._mqttClient.connect(self._broker, 1883, 60)
            if not self._blocking:
                self._mqttClient.loop_start()
            else:
                self._mqttClient.reconnect()
        else:
            raise Exception("no mqtt credentials found")

    # The callback for when the client receives a CONNACK response from the server.
    @staticmethod
    def on_connect(client, userdata, rc):
        try:
            if rc == 0:
                userdata._mqttConnected = True
                logging.info("Connected to mqtt broker with result code " + str(rc))
                if userdata._callbacks:
                    for topic, definitions in userdata._callbacks.iteritems():
                        userdata._subscribe(topic)
                        for definition in definitions:
                            # note: if definition.id is a string, then it points to a single asset, otherwise it's a path, that we can't
                            if isinstance(definition.id,
                                          basestring) and definition.level == 'asset' and definition.direction == 'in' and definition.toMonitor == 'state':  # refresh the state of all assets being monitored when reconnecting. Other events can't be refreshed.
                                curVal = userdata.getAssetState(definition.id)
                                if curVal:
                                    definition.callback(curVal)
            else:
                logging.error("Failed to connect to mqtt broker: " + mqtt.connack_string(rc))
        except Exception:
            logging.exception("failed to connect")

    # The callback for when a PUBLISH message is received from the server.
    @staticmethod
    def on_MQTTmessage(client, userdata, msg):
        try:
            if msg.topic in userdata._callbacks:
                topicParts = msg.topic.split('/')
                logging.info(str(topicParts))
                if topicParts[2] == 'in':  # data from cloud to client is always json, from device to cloud is not garanteed to be json.
                    value = json.loads(msg.payload)
                else:
                    value = msg.payload
                defs = userdata._callbacks[msg.topic]
                for definition in defs:
                    definition.callback(value)
        except Exception as e:
            if msg.payload:
                logging.exception("failed to process incomming message" + str(msg.payload))
            else:
                logging.exception("failed to process incomming message")

    @staticmethod
    def on_MQTTSubscribed(client, userdata, mid, granted_qos):
        logging.info("Subscribed to topic, receiving data from the cloud: qos=" + str(granted_qos))

    def subscribe(self, asset, callback):
        """monitor for changes for that asset. For more monitor features, use 'subscribeAdv'
        :type callback: function, format: callback(json_object)
        :param callback: a function that will be called when a value arrives for the specified asset.
        :type asset: string
        :param asset: the id of the assset to monitor
        """
        data = SubscriberData(self)
        data.id = asset
        data.callback = callback
        topic = data.getTopic()
        if topic in self._callbacks:
            self._callbacks[topic].append(data)
        else:
            self._callbacks[topic] = [data]
        if self._mqttClient and self._mqttConnected == True:
            self._subscribe(topic)

    def subscribeAdv(self, subscriberData, topic=None):
        """subscribe to topics with advanced parameter options
        If the topic is not provided, it is calculated from the subscriberData.
        This is for apps that also calculate the topic string, so that this isn't done unnecessarily
        """
        if not topic:
            topic = subscriberData.getTopic()
        if topic in self._callbacks:
            self._callbacks[topic].append(subscriberData)
        else:
            self._callbacks[topic] = [subscriberData]
        if self._mqttClient and self._mqttConnected == True:
            self._subscribe(topic)

    def addMessageCallback(self, topic, monitor):
        self._subscribe(topic)
        if topic in self._callbacks:
            raise Exception("topic already registered")
        else:
            self._callbacks[topic] = [monitor]
        self._mqttClient.message_callback_add(topic, lambda client, userdata, msg: monitor.onAssetValueChanged(json.loads(msg.payload)))

    def removeMessageCallback(self, topic):
        self._unsubscribe(topic)
        self._callbacks.pop(topic)
        self._mqttClient.message_callback_remove(topic)

    def unsubscribe(self, id, level='asset'):
        """
        remove all the callbacks for the specified id.
        :param level: which type of item: asset, device, gateway
        :param id: the id of the item (asset, device, gateway,..) to remove
        """
        desc = SubscriberData(self)
        desc.id = id
        desc.level = level
        for direction in ['in', 'out']:
            desc.direction = direction
            for toMonitor in ['state', 'event', 'command']:
                desc.toMonitor = toMonitor
                topic = desc.getTopic()
                if topic in self._callbacks:
                    self._callbacks.pop(topic)
                    if self._mqttClient and self._mqttConnected == True:
                        self._unsubscribe(topic)


    def _subscribe(self, topic):
        """
            internal subscribe routine
        :param desc: description of the subscription to make
        """
        logging.info("subscribing to: " + topic)
        result = self._mqttClient.subscribe(topic)  # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
        logging.info(str(result))

    def _unsubscribe(self, topic):
        logging.info("unsubscribing to: " + topic)
        result = self._mqttClient.unsubscribe(topic)  # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
        logging.info(str(result))


    def loop(self):
        """in case that the connect was called in a blocking manner, then this has to be called to start the main mqtt loop"""
        self._mqttClient.loop_forever()


    #todo: re-enable this function overload when publish command is fully supported (for virtuals)
    #def send_command(self, id, value, device=None, gateway=None):
    #    """
    #    send a command through mqtt.
    #    :param id:
    #    :param value:
    #    :param device:
    #    :param gateway:
    #    :return:
    #    """
    #    typeOfVal = type(value)
    #    if typeOfVal in [types.IntType, types.BooleanType, types.FloatType, types.LongType,
    #                     types.StringType]:  # if it's a basic type: send as csv, otherwise as json.
    #        toSend = str(value)
    #    else:
    #        toSend = json.dumps(value)
    #    topic = "client/" + self._clientId + "/in/"
    #    if gateway:
    #        topic += "gateway/" + gateway
    #    if device != None:
    #        topic += "/device/" + device + "/asset/" + str(id) + "/command"  # also need a topic to publish to
    #    else:
    #        topic += "/asset/" + str(id) + "/command"
    #    logging.info("Publishing message - topic: " + topic + ", payload: " + toSend)
    #    self._mqttClient.publish(topic, toSend, 0, False)