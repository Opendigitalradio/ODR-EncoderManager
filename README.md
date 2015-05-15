# ODR-EncoderManager
OpenDigitalRadio Encoder Manager is a tools to run and configure ODR Encoder easly with a WebGUI.

ODR-EncoderManager is currently in developpement and is not ready to use in production

Run install-python-dependency.sh to install all python dependency.

  * ./encoder.py -c config.ini
  * ./api.py -s static/ -l logs/

# Warning
This program has been tested only on GNU/Linux Debian Jessie (8.x)

No access protection has been implemented yet instead IP binding configuration. So, unless the network is protected otherwise, anyone can access and modify your encoder settings.


# TODO LIST
This list is without ordered !

  * Add BIG warning when RPC parameters are updated with WebGUI
  * Update ZMQ Key instead of ZMQ Key path (who need to have ssh access)
  * Debian startup script, to launch encoder at startup
  * Create help content on help page



