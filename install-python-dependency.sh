#!/bin/bash

#!/bin/bash
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

wget https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
python /tmp/get-pip.py
pip install twisted
pip install txJSON-RPC