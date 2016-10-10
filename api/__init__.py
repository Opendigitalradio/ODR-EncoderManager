# -*- encoding: UTF-8 -*-
#
# Form based authentication for CherryPy. Requires the
# Session tool to be loaded.
#

import json
import cherrypy
import urllib

from config import Config
from auth import AuthController, require, is_login

class API():
	
	def __init__(self, config_file):
		self.config_file = config_file
		self.conf = Config(self.config_file)
		self.auth = AuthController(self.conf.config['auth'])
		
	
	# all methods in this controller (and subcontrollers) is
	# open only to members of the admin group
	
	@cherrypy.expose
	def index(self):
		return """This is the api area."""
	
	@cherrypy.expose
	@require()
	def getConfig(self):
		self.conf = Config(self.config_file)
		return json.dumps(self.conf.config['odr'])
	
	@cherrypy.expose
	@require()
	def setConfig(self):
		self.conf = Config(self.config_file)
		
		cl = cherrypy.request.headers['Content-Length']
		rawbody = cherrypy.request.body.read(int(cl))
		odr = json.loads(rawbody)
		
		output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': odr }
        
		with open(self.config_file, 'w') as outfile:
			data = json.dumps(output, indent=4, separators=(',', ': '))
			outfile.write(data)
		
		return 'Ok'