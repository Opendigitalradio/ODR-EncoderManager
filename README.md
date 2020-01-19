# ODR-EncoderManager
OpenDigitalRadio Encoder Manager is a tools to run and configure ODR Encoder easly with a WebGUI.

# Note about version V4.0.3
  * Add audio level bar graph
  * AVT AE1 and AVT AE4 support
  * AES67 experimental support
  * need odr-audioenc v2.4.0 or higher
  * need odr-sourcecompanion v0.4.0 or higher
  * need odr-padenc v2.3.0 or higher

# Note about version V4.0.1
  * resolve 500 Internal server error when adding user

# Note about version V4.0.0
From version V4.0.0, python2 that will be deprecated on January 1st 2020 is no longer supported. Use python3.

Version V4.0.0, introduces the support of several encoder, managed from the same interface. In the case of an upgrade from a lower version, the config.json configuration file and processes managed by supervisor will be automatically converted into the new format.

New features from version V4.0.0 :
  * Multi encoder support
  * aes67 input support (experimental)
  * restart encoder after blank detection
  * Raw DLS support
  * Uniform PAD support
  * Can choose to enable/disable writing ICY Text when using a stream as input
  * AVT Status windows (via SNMP)
  * Edit DLS
  * Status page refactoring
  * ...


# INSTALLATION

  * (root) Install requirement (debian/jessie) : `apt install python3-cherrypy3 python3-jinja2 python3-serial python3-yaml supervisor python3-pysnmp`
  * (root) Install requirement (debian/stretch) : `apt install python3-cherrypy3 python3-jinja2 python3-serial python3-yaml supervisor python3-pysnmp4`
  * (root) Add odr user : `adduser odr`
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
port = 8900
username = user ; Auth username
password = pass ; Auth password
```
  * (root) Restart supervisor : `/etc/init.d/supervisor restart`
  * (root) Start WEB server : `supervisorctl reread; supervisorctl update ODR-encoderManager`
  * Go to : `http://<ip_address>:8080`
  * Login with user `joe` and password `secret` 



# CONFIGURATION
  * You can edit global configuration, in particular path in this files :
    * config.json
    * supervisor-gui.conf
  * If you want to change supervisor XMLRPC login/password, you need to edit `/etc/supervisor/supervisord.conf` and `config.json` files


# How to set DLS / DL+
**Set DLS / DL+ for all encoder**
To set a text metadata used for DLS, use http GET or POST on the Encoder Manager API from your automation software.
> http://{ip}:8080/api/setDLS?dls={artist}-{title}

As an alternative DLS+ tags are automatically activated if you use artist & title parameters:
> http://{ip}:8080/api/setDLS?artist={artist}&title={title}

Many radio automation software can send this information to Encoder Manager API by using a call of this type (for example)
> http://{ip}:8080/api/setDLS?dls=%%artist%% - %%title%%

%%artist%% - %%title%% should be replaced with the expression expected from your radio automation software.

At each events on your playlist (when a track start) the radio automation software will send via this url the appropriate metadata to Encoder Manager API. It will be reflected on the DAB signal.

**Set DLS / DL+ for specific encoder (from version V4.0.0)**
If you want to update DLS / DL+ for a specific encoder, you need to find the uniq_id on Encoder > Manage page under Information button
> http://{ip}:8080/api/setDLS?dls={artist}-{title}&uniq_id={00000000-0000-0000-0000-000000000000}

# ADVANCED
  * To use the reboot api (/api/reboot), you need to allow odr user to run shutdown command by adding the line bellow at the end of /etc/sudoers file :
```
odr     ALL=(ALL) NOPASSWD: /sbin/shutdown
```

