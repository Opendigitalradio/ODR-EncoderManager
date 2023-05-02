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

import os
import importlib
import cherrypy

from auth import AuthController, require, is_login
from config import Config

def listdirs(path):
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

def __getitem__(self, key):
    return getattr(self, key)


class Plugins():

    def __init__(self, config_file, hostname):
        self.config_file = config_file
        self.hostname = hostname
        self.conf = Config(self.config_file)
        self.plugins_dir = '%s/plugins/' % ( os.getcwd() )
        
        for plugin in listdirs(self.plugins_dir):
            if not plugin.startswith('__'):
                module_name = 'plugins.%s' % (plugin)
                try:
                    module_obj = importlib.import_module(module_name)
                    
                except BaseException as err:
                    serr = str(err)
                    print("Error loading plugins '" + plugin + "': " + serr)
                else:
                    print('Loading plugin "%s"' % (plugin), flush=True)
                    self.conf.addPlugins(plugin)
                    setattr( self, plugin, __getitem__(module_obj, plugin)(self.config_file, self.hostname) )
        
        # remove old plugin section in configuration file if removed
        self.conf = Config(self.config_file)
        output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': self.conf.config['odr'], 'plugins': self.conf.config['plugins'] }
        
        
        plugins_to_remove = []
        for plugin in output['plugins']:
            if plugin not in self.conf.getPlugins():
                plugins_to_remove.append(plugin)
        
        for plugin in plugins_to_remove:
            print('Remove plugin "%s" in configuration file' % (plugin), flush=True)
            del(output['plugins'][plugin])
        
        # Write configuration file
        try:
            self.conf.write(output)
        except Exception as e:
            return {'status': '-201', 'statusText': 'Error when writing configuration file: {}'.format(e)}
        
    
    def is_available(self):
        if len( self.conf.getPlugins() ) != 0:
            return True
        else:
            return False
        
    def list_plugins(self):
        return self.conf.getPlugins()
    
    @cherrypy.expose
    @require()
    def index(self):
        cherrypy.response.headers['content-type'] = "text/plain"
        return "This is the plugins area with {0} available.".format( len( loaded_plugins ) )
    
