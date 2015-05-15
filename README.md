# ODR-EncoderManager
OpenDigitalRadio Encoder Manager is a tools to run and configure ODR Encoder easly with a WebGUI.

ODR-EncoderManager is currently in developpement and is not ready to use in production

Run install-python-dependency.sh to install python dependency.

  * ./encoder.py -c config.ini
  * ./api.py -s static/ -l logs/


# TODO LIST

This list is without ordered !

  * Add an API method to update Dynamic Label Segment (DLS) with current song or other.
    * A RPC method on encoder daemon
    * A JSON method on api daemon
  * Add current DLS on status page
  * Add BIG warning when RPC parameters are updated with WebGUI
  * Update ZMQ Key instead of ZMQ Key path (who need to have ssh access)
  * Debian startup script, to launch encoder at startup
  * Create help content on help page



