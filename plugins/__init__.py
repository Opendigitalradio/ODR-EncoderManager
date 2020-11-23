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

def listdirs(path):
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

def __getitem__(self, key):
    return getattr(self, key)


class Plugins():

    def __init__(self, config_file):
        self.config_file = config_file
        self.plugins_dir = '%s/plugins/' % ( os.getcwd() )
        self.plugins = []
        
        for plugin in listdirs(self.plugins_dir):           
            module_name = 'plugins.%s' % (plugin)
            try:
                module_obj = importlib.import_module(module_name)
                
            except BaseException as err:
                serr = str(err)
                print("Error loading plugins '" + plugin + "': " + serr)
            else:
                print ('Loading plugins %s' % (plugin), flush=True)
                self.plugins.append(plugin)
                setattr( self, plugin, __getitem__(module_obj, plugin)(self.config_file) )
    
    def is_available(self):
        if len( self.plugins ) != 0:
            return True
        else:
            return False
        
    def list_plugins(self):
        return self.plugins
    
    @cherrypy.expose
    @require()
    def index(self):
        cherrypy.response.headers['content-type'] = "text/plain"
        return "This is the plugins area with {0} available.".format( len( self.plugins ) )
    
