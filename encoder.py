#!/usr/bin/env python

# -*- coding: utf-8 -*-
import os
import sys
import argparse

from twisted.internet import protocol, defer
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver

from txjsonrpc.web import jsonrpc
from txjsonrpc import jsonrpclib

from twisted.web import server

from twisted.internet import reactor
import re
import time

import json

from config import Config

import signal
from signal import SIGKILL

import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class EncoderManager():
	def __init__(self, configFile):
		self.encoderProcess = None
		self.motProcess = None
		self.configFile = configFile
		self.config = Config(self.configFile, logger)
		self.autorestart = True
	
	def get_dls(self):
		if self.config.mot == True:
			try:
				f = open(self.config.mot_dls_fifo_file, 'r')
				dls = f.read()
				f.close()
			except Exception,e:
				logger.warn('get_dls Fail to read dls data in file %s, error: %s' % (self.config.mot_dls_fifo_file, e))
				return str(e)
			else:
				return {'dls': str(dls)}
		else:
			return {'dls': 'DLS is disable ...'}

	def set_dls(self, dls=''):
		if self.config.mot == True:
			try:
				f = open(self.config.mot_dls_fifo_file, 'w')
				f.write(dls)
				f.close()
			except Exception,e:
				logger.warn('set_dls Fail to write dls data in file %s, error: %s' % (self.config.mot_dls_fifo_file, e))
				return str(e)
			else:
				return dls
		else:
			return 'set_dls DLS is disable ...'
	
	def reload_config(self):
		self.config = Config(self.configFile, logger)
	
	def getStatus(self):
		result = {}
		if self.encoderProcess == None:
			result['encoder'] = {'status': 'not running', 'pid': 0}
		else:
			result['encoder'] = {'status': 'running', 'pid': self.encoderProcess.transport.pid}
			
		if self.motProcess == None:
			result['mot-encoder'] = {'status': 'not running', 'pid': 0}
		else:
			result['mot-encoder'] = {'status': 'running', 'pid': self.motProcess.transport.pid}
			
		return result
		
	def run_encoder(self):
		self.autorestart = True
		executable = self.config.global_encoder_path
		args = executable
		
		if self.config.source_type == 'alsa':
			args += ' -d %s' % (self.config.source_device)
			if self.config.source_driftcomp == True:
				args += ' -D'
		if self.config.source_type == 'stream':
			args += ' --vlc-uri=%s' % (self.config.source_url)
		
		args += ' -b %s -r %s' % (self.config.output_bitrate, self.config.output_samplerate)
		if self.config.output_sbr == True:
			args += ' --sbr'
		if self.config.output_ps == True:
			args += ' --ps'
		if self.config.output_afterburner == False:
			args += ' --no-afterburner'
			
		if self.config.mot == True:
			if not os.path.isfile(self.config.mot_pad_fifo_file):
				logger.warn('dabplus-enc Pad file %s not exist. Ignoring PAD parameters.' % (self.config.mot_pad_fifo_file))
			else:
				args += ' --pad=%s' % (self.config.mot_pad)
				args += ' --pad-fifo=%s' % (self.config.mot_pad_fifo_file)
		
		args += ' -f raw -o tcp://%s:%s' % (self.config.output_host, self.config.output_port)
		if self.config.output_key_file.strip() != '':
			if os.path.isfile(self.config.output_key_file):
				args += ' -k %s' % (self.config.output_key_file)
			else:
				logger.crit('dabplus-enc ZMQ secret key file not found or not readable. Ignoring this file and secret-key parameters.')
		args = args.split()
		encoderProcessProtocol = MyEncoderProcessProtocol(self)
		reactor.spawnProcess(encoderProcessProtocol, executable, args, {})
	
	def stop_encoder(self, autorestart=True):
		self.autorestart = autorestart
		if self.encoderProcess:
			self.encoderProcess.transport.signalProcess(SIGKILL)
			
	def run_mot(self):
		self.autorestart = True
		executable = self.config.global_mot_path
		args = executable
		
		if self.config.mot == True:
			if self.config.mot_slide_directory.strip() != '':
				# Check if config.mot_slide_directory exist
				if not os.path.exists(self.config.mot_slide_directory):
					logger.warn('mot-encoder Slide directory not exist or not readable. Ignoring slide directory parameters - %s' % (self.config.mot_slide_directory))
				else:
					args += ' --dir=%s' % (self.config.mot_slide_directory)
					args += ' --sleep=%s' % (self.config.mot_slide_sleeping)
					if self.config.mot_slide_once == True:
						args += ' --erase'
						
			# Check if config.mot_dls_fifo_file exist and create it if needed.
			if not os.path.isfile(self.config.mot_dls_fifo_file):
				try:
					f = open(self.config.mot_dls_fifo_file, 'w')
					f.close()
				except Exception,e:
					logger.warn('mot-encoder Fail to create file %s, error: %s' % (self.config.mot_dls_fifo_file, e))
					return False
			else:
				f = open(self.config.mot_dls_fifo_file, 'w')
				f.write('')
				f.close()
				
			# Check if config.mot_pad_fifo_file exist and create it if needed.
			if not os.path.isfile(self.config.mot_pad_fifo_file):
				try:
					f = open(self.config.mot_pad_fifo_file, 'w')
					f.close()
				except Exception,e:
					logger.warn('mot-encoder Fail to create file %s, error: %s' % (self.config.mot_pad_fifo_file, e))
					return False
			else:
				f = open(self.config.mot_pad_fifo_file, 'w')
				f.write('')
				f.close()
			
			args += ' --pad=%s' % (self.config.mot_pad)
			args += ' --dls=%s' % (self.config.mot_dls_fifo_file)
			args += ' --output=%s' % (self.config.mot_pad_fifo_file)
			
				
			args = args.split()
			motencoderProcessProtocol = MyMotEncoderProcessProtocol(self)
			reactor.spawnProcess(motencoderProcessProtocol, executable, args, {})
	
	def stop_mot(self, autorestart=True):
		self.autorestart = autorestart
		if self.motProcess:
			self.motProcess.transport.signalProcess(SIGKILL)


class MyEncoderProcessProtocol(protocol.ProcessProtocol):
	def __init__(self, manager):
		self.manager = manager
		
	def connectionMade(self):
		logger.info('dabplus-enc connection made!')
		self.manager.encoderProcess = self
		
	def processEnded(self, reason):
		logger.info('dabplus-enc process ended, status %s' % (reason.value.exitCode))
		logger.debug('dabplus-enc autorestart value : %s' % (self.manager.autorestart))
		self.manager.encoderProcess = None
		# Stop mot (restart itself)
		self.manager.stop_mot(self.manager.autorestart)
		if self.manager.autorestart == True:
			# Restart encoder
			self.manager.run_encoder()

class MyMotEncoderProcessProtocol(protocol.ProcessProtocol):
	def __init__(self, manager):
		self.manager = manager
	
	def connectionMade(self):
		logger.info('mot-encoder connection made!')
		self.manager.motProcess = self

	def processEnded(self, reason):
		logger.info('mot-encoder process ended, status %s' % (reason.value.exitCode))
		logger.debug('mot-encoder autorestart value : %s' % (self.manager.autorestart))
		self.manager.motProcess = None
		# Restart mot
		if self.manager.autorestart == True:
			self.manager.run_mot()
			
class EncoderTelnetFactory(ServerFactory):
	def __init__(self, manager):
		self.manager = manager

class EncoderTelnetProtocol(LineReceiver):
	def connectionMade(self):
		self._peer = self.transport.getPeer().host
		logger.info('TELNET : Connection from %s' % (self._peer))
		
	def connectionLost(self, e):
		logger.info('TELNET : Lost connection from %s' % (self._peer))
	
	def lineReceived(self, line):
		if line == "status":
			logger.info('TELNET : Receive from %s command : %s' % (self._peer, line))
			for process, status in self.factory.manager.getStatus().iteritems():
				self.transport.write('%s: %s (pid:%s)\n' % (process, status['status'], status['pid']))
			self.transport.write('Ok\n')
		
		elif line == "restart":
			logger.info('TELNET : Receive from %s command : %s' % (self._peer, line))
			self.factory.manager.stop_encoder()
			self.factory.manager.stop_mot()
			time.sleep(0.5)
			if not self.factory.manager.motProcess:
				self.factory.manager.run_mot()
			time.sleep(0.1)
			if not self.factory.manager.encoderProcess:
				self.factory.manager.run_encoder()
			self.transport.write('Ok\n')
		
		elif line == "start":
			logger.info('TELNET : Receive from %s command : %s' % (self._peer, line))
			if not self.factory.manager.motProcess:
				self.factory.manager.run_mot()
			time.sleep(0.1)
			if not self.factory.manager.encoderProcess:
				self.factory.manager.run_encoder()
			self.transport.write('Ok\n')
		
		elif line == "stop":
			logger.info('TELNET : Receive from %s command : %s' % (self._peer, line))
			self.factory.manager.stop_encoder(None)
			self.factory.manager.stop_mot(None)
			self.transport.write('Ok\n')
		
		elif line == "reload_config":
			logger.info('TELNET : Receive from %s command : %s' % (self._peer, line))
			self.factory.manager.reload_config()
			self.transport.write('Ok\n')
			
		elif line == "show_config":
			logger.info('TELNET : Receive from %s command : %s' % (self._peer, line))
			self.transport.write(config.DisplayConfig())
			self.transport.write('\n')
			self.transport.write('Ok\n')
		
		elif line == "shutdown":
			logger.info('TELNET : Receive from %s command : %s' % (self._peer, line))
			self.factory.manager.stop_encoder(None)
			self.factory.manager.stop_mot(None)
			self.transport.write('Ok\n')
			reactor.stop()
		
		elif line == "exit":
			logger.info('TELNET : Receive from %s command : %s' % (self._peer, line))
			self.transport.loseConnection()
			
		elif line == "help":
			logger.info('TELNET : Receive from %s command : %s' % (self._peer, line))
			self.transport.write('Available command :\n')
			self.transport.write('-\n')
			self.transport.write('help          :  Display this help\n')
			self.transport.write('status        :  Display process status\n')
			self.transport.write('stop          :  Stop dabplus-enc & mot-encoder process\n')
			self.transport.write('start         :  Start dabplus-enc & mot-encoder process\n')
			self.transport.write('restart       :  Restart dabplus-enc & mot-encoder process\n')
			self.transport.write('reload_config :  Reload configuration from configuration file\n')
			self.transport.write('show_config   :  Display running configuration\n')
			self.transport.write('shutdown      :  WARNING : Stop dabplus-enc & mot-encoder process, and close Encoder Manager!\n')
			self.transport.write('exit          :  Close telnet connection\n')
			self.transport.write('Ok\n')
			
		else:
			logger.warn('TELNET : Receive from %s an unknown command : %s' % (self._peer, line))
			self.transport.write('Unknown command.\n')
			self.transport.write('Please use help to display all available command.\n')
			self.transport.write('Ok\n')




class EncoderRPC(jsonrpc.JSONRPC):
	def __init__(self, manager):
		self.manager = manager
	
	def render(self, request):
		request.content.seek(0, 0)
		# Unmarshal the JSON-RPC data.
		content = request.content.read()
		parsed = jsonrpclib.loads(content)
		functionPath = parsed.get("method")
		args = parsed.get('params')
		id = parsed.get('id')
		version = parsed.get('jsonrpc')
		if version:
			version = int(float(version))
		elif id and not version:
			version = jsonrpclib.VERSION_1
		else:
			version = jsonrpclib.VERSION_PRE1
		# XXX this all needs to be re-worked to support logic for multiple
		# versions...
		try:
			function = self._getFunction(functionPath)
		except jsonrpclib.Fault, f:
			self._cbRender(f, request, id, version)
		else:
			request.setHeader("content-type", "text/json")
			d = defer.maybeDeferred(function, *args, **{"request":request})
			d.addErrback(self._ebRender, id)
			d.addCallback(self._cbRender, request, id, version)
		return server.NOT_DONE_YET
	
	def jsonrpc_status(self, request):
		logger.info('JSONRPC : Receive from %s command : status' % (request.client.host))
		return self.manager.getStatus()
	
	def jsonrpc_start(self, request):
		logger.info('JSONRPC : Receive from %s command : start' % (request.client.host))
		if not self.manager.motProcess:
			self.manager.run_mot()
		time.sleep(0.1)
		if not self.manager.encoderProcess:
			self.manager.run_encoder()
		return 'encoder started'
	
	def jsonrpc_stop(self, request):
		logger.info('JSONRPC : Receive from %s command : stop' % (request.client.host))
		self.manager.stop_encoder(None)
		self.manager.stop_mot(None)
		return 'encoder stopped'

	def jsonrpc_restart(self, request):
		logger.info('JSONRPC : Receive from %s command : restart' % (request.client.host))
		self.manager.stop_encoder()
		self.manager.stop_mot()
		time.sleep(0.5)
		if not self.manager.motProcess:
			self.manager.run_mot()
		time.sleep(0.1)
		if not self.manager.encoderProcess:
			self.manager.run_encoder()
		return 'encoder restart'
	
	def jsonrpc_reload_config(self, request):
		logger.info('JSONRPC : Receive from %s command : reload_config' % (request.client.host))
		self.manager.reload_config()
		return 'encoder reload_config'
		
	def jsonrpc_show_config(self, request):
		logger.info('JSONRPC : Receive from %s command : show_config' % (request.client.host))
		return config.getConfig()
		
	def jsonrpc_set_config(self, cparam, request):
		logger.info('JSONRPC : Receive from %s command : set_config' % (request.client.host))
		config.setConfig(cparam['config'])
		return 'encoder set_config'
	
	def jsonrpc_set_dls(self, cparam, request):
		logger.info('JSONRPC : Receive from %s command : set_dls' % (request.client.host))
		dls = cparam['dls'].encode('utf-8')
		r = self.manager.set_dls(dls)
		return 'encoder set_dls ('+r+')'
	
	def jsonrpc_get_dls(self, request):
		logger.info('JSONRPC : Receive from %s command : get_dls' % (request.client.host))
		return self.manager.get_dls()


def signal_handler(signal, frame):
	logger.info('Ctrl+C pressed')
	manager.autorestart = None
	reactor.stop()
			
if __name__ == '__main__':
	# Get configuration file in argument
	parser = argparse.ArgumentParser(description='ODR Encoder Manager')
	parser.add_argument('-c','--config', help='configuration filename',required=True)
	parser.add_argument('-l','--log_dir', help='path of logs directory',required=True)
	parser.add_argument('--log_level', default='info', help='level of log. This parameters can take value : debug, info, warning, error, critical (default : info)',required=False)
	cli_args = parser.parse_args()
	
	# Check if configuration exist and is readable
	if os.path.isfile(cli_args.config) and os.access(cli_args.config, os.R_OK):
		print "Use configuration file %s" % (cli_args.config)
	else:
		print "Configuration file is missing or is not readable - %s" % (cli_args.config)
		sys.exit(1)
	
	# Check if log_dir exist and is writeable
	if os.path.isdir(cli_args.log_dir) and os.access(cli_args.log_dir, os.W_OK):
		print "Use logging directory %s" % (cli_args.log_dir)
	else:
		print "Log directory not exist or is not writeable - %s" % (cli_args.log_dir)
		sys.exit(1)
	
	# Logginf configuration
	LEVELS = {
		'debug': logging.DEBUG,
		'info': logging.INFO,
		'warning': logging.WARNING,
		'error': logging.ERROR,
		'critical': logging.CRITICAL
	}
	logHandler = TimedRotatingFileHandler(cli_args.log_dir+'/encoder.log', when="midnight", interval=1, backupCount=30)
	logFormatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s','%Y-%m-%d %H:%M:%S')
	logHandler.setFormatter( logFormatter )
	logHandler.suffix = "%Y-%m-%d"
	logger = logging.getLogger('ODR-EncoderManager')
	logger.addHandler( logHandler )
	logger.setLevel( LEVELS.get(cli_args.log_level, logging.NOTSET) )
	
	# Load configuration
	config = Config(cli_args.config, logger)
	
	# Load Encoder Manager class
	manager = EncoderManager(cli_args.config)
	
	# Start process
	manager.run_mot()
	time.sleep(0.5)
	manager.run_encoder()
	
	# Start telnet protocol
	sfTelnet = EncoderTelnetFactory(manager)
	sfTelnet.protocol = EncoderTelnetProtocol
	reactor.listenTCP(int(config.telnet_port), sfTelnet, backlog=50, interface=config.telnet_bind_ip)
	
	# Start JSON RPC protocol
	site = server.Site(EncoderRPC(manager))
	site.displayTracebacks = False
	reactor.listenTCP(int(config.rpc_port), site, backlog=50, interface=config.rpc_bind_ip)
	
	# Catch Ctrl+C
	signal.signal(signal.SIGINT, signal_handler)
	
	# Run Reactor process
	reactor.run() 
	
	print 'ODR Encoder Manager Exited'
	