# ODR-EncoderManager
OpenDigitalRadio Encoder Manager

You need to have ODR fdk-aac-dabplus version v0.7.0 or more with libvlc

This program need to have python twisted module.


First method - Install python module globaly :
  * wget https://bootstrap.pypa.io/get-pip.py
  * python get-pip.py
  * pip install twisted
  * ./encoder.py -c config.ini


Second method - Install python module in virtualenv :
  * wget https://bootstrap.pypa.io/get-pip.py
  * python get-pip.py
  * pip install virtualenv
  * pip install virtualenvwrapper

  * source /usr/local/bin/virtualenvwrapper.sh
  * mkvirtualenv encoder
  * pip install twisted
  

  * To run encoder Manager :
    * source /usr/local/bin/virtualenvwrapper.sh
    * workon encoder
    * ./encoder.py -c config.ini

  * To quit virtualenv :
    * deactivate
