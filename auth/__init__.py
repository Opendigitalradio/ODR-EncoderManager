#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2019 Yoann QUERET <yoann@queret.net>
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

import json
import cherrypy
try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+

import hashlib

from config import Config

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))

from html import escape


SESSION_KEY = '_cp_username'

def check_credentials(config_auth, username, password):
    """Verifies credentials for username and password.
    Returns None on success or a string describing the error on failure"""

    for up in config_auth['users']:
        if (up['username'] == username and up['password'] == password) or (up['username'] == username and up['password'] == hashlib.md5(password.encode('utf-8')).hexdigest()):
            return None
    return "Incorrect username or password."

def check_auth(*args, **kwargs):
    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as alist of
    conditions that the user must fulfill"""
    conditions = cherrypy.request.config.get('auth.require', None)
    # format GET params
    get_parmas = quote(cherrypy.request.request_line.split()[1])
    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    # Send old page as from_page parameter
                    raise cherrypy.HTTPRedirect("/auth/login?from_page=%s" % get_parmas)
        else:
            # Send old page as from_page parameter
            raise cherrypy.HTTPRedirect("/auth/login?from_page=%s" %get_parmas)

cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)

def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate

def is_login():
    sess = cherrypy.session
    username = sess.get(SESSION_KEY, None)
    if username:
        return True
    else:
        return False

# Conditions are callables that return True
# if the user fulfills the conditions they define, False otherwise
#
# They can access the current username as cherrypy.request.login
#
# Define those at will however suits the application.

#def member_of(groupname):
#    def check():
#        # replace with actual check if <username> is in <groupname>
#        return cherrypy.request.login == 'joe' and groupname == 'admin'
#    return check

#def name_is(reqd_username):
#    return lambda: reqd_username == cherrypy.request.login

# These might be handy

#def any_of(*conditions):
#    """Returns True if any of the conditions match"""
#    def check():
#        for c in conditions:
#            if c():
#                return True
#        return False
#    return check

# By default all conditions are required, but this might still be
# needed if you want to use it inside of an any_of(...) condition
#def all_of(*conditions):
#    """Returns True if all of the conditions match"""
#    def check():
#        for c in conditions:
#            if not c():
#                return False
#        return True
#    return check


# Controller to provide login and logout actions

class AuthController(object):
    def __init__(self, config_file):
        self.config_file = config_file

    def on_login(self, username):
        """Called on successful login"""

    def on_logout(self, username):
        """Called on logout"""

    @cherrypy.expose
    def login(self, username=None, password=None, from_page="/", **params):
        encode_username=escape(str(username), True)
        encode_from_page=escape(str(from_page[0]), True)
        if username is None or password is None:
            tmpl = env.get_template("login.html")
            if from_page.startswith('api', 1):
                cherrypy.response.headers['content-type'] = "application/json"
                return json.dumps( {'status': '-401', 'statusText': 'Unauthorized'} ).encode()
            else:
                return tmpl.render(username="", msg="Enter login information", from_page=encode_from_page)

        conf = Config(self.config_file)
        error_msg = check_credentials(conf.config['auth'], username, password)
        if error_msg:
            tmpl = env.get_template("login.html")
            if from_page.startswith('api', 1):
                cherrypy.response.headers['content-type'] = "application/json"
                return json.dumps( {'status': '-401', 'statusText': 'Unauthorized'} ).encode()
            else:
                return tmpl.render(username=encode_username, msg=error_msg, from_page=encode_from_page)
        else:
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            self.on_login(username)
            raise cherrypy.HTTPRedirect(from_page or "/")

    @cherrypy.expose
    def logout(self, from_page="/"):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
            self.on_logout(username)
        raise cherrypy.HTTPRedirect(from_page or "/")
