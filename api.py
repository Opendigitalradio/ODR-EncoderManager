#!/usr/bin/python

# -*- coding: utf-8 -*-
import cherrypy
from datetime import datetime
from datetime import timedelta
import json
import os

import argparse


# ---------- API ------------------------------------------------------------

class api(object):
	def __init__(self):
		pass
		
	def index(self):
		output = '<h1>ODR - Encoder Manager API</h1>'
		output += '<ul>'
		output += '<li><a href="/api/metadata">metadata</a> : Put metadata</li>'
		output += '</ul>'
		return output
	index.exposed = True
	
	def config(self):
		output = 'config'
		return output
	config.exposed = True
	
	def metadata(self):
		output = 'metadata'
		return output
	metadata.exposed = True


# ---------- MAIN ------------------------------------------------------------
class root(object):
	def __init__(self):
		self.api = api()
		
	def index(self):
		raise cherrypy.HTTPRedirect('/home')
	index.exposed = True
	
	def default(self, attr='abc'):
		return "Page not Found!"
	default.exposed = True



	
if __name__ == '__main__':
	# Get configuration file in argument
	parser = argparse.ArgumentParser(description='ODR WebGUI Encoder Manager')
	parser.add_argument('-s','--static-dir', help='Fulle path of static directory content',required=True)
	parser.add_argument('-l','--log-dir', help='log directory full path',required=True)
	parser.add_argument('--host', help='socket host (default: 0.0.0.0)',required=False)
	parser.add_argument('--port', help='socket port (default: 8080)',required=False)
	parser.add_argument('--rpc-host', help='encoder RPC host (default: 127.0.0.1)',required=False)
	parser.add_argument('--rpc-port', help='encoder RPC port (default: 7780)',required=False)
	cli_args = parser.parse_args()
	
	
	cherrypy.process.plugins.Daemonizer(cherrypy.engine).subscribe()
	cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8080, 'request.show_tracebacks' : True, })
	cherrypy.quickstart(root(),config={
  '/':
		{ 'log.access_file' : './access.log',
		'log.screen': False,
		'tools.sessions.on': True
		},
  '/home':
		{ 'log.access_file' : './access.log',
		'log.screen': False,
		'tools.sessions.on': True,
		'tools.staticfile.on': True,
		'tools.staticfile.filename': os.path.join(os.path.abspath("."), u"static/home.html")
		},
  '/config':
		{ 'log.access_file' : './access.log',
		'log.screen': False,
		'tools.sessions.on': True,
		'tools.staticfile.on': True,
		'tools.staticfile.filename': os.path.join(os.path.abspath("."), u"static/config.html")
		},
  '/css':
		{ 'log.access_file' : './access.log',
		'log.screen': False,
		'tools.sessions.on': True,
		'tools.staticdir.on': True,
		'tools.staticdir.dir': os.path.join(os.path.abspath("."), u"static/css/")
		},
  '/js':
		{ 'log.access_file' : './access.log',
		'log.screen': False,
		'tools.sessions.on': True,
		'tools.staticdir.on': True,
		'tools.staticdir.dir': os.path.join(os.path.abspath("."), u"static/js/")
		},
  '/fonts':
		{ 'log.access_file' : './access.log',
		'log.screen': False,
		'tools.sessions.on': True,
		'tools.staticdir.on': True,
		'tools.staticdir.dir': os.path.join(os.path.abspath("."), u"static/fonts/")
		},
  })
