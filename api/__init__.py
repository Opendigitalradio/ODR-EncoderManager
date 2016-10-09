# -*- encoding: UTF-8 -*-
#
# Form based authentication for CherryPy. Requires the
# Session tool to be loaded.
#

import cherrypy
import urllib

class API:
	
	# all methods in this controller (and subcontrollers) is
	# open only to members of the admin group
	
	@cherrypy.expose
	def index(self):
		return """This is the api area."""