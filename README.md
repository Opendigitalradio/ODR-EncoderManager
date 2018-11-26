# ODR-EncoderManager
OpenDigitalRadio Encoder Manager is a tools to run and configure ODR Encoder easly with a WebGUI.

# INSTALLATION

  * (root) Install requirement : `apt install python-cherrypy3 python-jinja2 python-serial supervisor`
  * (root) Add odr user to dialout group : `usermod -a -G dialout odr`
  * (root) Add odr user to audio group : `usermod -a -G audio odr`
  * (user) Got to odr user home : `cd /home/odr/`
  * (user) Clone git repository : `git clone https://github.com/YoannQueret/ODR-EncoderManager.git`
  * (user) Rename sample config : `mv /home/odr/ODR-EncoderManager/config.json.sample /home/odr/ODR-EncoderManager/config.json`
  * (root) Make the symlink: `ln -s /home/odr/ODR-EncoderManager/supervisor-encoder.conf /etc/supervisor/conf.d/odr-encoder.conf`
  * (root) Make the symlink: `ln -s /home/odr/ODR-EncoderManager/supervisor-gui.conf /etc/supervisor/conf.d/odr-gui.conf`
  * (root) Edit `/etc/supervisor/supervisord.conf` and add this section :
```
[inet_http_server]
port = 9001
username = user ; Auth username
password = pass ; Auth password
```
  * (root) Restart supervisor : `/etc/init.d/supervisor restart`
  * (root) Start WEB server : `supervisorctl reread; supervisorctl update ODR-encoderManager`
  * Go to : `http://<ip_address>:8080`



# CONFIGURATION
  * You can edit global configuration, in particular path in this files :
    * config.json
    * supervisor-gui.conf
  * If you want to change supervisor XMLRPC login/password, you need to edit `/etc/supervisor/supervisord.conf` and `config.json` files

# Note about Python2
  * If you want to use python2, you need to run `pip install future` before to have xmlrpc.client support

# ADVANCED
  * To use the reboot api (/api/reboot), you need to allow odr user to run shutdown command by adding the line bellow at the end of /etc/sudoers file :
```
odr     ALL=(ALL) NOPASSWD: /sbin/shutdown
```

