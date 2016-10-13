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
			command = output['odr']['path']['padenc_path']
			if output['odr']['padenc']['slide_directory'].strip() != '':
				# Check if config.mot_slide_directory exist
				if os.path.exists(output['odr']['padenc']['slide_directory']):
					command += ' --dir=%s' % (output['odr']['padenc']['slide_directory'])
					command += ' --sleep=%s' % (output['odr']['padenc']['slide_sleeping'])
					if output['odr']['padenc']['slide_once'] == 'true':
						command += ' --erase'
						
			# Check if config.mot_dls_fifo_file exist and create it if needed.
			if not os.path.isfile(output['odr']['padenc']['dls_fifo_file']):
				try:
					f = open(output['odr']['padenc']['dls_fifo_file'], 'w')
					f.close()
				except Exception,e:
					pass
			else:
				f = open(output['odr']['padenc']['dls_fifo_file'], 'w')
				f.write('')
				f.close()
				
			# Check if config.mot_pad_fifo_file exist and create it if needed.
			if not os.path.exists(output['odr']['padenc']['pad_fifo_file']):
				try:
					os.mkfifo(output['odr']['padenc']['pad_fifo_file'])
				except Exception,e:
					pass
			else:
				if not stat.S_ISFIFO(os.stat(output['odr']['padenc']['pad_fifo_file']).st_mode):
					#File %s is not a fifo file
					pass
			
			command += ' --pad=%s' % (output['odr']['padenc']['pad'])
			command += ' --dls=%s' % (output['odr']['padenc']['dls_fifo_file'])
			command += ' --output=%s' % (output['odr']['padenc']['pad_fifo_file'])
			
			if output['odr']['padenc']['raw_dls'] == 'true':
				command += ' --raw-dls'
				
			supervisorPadEncConfig = ""
			supervisorPadEncConfig += "[program:ODR-PadEnc]\n"
			supervisorPadEncConfig += "command=%s\n" % (command)
			supervisorPadEncConfig += "autostart=true\n"
			supervisorPadEncConfig += "autorestart=true\n"
			supervisorPadEncConfig += "priority=10\n"
			#supervisorPadEncConfig += "user=odr\n"
			#supervisorPadEncConfig += "group=odr\n"
			supervisorPadEncConfig += "stderr_logfile=/var/log/supervisor/ODR-PadEnc.err.log\n"
			supervisorPadEncConfig += "stdout_logfile=/var/log/supervisor/ODR-PadEnc.log\n"
			
			
				
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
				if os.path.exists(output['odr']['padenc']['pad_fifo_file']) and stat.S_ISFIFO(os.stat(output['odr']['padenc']['pad_fifo_file']).st_mode):
					command += ' --pad=%s' % (output['odr']['padenc']['pad'])
					command += ' --pad-fifo=%s' % (output['odr']['padenc']['pad_fifo_file'])
			
			command += ' -f raw'
			hosts = output['odr']['output']['zmq_host'].replace(' ','').split(',')
			for host in hosts:
				command += ' -o tcp://%s' % (host)
		
		supervisorConfig = ""
		supervisorConfig += "[program:ODR-audioencoder]\n"
		supervisorConfig += "command=%s\n" % (command)
		supervisorConfig += "autostart=true\n"
		supervisorConfig += "autorestart=true\n"
		supervisorConfig += "priority=10\n"
		#supervisorConfig += "user=odr\n"
		#supervisorConfig += "group=odr\n"
		supervisorConfig += "stderr_logfile=/var/log/supervisor/ODR-audioencoder.err.log\n"
		supervisorConfig += "stdout_logfile=/var/log/supervisor/ODR-audioencoder.log\n"
		
		with open(output['global']['supervisor_file'], 'w') as supfile:
			 supfile.write(supervisorConfig)
			 supfile.write('\n')
			 supfile.write(supervisorPadEncConfig)
		
		return 'Ok'
	
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
	
	@cherrypy.expose
	@require()
	def getStatus(self):
		self.conf = Config(self.config_file)
		server = xmlrpclib.Server(self.conf.config['global']['supervisor_xmlrpc'])
		output = []
		
		output.append( server.supervisor.getProcessInfo('ODR-audioencoder') )
		output.append( server.supervisor.getProcessInfo('ODR-PadEnc') )
		
		cherrypy.response.headers["Content-Type"] = "application/json"
		return json.dumps(output)