#!/usr/bin/python

# -*- coding: utf-8 -*-
import cherrypy
from datetime import datetime
from datetime import timedelta
import json
import os
import sys

import argparse
import requests

# ---------- API ------------------------------------------------------------

class API:
	exposed = True
	def __init__(self):
		self.getConfig = getConfig()
		self.setConfig = setConfig()
		self.getStatus = getStatus()
		self.start = start()
		self.stop = stop()
		self.restart = restart()

	def GET(self):
		return "api - Your IP is %s " % ( cherrypy.request.remote.ip )


class getConfig:
	exposed = True
	def __init__(self):
		pass

	def GET(self):
		r = rpc_request()
		return json.dumps(r.call('show_config'))
		
class setConfig:
	exposed = True
	def __init__(self):
		pass

	def POST(self):
		cl = cherrypy.request.headers['Content-Length']
		rawbody = cherrypy.request.body.read(int(cl))
		body = json.loads(rawbody)
		        
		r = rpc_request()
		rpcconfig = [ { "config" : body } ]
		return json.dumps(r.call('set_config', rpcconfig))

		
class getStatus:
	exposed = True
	def __init__(self):
		pass
	
	def GET(self):
		r = rpc_request()
		return json.dumps(r.call('status'))

class start:
	exposed = True
	def __init__(self):
		pass
	
	def GET(self):
		r = rpc_request()
		return json.dumps(r.call('start'))
		
class stop:
	exposed = True
	def __init__(self):
		pass
	
	def GET(self):
		r = rpc_request()
		return json.dumps(r.call('stop'))
		
class restart:
	exposed = True
	def __init__(self):
		pass
	
	def GET(self):
		r = rpc_request()
		return json.dumps(r.call('restart'))

# ---------- RPC -------------------------------------------------------------

class rpc_request:
	def __init__(self):
		self.rpc_uri = 'http://%s:%s/' % (cli_args.rpc_host, cli_args.rpc_port)
		self.rpc_headers = {'content-type': 'application/json'}
	
	def call(self, method, param=[]):
		payload = {
			"method": method,
			"params": param,
			"jsonrpc": "2.0",
			"id": 0,
		}
		try:
			response = requests.post( self.rpc_uri, data=json.dumps(payload), headers=self.rpc_headers).json()
			return response["result"]
		except Exception,e:
			return e.message

# ---------- MAIN ------------------------------------------------------------
class root(object):
	def __init__(self):
		#self.api = API()
		pass
		
	def index(self):
		raise cherrypy.HTTPRedirect('/home')
	index.exposed = True
	
	def default(self, attr='abc'):
		return "Page not Found!"
	default.exposed = True



	
if __name__ == '__main__':
	# Get configuration file in argument
	parser = argparse.ArgumentParser(description='ODR WebGUI Encoder Manager')
	parser.add_argument('-s','--static_dir', help='Full path of static directory content',required=True)
	parser.add_argument('-l','--log_dir', help='log directory full path',required=True)
	parser.add_argument('--host', default='0.0.0.0', help='socket host (default: 0.0.0.0)',required=False)
	parser.add_argument('--port', default='8080', help='socket port (default: 8080)',required=False)
	parser.add_argument('--rpc_host', default='127.0.0.1', help='encoder RPC host (default: 127.0.0.1)',required=False)
	parser.add_argument('--rpc_port', default='7080', help='encoder RPC port (default: 7780)',required=False)
	cli_args = parser.parse_args()
	
	# Check if log_dir exist and is writeable
	if os.path.isdir(cli_args.log_dir) and os.access(cli_args.log_dir, os.W_OK):
		print "Use logging directory %s" % (cli_args.log_dir)
	else:
		print "Log directory not exist or is not writeable - %s" % (cli_args.log_dir)
		sys.exit(1)
	
	# Check if static_dir exist and is readeable
	if os.path.isdir(cli_args.static_dir) and os.access(cli_args.static_dir, os.R_OK):
		print "Use static directory %s" % (cli_args.static_dir)
	else:
		print "Static directory not exist or is not readeable - %s" % (cli_args.static_dir)
		sys.exit(1)
	
	# Start cherrypy
	cherrypy.process.plugins.Daemonizer(cherrypy.engine).subscribe()
	cherrypy.config.update({'server.socket_host': cli_args.host, 'server.socket_port': int(cli_args.port), 'request.show_tracebacks' : True, })
	cherrypy.tree.mount(
		API(), '/api/',
			{'/':
				{'log.access_file' : os.path.join(cli_args.log_dir, 'access.log'),
				'log.screen': False,
				'tools.sessions.on': True,
				'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
			}
		)
	cherrypy.quickstart(root(),config={
		'/':
				{ 'log.access_file' : os.path.join(cli_args.log_dir, 'access.log'),
				'log.screen': False,
				'tools.sessions.on': True
				},
		'/home':
				{ 'log.access_file' : os.path.join(cli_args.log_dir, 'access.log'),
				'log.screen': False,
				'tools.sessions.on': True,
				'tools.staticfile.on': True,
				'tools.staticfile.filename': os.path.join(os.path.abspath("."), u"static/home.html")
				},
		'/status':
				{ 'log.access_file' : os.path.join(cli_args.log_dir, 'access.log'),
				'log.screen': False,
				'tools.sessions.on': True,
				'tools.staticfile.on': True,
				'tools.staticfile.filename': os.path.join(os.path.abspath("."), u"static/status.html")
				},
		'/config':
				{ 'log.access_file' : os.path.join(cli_args.log_dir, 'access.log'),
				'log.screen': False,
				'tools.sessions.on': True,
				'tools.staticfile.on': True,
				'tools.staticfile.filename': os.path.join(os.path.abspath("."), u"static/config.html")
				},
		'/css':
				{ 'log.access_file' : os.path.join(cli_args.log_dir, 'access.log'),
				'log.screen': False,
				'tools.sessions.on': True,
				'tools.staticdir.on': True,
				'tools.staticdir.dir': os.path.join(os.path.abspath("."), u"static/css/")
				},
		'/js':
				{ 'log.access_file' : os.path.join(cli_args.log_dir, 'access.log'),
				'log.screen': False,
				'tools.sessions.on': True,
				'tools.staticdir.on': True,
				'tools.staticdir.dir': os.path.join(os.path.abspath("."), u"static/js/")
				},
		'/fonts':
				{ 'log.access_file' : os.path.join(cli_args.log_dir, 'access.log'),
				'log.screen': False,
				'tools.sessions.on': True,
				'tools.staticdir.on': True,
				'tools.staticdir.dir': os.path.join(os.path.abspath("."), u"static/fonts/")
				},
	})
