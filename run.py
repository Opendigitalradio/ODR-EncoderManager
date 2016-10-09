import cherrypy
import argparse
import os
import sys

from auth import AuthController, require, member_of, name_is, is_login
from api import API

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))

class RestrictedArea:
	
	# all methods in this controller (and subcontrollers) is
	# open only to members of the admin group
	
	_cp_config = {
		'auth.require': [member_of('admin')]
	}
	
	@cherrypy.expose
	def index(self):
		return """This is the admin only area."""


class Root:
	
	_cp_config = {
		'tools.sessions.on': True,
		'tools.auth.on': True
	}
	
	auth = AuthController()
	
	restricted = RestrictedArea()
	api = API()
	
	# This is available for all authenticated or not user
	@cherrypy.expose
	def index(self):
		raise cherrypy.HTTPRedirect('/home')
	
	@cherrypy.expose
	def home(self):
		tmpl = env.get_template("home.html")
		return tmpl.render(is_login=is_login())
	
	@cherrypy.expose
	def help(self):
		tmpl = env.get_template("help.html")
		return tmpl.render(is_login=is_login())
	
	@cherrypy.expose
	def about(self):
		tmpl = env.get_template("about.html")
		return tmpl.render(is_login=is_login())
	
	# This is only available for authenticated user
	@cherrypy.expose
	@require()
	def status(self):
		tmpl = env.get_template("status.html")
		return tmpl.render(is_login=is_login())
	
	# This is only available for user in group admin
	@cherrypy.expose
	@require(member_of("admin"))
	def config(self):
		tmpl = env.get_template("config.html")
		return tmpl.render(is_login=is_login())


if __name__ == '__main__':
	# Get configuration file in argument
	parser = argparse.ArgumentParser(description='ODR Encoder Manager (WebGUI)')
	parser.add_argument('-s','--static_dir', help='Absolute path of static directory content',required=True)
	parser.add_argument('-l','--log_dir', help='Absolute path of logs directory',required=True)
	parser.add_argument('--daemon', help='run as daemon', action="store_true")
	parser.add_argument('--host', default='0.0.0.0', help='socket host (default: 0.0.0.0)',required=False)
	parser.add_argument('--port', default='8080', help='socket port (default: 8080)',required=False)
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
	if cli_args.daemon:
		cherrypy.process.plugins.Daemonizer(cherrypy.engine).subscribe()
	
	cherrypy.config.update({
		'server.socket_host': cli_args.host,
		'server.socket_port': int(cli_args.port),
		'request.show_tracebacks' : True,
		'environment': 'production',
		'tools.sessions.on': True,
		#'tools.encode.on': True,
		#'tools.encode.encoding': "utf-8",
		'log.access_file' : os.path.join(cli_args.log_dir, 'access.log'),
		'log.error_file' : os.path.join(cli_args.log_dir, 'error.log'),
		'log.screen': False,
		})
	
	cherrypy.tree.mount(
		Root(), config={
			'/':
					{ 
					},
			'/css':
					{ 
					'tools.staticdir.on': True,
					'tools.staticdir.dir': os.path.join(cli_args.static_dir, u"css/")
					},
			'/js':
					{ 
					'tools.staticdir.on': True,
					'tools.staticdir.dir': os.path.join(cli_args.static_dir, u"js/")
					},
			'/fonts':
					{ 
					'tools.staticdir.on': True,
					'tools.staticdir.dir': os.path.join(cli_args.static_dir, u"fonts/")
					},
			'/favicon.ico':
					{ 
					'tools.staticfile.on': True,
					'tools.staticfile.filename': os.path.join(cli_args.static_dir, u"fonts/favicon.ico")
					},
		}
	)
	
	#cherrypy.engine.signal_handler.handlers["SIGINT"] = handle_sigint
	
	cherrypy.engine.start()
	cherrypy.engine.block()
	
    #cherrypy.quickstart(Root())