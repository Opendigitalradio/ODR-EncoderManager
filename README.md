# ODR-EncoderManager
OpenDigitalRadio Encoder Manager is a tools to run and configure ODR Encoder easly with a WebGUI.

ODR-EncoderManager is currently in complet re-developpement in this branch and is not yet ready to use in production.

![Screenshot] (https://raw.github.com/YoannQueret/ODR-EncoderManager/master/ODR-Encoder_Manager.png)

# INSTALLATION

  * Install requirement : apt install python-cherrypy3 python-jinja2 supervisor
  * Got to odr user home : cd /home/odr/
  * Clone git repository : git clone https://github.com/YoannQueret/ODR-EncoderManager.git
  * Make the symlink: ln -s /home/odr/ODR-EncoderManager/supervisor.conf /etc/supervisor/conf.d/encoderManager.conf
  * Make the symlink: ln -s /home/odr/ODR-EncoderManager/supervisor-gui.conf /etc/supervisor/conf.d/encoderManager-gui.conf
  * Edit /etc/supervisor/supervisord.conf and add this section :

[inet_http_server]
port = 9001
username = user ; Auth username
password = pass ; Auth password

  * Restart supervisor : /etc/init.d/supervisor restart
  * Start WEB server : supervisorctl reread; supervisorctl update encoderManager-gui
  * Go to : http://<ip_address>:8080
  





