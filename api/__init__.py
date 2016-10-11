# -*- encoding: UTF-8 -*-
#
# Form based authentication for CherryPy. Requires the
# Session tool to be loaded.
#

import json
import cherrypy
import urllib
import os

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
		
		supervisorConfig = ""
		# Write supervisor pad-encoder section
		if output['odr']['padenc']['enable'] == 'true':
			# TODO ADD PADENC SUPPORT
			pass
				
		# Write supervisor audio-encoder section
		if output['odr']['output']['type'] == 'dab':
			command = output['odr']['path']['encoder_dab_path']
			if output['odr']['source']['type'] == 'stream':
				command += ' -s %s' % (output['odr']['output']['dab_samplerate'])
				command += ' -V %s' % (output['odr']['source']['url'])
				command += ' -b %s' % (output['odr']['output']['dab_bitrate'])
				if output['odr']['padenc']['enable'] == 'true':
					command += ' -W %s' % (output['odr']['padenc']['dls_fifo_file'])
			
			if output['odr']['source']['type'] == 'alsa':
				command += ' -s %s' % (output['odr']['output']['dab_samplerate'])
				command += ' -V alsa://plug%s' % (output['odr']['source']['device'])
				command += ' -b %s' % (output['odr']['output']['dab_bitrate'])
			
			if output['odr']['padenc']['enable'] == 'true':
				if os.path.exists(output['odr']['padenc']['pad_fifo_file']) and stat.S_ISFIFO(os.stat(output['odr']['padenc']['pad_fifo_file']).st_mode):
					command += ' -p %s' % (output['odr']['padenc']['pad'])
					command += ' -P %s' % (output['odr']['padenc']['pad_fifo_file'])
			
			hosts = output['odr']['output']['zmq_host'].replace(' ','').split(',')
			for host in hosts:
				command += ' tcp://%s;' % (host)
			# Remove the last fucking ;
			command = command[:-1]
			
		elif output['odr']['output']['type'] == 'dabp':
			command = output['odr']['path']['encoder_dabp_path']
			if output['odr']['source']['type'] == 'alsa':
				command += ' -d %s' % (output['odr']['source']['device'])
			if output['odr']['source']['type'] == 'stream':
				command += ' --vlc-uri=%s' % (output['odr']['source']['url'])
			if output['odr']['source']['driftcomp'] == 'true':
				command += ' -D'
			command += ' -b %s -r %s' % (output['odr']['output']['dabp_bitrate'], output['odr']['output']['dabp_samplerate'])
			if output['odr']['output']['dabp_sbr'] == 'true':
				command += ' --sbr'
			if output['odr']['output']['dabp_ps'] == 'true':
				command += ' --ps'
			if output['odr']['output']['dabp_afterburner'] == 'false':
				command += ' --no-afterburner'
			
			if output['odr']['padenc']['enable'] == 'true':
				# TODO ADD PADENC SUPPORT
				pass
			
			command += ' -f raw'
			hosts = output['odr']['output']['zmq_host'].replace(' ','').split(',')
			for host in hosts:
				command += ' -o tcp://%s' % (host)
		
		
		supervisorConfig += "[program:ODR-audioencoder]\n"
		supervisorConfig += "command=%s\n" % (command)
		supervisorConfig += "autostart=true\n"
		supervisorConfig += "autorestart=true\n"
		supervisorConfig += "priority=10\n"
		supervisorConfig += "user=odr\n"
		supervisorConfig += "group=odr\n"
		supervisorConfig += "stderr_logfile=/var/log/supervisor/ODR-audioencoder.err.log\n"
		supervisorConfig += "stdout_logfile=/var/log/supervisor/ODR-audioencoder.log\n"
		
		with open(output['global']['supervisor_file'], 'w') as supfile:
			 supfile.write(supervisorConfig)
		
		return 'Ok'