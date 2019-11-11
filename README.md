# ODR-EncoderManager
OpenDigitalRadio Encoder Manager is a tools to run and configure ODR Encoder easly with a WebGUI.

# Note about version V4.0.1
  * resolve 500 Internal server error when adding user

# Note about version V4.0.0
From version V4.0.0, python2 that will be deprecated on January 1st 2020 is no
longer supported. Use python3.

Version V4.0.0, introduces the support of several encoder, managed from the same
interface. In the case of an upgrade from a lower version, the config.json
configuration file and processes managed by supervisor will be automatically
converted into the new format.

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

  * Install requirement:

      ```bash
      $ sudo apt install python3-cherrypy3 python3-jinja2 python3-serial python3-pysnmp4 supervisor
      ```
    Older Debian version may need `python3-pysnmp` instead of `python3-pysnmp4`.

  * create odr user:

      ```bash
      $ sudo useradd odr
      $ sudo usermod -a -G dialout,audio odr
      ```
  * Clone repo to `/opt/ODR-EncoderManager`:

      ```bash
      $ sudo git clone https://github.com/YoannQueret/ODR-EncoderManager /opt/ODR-EncoderManager
      ```

  * Configure ODR EncoderManager:

      ```bash
      $ sudo mv /opt/ODR-EncoderManager/config.json.sample /opt/ODR-EncoderManager/config.json
      $ sudo ln -s /opt/ODR-EncoderManager/supervisor-encoder.conf /etc/supervisor/conf.d/odr-encoder.conf
      $ sudo ln -s /opt/ODR-EncoderManager/supervisor-gui.conf /etc/supervisor/conf.d/odr-gui.conf
      $ sudo chown -R odr:odr /opt/ODR-EncoderManager
      ```

  * Edit `/etc/supervisor/supervisord.conf` and add this section:

      ```conf
      [inet_http_server]
      port = 9001
      username = admin ; Auth username
      password = admin ; Auth password
      ```

    Synchronise those credentials with `/opt/ODR-EncoderManager/config.json`.

  * Finally restart supervisor:

      ```bash
      $ sudo systemctl restart supervisor
      ```

  * And start WEB server:

      ```bash
      $ sudo supervisorctl reread
      $ sudo supervisorctl update ODR-encoderManager
      ```

  * Go to : `http://<ip_address>:8080`


# CONFIGURATION
  * You can edit global configuration, in particular path in this files :
    * config.json
    * supervisor-gui.conf
  * If you want to change supervisor XMLRPC login/password, you need to edit `/etc/supervisor/supervisord.conf` and `config.json` files


# How to set DLS / DL+
**Set DLS / DL+ for all encoder**
To set a text metadata used for DLS, use http GET or POST on the Encoder Manager
API from your automation software.
> http://{ip}:8080/api/setDLS?dls={artist}-{title}

As an alternative DLS+ tags are automatically activated if you use artist &
title parameters:
> http://{ip}:8080/api/setDLS?artist={artist}&title={title}

Many radio automation software can send this information to Encoder Manager API
by using a call of this type (for example)
> http://{ip}:8080/api/setDLS?dls=%%artist%% - %%title%%

%%artist%% - %%title%% should be replaced with the expression expected from your
radio automation software.

At each events on your playlist (when a track start) the radio automation
software will send via this url the appropriate metadata to Encoder Manager API.
It will be reflected on the DAB signal.

**Set DLS / DL+ for specific encoder (from version V4.0.0)**
If you want to update DLS / DL+ for a specific encoder, you need to find the
uniq_id on Encoder > Manage page under Information button
> http://{ip}:8080/api/setDLS?dls={artist}-{title}&uniq_id={00000000-0000-0000-0000-000000000000}

# ADVANCED
  * To use the reboot api (/api/reboot), you need to allow odr user to run
  shutdown command by adding the line bellow at the end of /etc/sudoers file :
```
odr     ALL=(ALL) NOPASSWD: /sbin/shutdown
```

