#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cherrypy
import argparse
import os
import sys

from config import Config, is_network
from auth import AuthController, require, is_login
from api import API

import signal
import time

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))


class Root():
        def __init__(self, config_file):
                self.config_file = config_file
                self.conf = Config(self.config_file)
                self.auth = AuthController(self.config_file)
                self.api = API(self.config_file)

        _cp_config = {
                'tools.sessions.on': True,
                'tools.auth.on': True
        }

        # This is available for all authenticated or not user
        @cherrypy.expose
        def index(self):
                raise cherrypy.HTTPRedirect('/home')

        @cherrypy.expose
        def home(self):
                tmpl = env.get_template("home.html")
                js = []
                return tmpl.render(tab='home', js=js, is_login=is_login(), is_network=is_network(self.config_file))

        @cherrypy.expose
        def help(self):
                tmpl = env.get_template("help.html")
                js = []
                return tmpl.render(tab='help', js=js, is_login=is_login(), is_network=is_network(self.config_file))

        @cherrypy.expose
        def about(self):
                tmpl = env.get_template("about.html")
                js = []
                return tmpl.render(tab='about', js=js, is_login=is_login(), is_network=is_network(self.config_file))

        # This is only available for authenticated user
        @cherrypy.expose
        @require()
        def status(self):
                tmpl = env.get_template("status.html")
                js = ['/js/odr-status.js']
                return tmpl.render(tab='status', js=js, is_login=is_login(), is_network=is_network(self.config_file))

        @cherrypy.expose
        @require()
        def config(self):
                tmpl = env.get_template("config.html")
                js = ['/js/odr-config.js']
                return tmpl.render(tab='config', js=js, is_login=is_login(), is_network=is_network(self.config_file))

        @cherrypy.expose
        @require()
        def backup(self):
                tmpl = env.get_template("backup.html")
                js = ['/js/odr-backup.js']
                return tmpl.render(tab='backup', js=js, is_login=is_login(), is_network=is_network(self.config_file))

        @cherrypy.expose
        @require()
        def user(self):
                tmpl = env.get_template("user.html")
                js = ['/js/odr-user.js']
                return tmpl.render(tab='user', js=js, is_login=is_login(), is_network=is_network(self.config_file))

        @cherrypy.expose
        @require()
        def network(self):
                tmpl = env.get_template("network.html")
                js = ['/js/odr-network.js']
                return tmpl.render(tab='user', js=js, is_login=is_login(), is_network=is_network(self.config_file))

def signal_handler(signal, frame):
    print ( "Exiting..." )
    cherrypy.engine.exit()
    sys.exit(0)

if __name__ == '__main__':
        # Get configuration file in argument
        parser = argparse.ArgumentParser(description='ODR Encoder Manager (WebGUI)')
        parser.add_argument('-c','--config', help='configuration filename',required=True)
        cli_args = parser.parse_args()

        # Check if configuration exist and is readable
        if os.path.isfile(cli_args.config) and os.access(cli_args.config, os.R_OK):
                print ( "Use configuration file %s" % (cli_args.config) )
        else:
                print ( "Configuration file is missing or is not readable - %s" % (cli_args.config) )
                sys.exit(1)

        # Load configuration
        config = Config(cli_args.config)

        # Start cherrypy
        if config.config['global']['daemon']:
                cherrypy.process.plugins.Daemonizer(cherrypy.engine).subscribe()

        cherrypy.config.update({
                'server.socket_host': config.config['global']['host'],
                'server.socket_port': int(config.config['global']['port']),
                'request.show_tracebacks' : True,
                'environment': 'production',
                'log.access_file' : os.path.join(config.config['global']['logs_directory'], 'access.log'),
                'log.error_file' : os.path.join(config.config['global']['logs_directory'], 'error.log'),
                'log.screen': False,
                'tools.sessions.on': True,
                'tools.encode.on': True,
                'tools.encode.encoding': "utf-8"
                })

        cherrypy.tree.mount(
                Root(cli_args.config), config={
                        '/':
                                        { 
                                        },
                        '/css':
                                        { 
                                        'tools.staticdir.on': True,
                                        'tools.staticdir.dir': os.path.join(config.config['global']['static_directory'], u"css/")
                                        },
                        '/js':
                                        { 
                                        'tools.staticdir.on': True,
                                        'tools.staticdir.dir': os.path.join(config.config['global']['static_directory'], u"js/")
                                        },
                        '/fonts':
                                        { 
                                        'tools.staticdir.on': True,
                                        'tools.staticdir.dir': os.path.join(config.config['global']['static_directory'], u"fonts/")
                                        },
                        '/favicon.ico':
                                        { 
                                        'tools.staticfile.on': True,
                                        'tools.staticfile.filename': os.path.join(config.config['global']['static_directory'], u"fonts/favicon.ico")
                                        },
                }
        )

        signal.signal(signal.SIGINT, signal_handler)
        cherrypy.engine.start()
        #cherrypy.engine.block()

        while True:
            time.sleep(5)
