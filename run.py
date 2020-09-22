#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2020 Yoann QUERET <yoann@queret.net>
"""

"""
This file is part of ODR-EncoderManager.

ODR-EncoderManager is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ODR-EncoderManager is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ODR-EncoderManager.  If not, see <http://www.gnu.org/licenses/>.
"""

import cherrypy
import argparse
import os
import sys

from config import Config, is_network, is_adcast, is_slide_mgnt
from auth import AuthController, require, is_login
from api import API

import signal
import time

import uuid

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
    @require()
    def help(self):
        tmpl = env.get_template("help.html")
        js = []
        return tmpl.render(tab='help', js=js, is_login=is_login(), is_network=is_network(self.config_file))

    @cherrypy.expose
    @require()
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
        css = ['/css/bars.css']
        return tmpl.render(tab='status', js=js, css=css, is_login=is_login(), is_network=is_network(self.config_file))

    @cherrypy.expose
    @require()
    def encoderconfig(self):
        tmpl = env.get_template("encoderconfig.html")
        js = ['/js/odr-encoderconfig.js']
        return tmpl.render(tab='encoderconfig', js=js, is_login=is_login(), is_network=is_network(self.config_file), is_slide_mgnt=is_slide_mgnt(self.config_file), is_adcast=is_adcast(self.config_file))

    @cherrypy.expose
    @require()
    def encodermanage(self):
        tmpl = env.get_template("encodermanage.html")
        js = ['/js/odr-encodermanage.js']
        return tmpl.render(tab='encodermanage', js=js, is_login=is_login(), is_network=is_network(self.config_file))

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
    print("Exiting...")
    cherrypy.engine.exit()
    sys.exit(0)

if __name__ == '__main__':
    # Get configuration file in argument
    parser = argparse.ArgumentParser(description='ODR Encoder Manager (WebGUI)')
    parser.add_argument('-c','--config', help='configuration filename', required=True)
    cli_args = parser.parse_args()

    # Check if configuration exist and is readable
    if os.path.isfile(cli_args.config) and os.access(cli_args.config, os.R_OK):
        print("Use configuration file %s" % cli_args.config)
    else:
        print("Configuration file is missing or is not readable - %s" % cli_args.config)
        sys.exit(1)

    # Load configuration
    config = Config(cli_args.config)

    # Check if configuration file need to be updated to support multi encoder
    if isinstance(config.config['odr'], dict):
        print ( 'Convert configuration file to support multi encoder ...' )

        odr = config.config['odr']
        odr['name'] = 'default coder'
        odr['uniq_id'] = str(uuid.uuid4())
        odr['description'] = 'This is the default coder converted from previous version'
        output = { 'global': config.config['global'], 'auth': config.config['auth'], 'odr': [ odr ] }

        # Write configuration file
        try:
            config.write(output, False)
        except Exception as e:
            print ( 'Error when writing configuration file: ' + str(e) )
            sys.exit(2)

    # Check if configuration file need to be updated with new key
    try:
        config.checkConfigurationFile()
    except Exception as e:
        print ( 'Error during configuration file check: ' + str(e) )
        sys.exit(2)

    # Check supervisor process and add or remove it if necessary
    try:
        config.checkSupervisorProcess()
    except Exception as e:
        print ( 'Error during supervisor process check: ' + str(e) )
        sys.exit(2)

    # init configuration changed
    config.initConfigurationChanged()

    # Start cherrypy
    if config.config['global']['daemon']:
        cherrypy.process.plugins.Daemonizer(cherrypy.engine).subscribe()

    cherrypy.config.update({
        'server.socket_host': config.config['global']['host'],
        'server.socket_port': int(config.config['global']['port']),
        'request.show_tracebacks' : False,
        'environment': 'production',
        'log.access_file' : os.path.join(config.config['global']['logs_directory'], 'access.log'),
        'log.error_file' : os.path.join(config.config['global']['logs_directory'], 'error.log'),
        'log.screen': False,
        'tools.sessions.on': True,
        'tools.sessions.name': "ODR-Encoder-Manager",
        'tools.sessions.secure': True,
        'tools.sessions.same_site': 'Lax',
        'tools.encode.on': True,
        'tools.encode.encoding': "utf-8"
        })

    cherrypy.tree.mount(
        Root(cli_args.config), config={
            '/': {
                },
            '/css': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(config.config['global']['static_directory'], u"css/"),
                'tools.gzip.on'       : True,
                'tools.expires.on'    : True,
                'tools.expires.secs'  : 0
                },
            '/js': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(config.config['global']['static_directory'], u"js/"),
                'tools.gzip.on'       : True,
                'tools.expires.on'    : True,
                'tools.expires.secs'  : 0
                },
            '/fonts': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(config.config['global']['static_directory'], u"fonts/"),
                'tools.gzip.on'       : True,
                'tools.expires.on'    : True,
                'tools.expires.secs'  : 0
                },
            '/favicon.ico': {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': os.path.join(config.config['global']['static_directory'], u"fonts/favicon.ico")
                },
        }
    )

    signal.signal(signal.SIGINT, signal_handler)
    cherrypy.engine.start()
    #cherrypy.engine.block()
    
    config.initAudioSocket()
    while True:
        config.addAudioSocket()
        config.retreiveAudioSocket()
        time.sleep(0.10)
