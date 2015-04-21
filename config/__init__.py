#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser
import os
import sys

class Config():
	def __init__(self,config_file):
		self.config = ConfigParser.ConfigParser()
		self.config.read(config_file)
		
		self.source_type = self.ConfigSectionMap('source')['type']
		
		# Global configuration
		self.global_encoder_path = self.ConfigSectionMap('global')['encoder_path']
		self.global_mot_path = self.ConfigSectionMap('global')['mot_path']
		
		# Telnet configuration
		self.telnet_port = self.ConfigSectionMap('telnet')['port']
		self.telnet_bind_ip = self.ConfigSectionMap('telnet')['bind_ip']
		
		# Source configuration
		if self.source_type == 'alsa':
			self.source_device = self.ConfigSectionMap('source')['device']
			if self.ConfigSectionMap('source')['driftcomp'].upper() == 'TRUE':
				self.source_driftcomp = True
			else:
				self.source_driftcomp = False
		if self.source_type == 'stream':
			self.source_url = self.ConfigSectionMap('source')['url']
			self.source_volume = self.ConfigSectionMap('source')['volume']
		
		# Output configuration
		self.output_host = self.ConfigSectionMap('output')['host']
		self.output_port = self.ConfigSectionMap('output')['port']
		self.output_key_file = self.ConfigSectionMap('output')['key_file']
		
		self.output_samplerate = self.ConfigSectionMap('output')['samplerate']
		self.output_bitrate = self.ConfigSectionMap('output')['bitrate']
		if self.ConfigSectionMap('output')['sbr'].upper() == 'TRUE':
			self.output_sbr = True
		else:
			self.output_sbr = False
		if self.ConfigSectionMap('output')['ps'].upper() == 'TRUE':
			self.output_ps = True
		else:
			self.output_ps = False
		if self.ConfigSectionMap('output')['afterburner'].upper() == 'TRUE':
			self.output_afterburner = True
		else:
			self.output_afterburner = False
		
		# MOT configuration
		if self.ConfigSectionMap('mot')['enable'].upper() == 'TRUE':
			self.mot = True
			self.mot_pad = self.ConfigSectionMap('mot')['pad']
			self.mot_pad_fifo_file = self.ConfigSectionMap('mot')['pad_fifo_file']
			self.mot_dls_fifo_file = self.ConfigSectionMap('mot')['dls_fifo_file']
			self.mot_slide_directory = self.ConfigSectionMap('mot')['slide_directory']
			self.mot_slide_sleeping = self.ConfigSectionMap('mot')['slide_sleeping']
			if self.ConfigSectionMap('mot')['slide_once'].upper() == 'TRUE':
				self.mot_slide_once = True
			else:
				self.mot_slide_once = False
		else:
			self.mot = False
			
	def DisplayConfig(self, section=None):
		output = ''
		for section_name in self.config.sections():
			output += 'Section: %s\n' % (section_name)
			#output += '  Options:', self.config.options(section_name)
			for name, value in self.config.items(section_name):
				output += '  %s = %s\n' % (name, value)
		return output

	def ConfigSectionMap(self, section):
		dict1 = {}
		options = self.config.options(section)
		for option in options:
			try:
				dict1[option] = self.config.get(section, option)
				if dict1[option] == -1:
						DebugPrint("skip: %s" % option)
			except:
				print("exception on %s!" % option)
				dict1[option] = None
		return dict1