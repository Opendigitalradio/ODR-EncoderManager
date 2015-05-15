#!/usr/bin/env python

import os
import sys
import argparse

from twisted.internet import protocol
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver

from txjsonrpc.web import jsonrpc
from twisted.web import server

from twisted.internet import reactor
import re
import time

import json

from config import Config

import signal
from signal import SIGKILL



class EncoderManager():
	def __init__(self, configFile):
		self.encoderProcess = None
		self.motProcess = None
		self.configFile = configFile
		self.config = Config(self.configFile)
		self.autorestart = True
	
	def get_dls(self):
		try:
			f = open(self.config.mot_dls_fifo_file, 'r')
			dls = f.read()
			f.close()
		except Exception,e:
			print 'get_dls Fail to read dls data in file %s, error: %s' % (self.config.mot_dls_fifo_file, e)
			return str(e)
		else:
			return {'dls': str(dls)}

	def set_dls(self, dls=''):
		try:
			f = open(self.config.mot_dls_fifo_file, 'w')
			f.write(dls)
			f.close()
		except Exception,e:
			print 'set_dls Fail to write dls data in file %s, error: %s' % (self.config.mot_dls_fifo_file, e)
			return str(e)
		else:
			return dls
	
	def reload_config(self):
		self.config = Config(self.configFile)
	
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
				print 'dabplus-enc File %s not exist. Trying to create it.' % (self.config.mot_pad_fifo_file)
				try:
					f = open(self.config.mot_pad_fifo_file, 'w')
					f.close()
				except Exception,e:
					print 'dabplus-enc Fail to create file %s, error: %s, Ignoring pad parameters' % (self.config.mot_pad_fifo_file, e)
				else:
					print 'dabplus-enc File %s is created.' % (self.config.mot_pad_fifo_file)
					args += ' --pad=%s' % (self.config.mot_pad)
					args += ' --pad-fifo=%s' % (self.config.mot_pad_fifo_file)
			else:
				args += ' --pad=%s' % (self.config.mot_pad)
				args += ' --pad-fifo=%s' % (self.config.mot_pad_fifo_file)
		
		args += ' -f raw -o tcp://%s:%s' % (self.config.output_host, self.config.output_port)
		if self.config.output_key_file.strip() != '':
			if os.path.isfile(self.config.output_key_file):
				args += ' -k %s' % (self.config.output_key_file)
			else:
				print 'dabplus-enc ZMQ secret key file not found or not readable. Ignoring this file and secret-key parameters.'
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
					print 'mot-encoder Slide directory not exist or not readable. Ignoring slide directory parameters - %s' % (self.config.mot_slide_directory)
				else:
					args += ' --dir=%s' % (self.config.mot_slide_directory)
					if self.config.mot_slide_once == True:
						args += ' --erase'
						
			# Check if config.mot_dls_fifo_file exist and create it if needed.
			if not os.path.isfile(self.config.mot_dls_fifo_file):
				try:
					f = open(self.config.mot_dls_fifo_file, 'w')
					f.close()
				except Exception,e:
					print 'mot-encoder Fail to create file %s, error: %s' % (self.config.mot_dls_fifo_file, e)
					return False
			
			# Check if config.mot_pad_fifo_file exist and create it if needed.
			if not os.path.isfile(self.config.mot_pad_fifo_file):
				try:
					f = open(self.config.mot_pad_fifo_file, 'w')
					f.close()
				except Exception,e:
					print 'mot-encoder Fail to create file %s, error: %s' % (self.config.mot_pad_fifo_file, e)
					return False
			
			args += ' --pad=%s' % (self.config.mot_pad)
			args += ' --dls=%s' % (self.config.mot_dls_fifo_file)
			args += ' --output=%s' % (self.config.mot_pad_fifo_file)
			args += ' --sleep=%s' % (self.config.mot_slide_sleeping)
			
				
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
		print "dabplus-enc connection made!"
		self.manager.encoderProcess = self
		
	def processEnded(self, reason):
		print "dabplus-enc process ended, status %s" % (reason.value.exitCode)
		#print "encoder autorestart: %s" % (self.manager.autorestart)
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
		print "mot-encoder connection made!"
		self.manager.motProcess = self

	def processEnded(self, reason):
		print "mot-encoder process ended, status %s" % (reason.value.exitCode)
		#print "encoder autorestart: %s" % (self.manager.autorestart)
		self.manager.motProcess = None
		# Restart mot
		if self.manager.autorestart == True:
			self.manager.run_mot()
			
class EncoderTelnetFactory(ServerFactory):
	def __init__(self, manager):
		self.manager = manager

class EncoderTelnetProtocol(LineReceiver):
	def connectionMade(self):
		self._peer = self.transport.getPeer()
		print 'Connection from %s' % (self._peer)
		
	def connectionLost(self, e):
		print 'Lost connection from %s' % (self._peer)
	
	def lineReceived(self, line):
		if line == "status":
			print '%s - %s' % (self._peer, line)
			for process, status in self.factory.manager.getStatus().iteritems():
				self.transport.write('%s: %s (pid:%s)\n' % (process, status['status'], status['pid']))
			self.transport.write('Ok\n')
		
		elif line == "restart":
			print '%s - %s' % (self._peer, line)
			self.factory.manager.stop_encoder()
			self.factory.manager.stop_mot()
			time.sleep(0.5)
			if not self.factory.manager.encoderProcess:
				self.factory.manager.run_encoder()
			if not self.factory.manager.motProcess:
				self.factory.manager.run_mot()
			self.transport.write('Ok\n')
		
		elif line == "start":
			print '%s - %s' % (self._peer, line)
			if not self.factory.manager.encoderProcess:
				self.factory.manager.run_encoder()
			if not self.factory.manager.motProcess:
				self.factory.manager.run_mot()
			self.transport.write('Ok\n')
		
		elif line == "stop":
			print '%s - %s' % (self._peer, line)
			self.factory.manager.stop_encoder(None)
			self.factory.manager.stop_mot(None)
			self.transport.write('Ok\n')
		
		elif line == "reload_config":
			print '%s - %s' % (self._peer, line)
			self.factory.manager.reload_config()
			self.transport.write('Ok\n')
			
		elif line == "show_config":
			print '%s - %s' % (self._peer, line)
			self.transport.write(config.DisplayConfig())
			self.transport.write('\n')
			self.transport.write('Ok\n')
		
		elif line == "shutdown":
			print '%s - %s' % (self._peer, line)
			self.factory.manager.stop_encoder(None)
			self.factory.manager.stop_mot(None)
			self.transport.write('Ok\n')
			reactor.stop()
		
		elif line == "exit":
			print '%s - %s' % (self._peer, line)
			self.transport.loseConnection()
			
		elif line == "help":
			print '%s - %s' % (self._peer, line)
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
			print '%s - Unknown command : %s' % (self._peer, line)
			self.transport.write('Unknown command.\n')
			self.transport.write('Please use help to display all available command.\n')
			self.transport.write('Ok\n')




class EncoderRPC(jsonrpc.JSONRPC):
	def __init__(self, manager):
		self.manager = manager
	
		
	#def jsonrpc_add(self, a, b):
		#return 'encoder %s' % (a + b)
	
	def jsonrpc_status(self):
		return self.manager.getStatus()
	
	def jsonrpc_start(self):
		if not self.manager.encoderProcess:
			self.manager.run_encoder()
		if not self.manager.motProcess:
			self.manager.run_mot()
		return 'encoder started'
	
	def jsonrpc_stop(self):
		self.manager.stop_encoder(None)
		self.manager.stop_mot(None)
		return 'encoder stopped'

	def jsonrpc_restart(self):
		self.manager.stop_encoder()
		self.manager.stop_mot()
		time.sleep(0.5)
		if not self.manager.encoderProcess:
			self.manager.run_encoder()
		if not self.manager.motProcess:
			self.manager.run_mot()
		return 'encoder restart'
	
	def jsonrpc_reload_config(self):
		self.manager.reload_config()
		return 'encoder reload_config'
		
	def jsonrpc_show_config(self):
		return config.getConfig()
		
	def jsonrpc_set_config(self, cparam):
		config.setConfig(cparam['config'])
		#return cparam['config']
		return 'encoder set_config'
	
	def jsonrpc_set_dls(self, cparam):
		dls = cparam['dls']
		r = self.manager.set_dls(dls)
		return 'encoder set_dls set to value : '+dls+' ('+r+')'
	
	def jsonrpc_get_dls(self):
		return self.manager.get_dls()
	      

	

def signal_handler(signal, frame):
	print('You pressed Ctrl+C!')
	manager.autorestart = None
	reactor.stop()
			
if __name__ == '__main__':
	# Get configuration file in argument
	parser = argparse.ArgumentParser(description='DAB Plus encoder')
	parser.add_argument('-c','--config', help='Configuration file name',required=True)
	cli_args = parser.parse_args()
	
	# Check if configuration exist and is readable
	if os.path.isfile(cli_args.config) and os.access(cli_args.config, os.R_OK):
		print "Use configuration file %s" % (cli_args.config)
	else:
		print "Configuration file is missing or is not readable - %s" % (cli_args.config)
		sys.exit(1)
	
	# Load configuration
	config = Config(cli_args.config)
	
	# Load Encoder Manager class
	manager = EncoderManager(cli_args.config)
	
	# Start process
	manager.run_encoder()
	manager.run_mot()
	
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
	
	print 'ODR encoder Manager Exited'
	