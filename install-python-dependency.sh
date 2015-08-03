#!/bin/bash

# 
# Copyright (C) 2015 Yoann QUERET <yoann@queret.net>
# 

# 
# This file is part of ODR-EncoderManager.
# 
# ODR-EncoderManager is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ODR-EncoderManager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with ODR-EncoderManager.  If not, see <http://www.gnu.org/licenses/>.
# 

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# install pip
wget https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
python /tmp/get-pip.py

# for both encoder and api daemon
pip install argparse

# for encoder daemon
pip install twisted
pip install txJSON-RPC

# for api daemon
pip install requests
pip install cherrypy