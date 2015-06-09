# Supervisor

You can use supervisor to run ODR Encoder Manager at startup and keep running.

To install supervisor : 

  * apt-get install supervisor

You need to copy api.conf and encoder.conf in /etc/supervisor/conf.d/ and change path if needed.

To apply changes to supervisor, run :

  * supervisorctl reread
  * supervisorctl update

To see process status :

  * supervisorcrl status

To start or stop a process :

  * supervisorcrl [start|stop] [api|encoder]

To enable Web interface to manage process add to your /etc/supervisor/supervisord.conf file :
[inet_http_server]
port=*:9001
;username="admin"
;password="admin"