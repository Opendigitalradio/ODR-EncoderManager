#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 Yoann QUERET <yoann@queret.net>
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

import ConfigParser
import os
import sys
import json

class Config():
	def __init__(self, config_file):
		self.config_file = config_file
		
		self.load(config_file)
			
	def load(self, config_file):
		with open(self.config_file) as data_file:    
			self.config = json.load(data_file)
		