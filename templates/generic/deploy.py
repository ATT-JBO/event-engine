__author__ = 'Jan Bogaerts'
__copyright__ = "Copyright 2016, AllThingsTalk"
__credits__ = []
__maintainer__ = "Jan Bogaerts"
__email__ = "jb@allthingstalk.com"
__status__ = "Prototype"  # "Development", or "Production"


import requests
import json
import credentials

with open("rules.py") as file:
    code = file.read()
    r = requests.put("http://localhost:1000/event", data=json.dumps({'name': 'test1',
                                                     'version': '0.1',
                                                     'username': credentials.UserName,
                                                     'password': credentials.Pwd,
                                                     'parameters':{},
                                                     'code': code}))
    print(r.status_code, r.reason, r.content)