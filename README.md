# ODR-EncoderManager
OpenDigitalRadio Encoder Manager is a tools to run and configure ODR Encoder easly with a WebGUI.

ODR-EncoderManager is currently in complet re-developpement in this branch and is not yet ready to use in production.

![Screenshot] (https://raw.github.com/YoannQueret/ODR-EncoderManager/master/ODR-Encoder_Manager.png)

# INSTALLATION

  * Install requirement : apt install python-cherrypy3 python-jinja2 supervisor
  * Got to odr user home : cd /home/odr/
  * Clone git repository : git clone https://github.com/YoannQueret/ODR-EncoderManager.git
  * Make the symlink: ln -s /home/odr/ODR-EncoderManager/supervisor-encoder.conf /etc/supervisor/conf.d/odr-encoder.conf
  * Make the symlink: ln -s /home/odr/ODR-EncoderManager/supervisor-gui.conf /etc/supervisor/conf.d/odr-gui.conf
  * Edit /etc/supervisor/supervisord.conf and add this section :

[inet_http_server]
port = 9001
username = user ; Auth username
password = pass ; Auth password

  * Restart supervisor : /etc/init.d/supervisor restart
  * Start WEB server : supervisorctl reread; supervisorctl update ODR-encoderManager
  * Go to : http://<ip_address>:8080
  


# CONFIGURATION
  * You can edit global configuration, in particular path in this files :
    * config.json
    * supervisor-gui.conf
  * If you want to change supervisor XMLRPC login/password, you need to edit /etc/supervisor/supervisord.conf and config.json files
    


