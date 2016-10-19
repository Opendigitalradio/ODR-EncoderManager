# -*- encoding: UTF-8 -*-
#
# Form based authentication for CherryPy. Requires the
# Session tool to be loaded.
#

import json
import cherrypy

import urllib
import os
import stat
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
        
		try:
			with open(self.config_file, 'w') as outfile:
				data = json.dumps(output, indent=4, separators=(',', ': '))
				outfile.write(data)
		except Exception,e:
			cherrypy.response.headers["Content-Type"] = "application/json"
			return json.dumps({'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)})
		
		supervisorConfig = ""
		# Write supervisor pad-encoder section
		if output['odr']['padenc']['enable'] == 'true':
			command = output['odr']['path']['padenc_path']
			if output['odr']['padenc']['slide_directory'].strip() != '':
				# Check if config.mot_slide_directory exist
				if os.path.exists(output['odr']['padenc']['slide_directory']):
					command += ' --dir=%s' % (output['odr']['padenc']['slide_directory'])
					if output['odr']['padenc']['slide_once'] == 'true':
						command += ' --erase'
						
			# Check if config.mot_dls_fifo_file exist and create it if needed.
			if not os.path.isfile(output['odr']['padenc']['dls_fifo_file']):
				try:
					f = open(output['odr']['padenc']['dls_fifo_file'], 'w')
					f.close()
				except Exception,e:
					cherrypy.response.headers["Content-Type"] = "application/json"
					return json.dumps({'status': '-202', 'statusText': 'Error when create DLS fifo file' + str(e)})
			else:
				try:
					f = open(output['odr']['padenc']['dls_fifo_file'], 'w')
					f.write('')
					f.close()
				except Exception,e:
					cherrypy.response.headers["Content-Type"] = "application/json"
					return json.dumps({'status': '-203', 'statusText': 'Error when writing into DLS fifo file' + str(e)})
				
			# Check if config.mot_pad_fifo_file exist and create it if needed.
			if not os.path.exists(output['odr']['padenc']['pad_fifo_file']):
				try:
					os.mkfifo(output['odr']['padenc']['pad_fifo_file'])
				except Exception,e:
					cherrypy.response.headers["Content-Type"] = "application/json"
					return json.dumps({'status': '-204', 'statusText': 'Error when create PAD fifo file' + str(e)})
			else:
				if not stat.S_ISFIFO(os.stat(output['odr']['padenc']['pad_fifo_file']).st_mode):
					#File %s is not a fifo file
					pass
			
			command += ' --sleep=%s' % (output['odr']['padenc']['slide_sleeping'])
			command += ' --pad=%s' % (output['odr']['padenc']['pad'])
			command += ' --dls=%s' % (output['odr']['padenc']['dls_fifo_file'])
			command += ' --output=%s' % (output['odr']['padenc']['pad_fifo_file'])
			
			if output['odr']['padenc']['raw_dls'] == 'true':
				command += ' --raw-dls'
				
			supervisorPadEncConfig = ""
			supervisorPadEncConfig += "[program:ODR-padencoder]\n"
			supervisorPadEncConfig += "command=%s\n" % (command)
			supervisorPadEncConfig += "autostart=true\n"
			supervisorPadEncConfig += "autorestart=true\n"
			supervisorPadEncConfig += "priority=10\n"
			supervisorPadEncConfig += "stderr_logfile=/var/log/supervisor/ODR-padencoder.err.log\n"
			supervisorPadEncConfig += "stdout_logfile=/var/log/supervisor/ODR-padencoder.log\n"
			
		# Write supervisor audioencoder section
		# Encoder path
		command = output['odr']['path']['encoder_path']
		
		# Input stream
		if output['odr']['source']['type'] == 'alsa':
			command += ' -d %s' % (output['odr']['source']['device'])
		if output['odr']['source']['type'] == 'stream':
			command += ' --vlc-uri=%s' % (output['odr']['source']['url'])
		if output['odr']['source']['driftcomp'] == 'true':
			command += ' -D'
		command += ' -b %s' % (output['odr']['output']['bitrate'])
		command += ' -r %s' % (output['odr']['output']['samplerate'])
		command += ' -c %s' % (output['odr']['output']['channels'])
		
		# DAB specific option
		if output['odr']['output']['type'] == 'dab':
			command += ' --dab'
			command += ' --dabmode=%s' % (output['odr']['output']['dab_dabmode'])
			command += ' --dabpsy=%s' % (output['odr']['output']['dab_dabpsy'])
		
		
		# DAB+ specific option
		if output['odr']['output']['type'] == 'dabp':
			if output['odr']['output']['dabp_sbr'] == 'true':
				command += ' --sbr'
			if output['odr']['output']['dabp_ps'] == 'true':
				command += ' --ps'
			if output['odr']['output']['dabp_sbr'] == 'false' and output['odr']['output']['dabp_ps'] == 'false':
				command += ' --aaclc'
			if output['odr']['output']['dabp_afterburner'] == 'false':
				command += ' --no-afterburner'
		
		# PAD encoder
		if output['odr']['padenc']['enable'] == 'true':
			if os.path.exists(output['odr']['padenc']['pad_fifo_file']) and stat.S_ISFIFO(os.stat(output['odr']['padenc']['pad_fifo_file']).st_mode):
				command += ' --pad=%s' % (output['odr']['padenc']['pad'])
				command += ' --pad-fifo=%s' % (output['odr']['padenc']['pad_fifo_file'])
				command += ' --write-icy-text=%s' % (output['odr']['padenc']['dls_fifo_file'])
		
		# Output
		hosts = output['odr']['output']['zmq_host'].replace(' ','').split(',')
		for host in hosts:
			command += ' -o tcp://%s' % (host)
				
		supervisorConfig = ""
		supervisorConfig += "[program:ODR-audioencoder]\n"
		supervisorConfig += "command=%s\n" % (command)
		supervisorConfig += "autostart=true\n"
		supervisorConfig += "autorestart=true\n"
		supervisorConfig += "priority=10\n"
		supervisorConfig += "stderr_logfile=/var/log/supervisor/ODR-audioencoder.err.log\n"
		supervisorConfig += "stdout_logfile=/var/log/supervisor/ODR-audioencoder.log\n"
		
		try:
			with open(output['global']['supervisor_file'], 'w') as supfile:
				supfile.write(supervisorConfig)
				supfile.write('\n')
				supfile.write(supervisorPadEncConfig)
		except Exception,e:
			cherrypy.response.headers["Content-Type"] = "application/json"
			return json.dumps({'status': '-205', 'statusText': 'Error when writing supervisor file: ' + str(e)})
		
		# Check if ODR program availaible in supervisor ProcessInfo and try to add it
		server = xmlrpclib.Server(self.conf.config['global']['supervisor_xmlrpc'])
		programs = server.supervisor.getAllProcessInfo()
		if not self.is_program_exist(programs, 'ODR-audioencoder'):
			try:
				server.supervisor.reloadConfig()
				server.supervisor.addProcessGroup('ODR-audioencoder')
			except:
				cherrypy.response.headers["Content-Type"] = "application/json"
				return json.dumps({'status': '-206', 'statusText': 'Error when starting ODR-audioencoder (XMLRPC): ' + str(e)})
					
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