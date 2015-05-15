#!/bin/bash

#!/bin/bash
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