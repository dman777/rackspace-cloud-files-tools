import os 
import sys
import getpass
import json
import logging
import requests

logger = logging.getLogger("krunch")

class Authenticate(object):
    """Authenticates user using apikey"""
    def __init__(self, username, apikey):
	self.username = username
	self.apikey = apikey
	self.token = None
	self.jsonresp = None
	self.getToken()

    url = "https://identity.api.rackspacecloud.com/v2.0/tokens"
    

    def getToken(self):
	try:
	    jsonreq = ( {"auth": {"RAX-KSKEY:apiKeyCredentials": {
			  "username": self.username,
			  "apiKey": self.apikey }}})
	    auth_headers = {'content-type': 'application/json'}
	    r = requests.post(self.url, data=json.dumps(jsonreq), headers=auth_headers)
	    self.jsonresp = json.loads(r.text)
	    self.token = str(self.jsonresp['access']['token']['id'])
	except:
	    msg = "Bad name or apikey!"
	    logger.error(msg)
	    sys.exit()
