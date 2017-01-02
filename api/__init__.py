# -*- encoding: UTF-8 -*-
#
# Form based authentication for CherryPy. Requires the
# Session tool to be loaded.
#

import json
import cherrypy

import urllib
import os
import xmlrpclib

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
		cherrypy.response.headers["Content-Type"] = "application/json"
		return json.dumps({'status': '0', 'statusText': 'Ok', 'data': self.conf.config['odr']})
	
	@cherrypy.expose
	@require()
	def setConfig(self):
		self.conf = Config(self.config_file)
		
		cl = cherrypy.request.headers['Content-Length']
		rawbody = cherrypy.request.body.read(int(cl))
		odr = json.loads(rawbody)
		
		output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': odr }
        
        # Write configuration file
		try:
			self.conf.write(output)
		except Exception,e:
			cherrypy.response.headers["Content-Type"] = "application/json"
			return json.dumps({'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)})
        
        # Generate supervisor files
		try:
			self.conf.generateSupervisorFiles(output)
		except Exception,e:
			cherrypy.response.headers["Content-Type"] = "application/json"
			return json.dumps({'status': '-202', 'statusText': 'Error generating supervisor files' + str(e)})
		
		
		# Check if ODR program availaible in supervisor ProcessInfo and try to add it
		
		# Retreive supervisor process
		server = xmlrpclib.Server(self.conf.config['global']['supervisor_xmlrpc'])
		programs = server.supervisor.getAllProcessInfo()
		
		# Check for ODR-audioencoder
		if not self.is_program_exist(programs, 'ODR-audioencoder'):
			try:
				server.supervisor.reloadConfig()
				server.supervisor.addProcessGroup('ODR-audioencoder')
			except:
				cherrypy.response.headers["Content-Type"] = "application/json"
				return json.dumps({'status': '-206', 'statusText': 'Error when starting ODR-audioencoder (XMLRPC): ' + str(e)})
		
		# Check for ODR-padencoder
		if not self.is_program_exist(programs, 'ODR-padencoder'):
			try:
				server.supervisor.reloadConfig()
				server.supervisor.addProcessGroup('ODR-padencoder')
			except:
				cherrypy.response.headers["Content-Type"] = "application/json"
				return json.dumps({'status': '-207', 'statusText': 'Error when starting ODR-padencoder (XMLRPC): ' + str(e)})
		
		cherrypy.response.headers["Content-Type"] = "application/json"
		return json.dumps({'status': '0', 'statusText': 'Ok'})
	
	@cherrypy.expose
	@require()
	def getDLS(self):
		self.conf = Config(self.config_file)
		cherrypy.response.headers["Content-Type"] = "application/json"
		
		if self.conf.config['odr']['padenc']['enable'] == 'true':
			try:
				f = open(self.conf.config['odr']['padenc']['dls_fifo_file'], 'r')
				dls = f.read()
				f.close()
			except Exception,e:
				return json.dumps({'dls': 'Fail to read dls data'})
			else:
				return json.dumps({'dls': str(dls)})
		else:
			return json.dumps({'dls': 'DLS is disable ...'})
	
	def is_program_exist(self, json, program):
		ex = False
		for p in json:
			if p['name'] == program :
				ex = True
		return ex
		
	@cherrypy.expose
	@require()
	def getStatus(self):
		self.conf = Config(self.config_file)
		cherrypy.response.headers["Content-Type"] = "application/json"
		server = xmlrpclib.Server(self.conf.config['global']['supervisor_xmlrpc'])
		output = []
		
		try:
			output.append( server.supervisor.getProcessInfo('ODR-audioencoder') )
			output.append( server.supervisor.getProcessInfo('ODR-padencoder') )
		except Exception,e:
			return json.dumps({'status': '-301', 'statusText': 'Error when getting ODR-audioencoder and ODR-padencoder status (XMLRPC): ' + str(e)})
		
		return json.dumps({'status': '0', 'statusText': 'Ok', 'data': output})
	
	
	def serviceAction(self, action, service):
		self.conf = Config(self.config_file)
		
		server = xmlrpclib.Server(self.conf.config['global']['supervisor_xmlrpc'])
		try:
			if action == 'start':
				server.supervisor.reloadConfig()
				server.supervisor.removeProcessGroup(service)
				server.supervisor.reloadConfig()
				server.supervisor.addProcessGroup(service)
				server.supervisor.reloadConfig()
				#server.supervisor.startProcess(service)
			elif action == 'stop':
				server.supervisor.stopProcess(service)
			elif action == 'restart':
				server.supervisor.stopProcess(service)
				
				server.supervisor.reloadConfig()
				server.supervisor.removeProcessGroup(service)
				server.supervisor.reloadConfig()
				server.supervisor.addProcessGroup(service)
				server.supervisor.reloadConfig()
				#server.supervisor.startProcess(service)
		except Exception,e:
			return { 'status': '-401', 'statusText': str(e) }
		else:
			return { 'status': '0', 'statusText': 'Ok', 'data': [] }
	
	@cherrypy.expose
	@require()
	def start(self):
		cherrypy.response.headers["Content-Type"] = "application/json"
		
		cl = cherrypy.request.headers['Content-Length']
		rawbody = cherrypy.request.body.read(int(cl))
		data = odr = json.loads(rawbody)
		
		return json.dumps(self.serviceAction('start', data['service']))
		
	@cherrypy.expose
	@require()
	def stop(self):
		cherrypy.response.headers["Content-Type"] = "application/json"
		
		cl = cherrypy.request.headers['Content-Length']
		rawbody = cherrypy.request.body.read(int(cl))
		data = odr = json.loads(rawbody)
		
		return json.dumps(self.serviceAction('stop', data['service']))
	
	@cherrypy.expose
	@require()
	def restart(self):
		cherrypy.response.headers["Content-Type"] = "application/json"
		
		cl = cherrypy.request.headers['Content-Length']
		rawbody = cherrypy.request.body.read(int(cl))
		data = odr = json.loads(rawbody)
		
		return json.dumps(self.serviceAction('restart', data['service']))