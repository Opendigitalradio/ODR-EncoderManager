# -*- encoding: UTF-8 -*-
#
# Form based authentication for CherryPy. Requires the
# Session tool to be loaded.
#

import json
import cherrypy
from cherrypy.lib.httputil import parse_query_string


import urllib
import os

import sys
if sys.version_info >= (3, 0):
    from xmlrpc import client as xmlrpc_client
else:
    import xmlrpclib as xmlrpc_client

from config import Config
from auth import AuthController, require, is_login

import subprocess
import io
import zipfile
import datetime
import shutil

import hashlib
import codecs

class API():

    def __init__(self, config_file):
        self.config_file = config_file
        self.conf = Config(self.config_file)
        self.auth = AuthController(self.conf.config['auth'])


    # all methods in this controller (and subcontrollers) is
    # open only to members of the admin group

    @cherrypy.expose
    def index(self):
        cherrypy.response.headers['content-type'] = "text/plain"
        return """This is the api area."""

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def reboot(self):
        command = 'sudo /sbin/shutdown -r now'
        p_status = subprocess.call(command, shell=True)

        if int(p_status) != 0:
            return {'status': '-299', 'statusText': 'Can not process reboot - %s ' % (int(p_status))}
        else:
            return {'status': '0', 'statusText': 'Ok'}

    @cherrypy.expose
    @require()
    def backup(self):
        self.conf = Config(self.config_file)
        result = io.BytesIO()
        zipped = zipfile.ZipFile(result, mode = 'w', compression = zipfile.ZIP_DEFLATED)
        zipped.writestr('config.json', json.dumps(self.conf.config, indent=4, separators=(',', ': ')))
        zipped.close()
        result.seek(0)
        datefile = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        cherrypy.response.headers['content-type']        = 'application/octet-stream'
        cherrypy.response.headers['content-disposition'] = 'attachment; filename=backup-%s.zip' % (datefile)
        return result

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def restore(self, myFile):
        self.conf = Config(self.config_file)
        size = 0
        data = myFile.file.read()
        size += len(data)

        localfile = '/tmp/'+myFile.filename
        file = open (localfile, 'wb')
        file.write(data)
        file.close()

        if zipfile.is_zipfile(localfile):
            # Open local ZIP file and extract config.json file
            fh = open( localfile , 'rb')
            zipped = zipfile.ZipFile(fh)
            for name in zipped.namelist():
                if name == 'config.json':
                    zipped.extract(name, '/tmp/')
            fh.close()

            # Remove ZIP file
            try:
                os.remove(localfile)
            except Exception as e:
                pass

            # Read tmp config.json file
            with open('/tmp/config.json') as data_file:
                output = json.load(data_file)

            # Remove config.json file
            try:
                os.remove('/tmp/config.json')
            except Exception as e:
                pass

            # Write configuration file
            try:
                self.conf.write(output)
            except Exception as e:
                return {'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)}

            # Generate supervisor files
            try:
                self.conf.generateSupervisorFiles(output)
            except Exception as e:
                return {'status': '-202', 'statusText': 'Error generating supervisor files' + str(e)}

            # Generate network files
            try:
                self.conf.generateNetworkFiles(output)
            except Exception as e:
                return {'status': '-202', 'statusText': 'Error when writing network file' + str(e)}


            # Check if ODR program availaible in supervisor ProcessInfo and try to add it

            # Retreive supervisor process
            server = xmlrpc_client.ServerProxy(self.conf.config['global']['supervisor_xmlrpc'])
            programs = server.supervisor.getAllProcessInfo()

            # Check for ODR-audioencoder
            if not self.is_program_exist(programs, 'ODR-audioencoder'):
                try:
                    server.supervisor.reloadConfig()
                    server.supervisor.addProcessGroup('ODR-audioencoder')
                except:
                    return {'status': '-206', 'statusText': 'Error when starting ODR-audioencoder (XMLRPC): ' + str(e)}

            # Check for ODR-padencoder
            if not self.is_program_exist(programs, 'ODR-padencoder'):
                try:
                    server.supervisor.reloadConfig()
                    server.supervisor.addProcessGroup('ODR-padencoder')
                except:
                    return {'status': '-207', 'statusText': 'Error when starting ODR-padencoder (XMLRPC): ' + str(e)}

            return {'status': '0', 'statusText': 'Ok'}
        else:
            return {'status': '-200', 'statusText': 'Uploaded file is not a zip file'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def getNetworkDNS(self, **params):
        self.conf = Config(self.config_file)
        query = parse_query_string(cherrypy.request.query_string)
        data = self.conf.config['global']['network']['dns']
        return {'status': '0', 'statusText': 'Ok', 'data': data}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def setNetworkDNS(self):
        self.conf = Config(self.config_file)

        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        param = json.loads(rawbody.decode('utf-8'))

        output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': self.conf.config['odr'] }

        output['global']['network']['dns'] = param

        # Write configuration file
        try:
            self.conf.write(output)
        except Exception as e:
            return {'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)}


        # Generate network files
        try:
            self.conf.generateNetworkFiles(output)
        except Exception as e:
            return {'status': '-201', 'statusText': 'Error when writing network file: ' + str(e)}
        return {'status': '0', 'statusText': 'Ok'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def getNetworkNTP(self, **params):
        self.conf = Config(self.config_file)
        query = parse_query_string(cherrypy.request.query_string)
        data = self.conf.config['global']['network']['ntp']
        return {'status': '0', 'statusText': 'Ok', 'data': data}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def setNetworkNTP(self):
        self.conf = Config(self.config_file)

        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        param = json.loads(rawbody.decode('utf-8'))

        output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': self.conf.config['odr'] }

        output['global']['network']['ntp'] = param

        # Write configuration file
        try:
            self.conf.write(output)
        except Exception as e:
            return {'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)}


        # Generate network files
        try:
            self.conf.generateNetworkFiles(output)
        except Exception as e:
            return {'status': '-201', 'statusText': 'Error when writing network file: ' + str(e)}
        return {'status': '0', 'statusText': 'Ok'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def restartNTP(self):
        command = 'sudo /bin/systemctl restart ntp'
        p_status = subprocess.call(command, shell=True)

        if int(p_status) != 0:
            return {'status': '-299', 'statusText': 'Can not process restart - %s ' % (int(p_status))}
        else:
            return {'status': '0', 'statusText': 'Ok'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def getNetworkCards(self, **params):
        self.conf = Config(self.config_file)
        query = parse_query_string(cherrypy.request.query_string)

        if 'card' in query:
            data={}
            for card in self.conf.config['global']['network']['cards']:
                if card['card'] == query['card']:
                    data=card
        else:
            data = self.conf.config['global']['network']['cards']

        return {'status': '0', 'statusText': 'Ok', 'data': data}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def setNetworkCard(self):
        self.conf = Config(self.config_file)

        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        param = json.loads(rawbody.decode('utf-8'))

        output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': self.conf.config['odr'] }

        change = False
        for i,value in enumerate(output['global']['network']['cards']):
            if value['card'] == param['card']:
                output['global']['network']['cards'][i]['dhcp'] = param['dhcp']
                output['global']['network']['cards'][i]['ip'] = param['ip']
                output['global']['network']['cards'][i]['netmask'] = param['netmask']
                output['global']['network']['cards'][i]['gateway'] = param['gateway']
                change = True
        if not change:
            return {'status': '-201', 'statusText': 'Card not found: ' + str(e)}

        # Write configuration file
        try:
            self.conf.write(output)
        except Exception as e:
            return {'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)}


        # Generate network files
        try:
            self.conf.generateNetworkFiles(output)
        except Exception as e:
            return {'status': '-202', 'statusText': 'Error generating network files' + str(e)}
        return {'status': '0', 'statusText': 'Ok'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def getConfig(self):
        self.conf = Config(self.config_file)
        return {'status': '0', 'statusText': 'Ok', 'data': self.conf.config['odr']}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def getAlsaDevices(self):
        command = '/usr/bin/arecord -l'
        try:
            output = subprocess.check_output(command,
                                shell=True,
                                stderr=subprocess.STDOUT)
        except:
            return {'status': '-200', 'statusText': 'Error listing alsa devices', 'data': ''}
        return {'status': '0', 'statusText': 'Ok', 'data': str(output.decode('UTF-8'))}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def setConfig(self):
        self.conf = Config(self.config_file)

        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        odr = json.loads(rawbody.decode('utf-8'))

        output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': odr }

        # Write configuration file
        try:
            self.conf.write(output)
        except Exception as e:
            return {'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)}

        # Generate supervisor files
        try:
            self.conf.generateSupervisorFiles(output)
        except Exception as e:
            return {'status': '-202', 'statusText': 'Error generating supervisor files' + str(e)}


        # Check if ODR program availaible in supervisor ProcessInfo and try to add it

        # Retreive supervisor process
        try:
            server = xmlrpc_client.ServerProxy(self.conf.config['global']['supervisor_xmlrpc'])
        except Exception as e:
                return {'status': '-211', 'statusText': 'Error when connect to supervisor XMLRPC: ' + str(e)}

        try:
            programs = server.supervisor.getAllProcessInfo()
        except Exception as e:
                return {'status': '-212', 'statusText': 'Error when retreive supervisor process: ' + str(e)}

        # Check for ODR-audioencoder
        if not self.is_program_exist(programs, 'ODR-audioencoder'):
            try:
                server.supervisor.reloadConfig()
                server.supervisor.addProcessGroup('ODR-audioencoder')
            except:
                return {'status': '-206', 'statusText': 'Error when starting ODR-audioencoder (XMLRPC): ' + str(e)}

        # Check for ODR-padencoder
        if not self.is_program_exist(programs, 'ODR-padencoder'):
            try:
                server.supervisor.reloadConfig()
                server.supervisor.addProcessGroup('ODR-padencoder')
            except:
                return {'status': '-207', 'statusText': 'Error when starting ODR-padencoder (XMLRPC): ' + str(e)}

        return {'status': '0', 'statusText': 'Ok'}


    @cherrypy.expose
    def setDLS(self, dls=None, artist=None, title=None, output=None, **params):
        self.conf = Config(self.config_file)

        if cherrypy.request.method == 'POST':
            query = {}
            if dls:
                query['dls'] = dls
            elif artist and title:
                query['artist'] = artist
                query['title'] = title
            if output:
                query['output'] = output

        elif cherrypy.request.method == 'GET':
            query = parse_query_string(cherrypy.request.query_string)

        else:
            cherrypy.response.status = 400
            # it's impossible to use build_response here, because
            # with an invalid request, the `output` parameter is
            # also considered invalid.
            cherrypy.response.headers['content-type'] = "text/plain"
            return "Only HTTP POST or GET are available"

        def build_response(r):
            """Helper function to choose between plain text and JSON
            response. `r` shall be a dictionary.
            """
            if 'output' in query and query['output'] == 'json':
                cherrypy.response.headers['content-type'] = "application/json"
                return json.dumps(r).encode()
            else:
                cherrypy.response.headers['content-type'] = "text/plain"
                return r['statusText']

        # DLS (odr-padenc process) is enable
        if self.conf.config['odr']['padenc']['enable'] == 'true':
            # dls parameters is present and override all other
            if 'dls' in query:
                if self.getDLS()['dls'] == query['dls'] and 'dlplus' not in self.getDLS():
                    r = {'status': '0', 'statusText': 'Ok-oldegal', 'dls': query['dls']}
                    return build_response(r)

                try:
                    with codecs.open(self.conf.config['odr']['padenc']['dls_fifo_file'], 'w', 'utf-8') as outfile:
                        outfile.write(query['dls'])
                except Exception as e:
                    r = {'status': '-210', 'statusText': 'Fail to write dls data'}
                    cherrypy.response.status = 500
                    return build_response(r)
                else:
                    r = {'status': '0', 'statusText': 'Ok', 'dls': query['dls']}
                    return build_response(r)

            # dls is not present and artist and title are available
            elif ('artist' in query) and ('title' in query):
                if 'dlplus' in self.getDLS() and self.getDLS()['dlplus']['artist'] == query['artist'] and self.getDLS()['dlplus']['title'] == query['title']:
                    r = {'status': '0', 'statusText': 'Ok-oldegal', 'dls': { 'artist': query['artist'], 'title': query['title']}}
                    return build_response(r)

                if (query['artist'] != '') and (query['title'] != ''):
                    data  = '##### parameters { #####\n'
                    data += 'DL_PLUS=1\n'
                    data += '# this tags \"%s\" as ITEM.ARTIST\n' % (query['artist'])
                    data += 'DL_PLUS_TAG=4 0 %s\n' % ( len(query['artist']) - 1 )
                    data += '# this tags \"%s\" as ITEM.TITLE\n' % (query['title'])
                    data += 'DL_PLUS_TAG=1 %s %s\n' % ( len(query['artist']) + 3 , len(query['title']) - 1 )
                    data += '##### parameters } #####\n'
                    data += '%s - %s\n' % (query['artist'], query['title'])
                    try:
                        with codecs.open(self.conf.config['odr']['padenc']['dls_fifo_file'], 'w', 'utf-8') as outfile:
                            outfile.write(data)
                    except Exception as e:
                        r = {'status': '-210', 'statusText': 'Fail to write dls data'}
                        cherrypy.response.status = 500
                        return build_response(r)
                    else:
                        r = {'status': '0', 'statusText': 'Ok', 'dls': { 'artist': query['artist'], 'title': query['title']} }
                        return build_response(r)
                else:
                    r = {'status': '-215', 'statusText': 'Error, artist or title are blank'}
                    cherrypy.response.status = 422
                    return build_response(r)

            # no needed parameters available
            else:
                r = {'status': '-209', 'statusText': 'Error, you need to use dls or artist + title parameters'}
                cherrypy.response.status = 400
                return build_response(r)

        # DLS (odr-padenc process) is disable
        else:
            r = {'status': '-208', 'statusTest': 'DLS is disable'}
            cherrypy.response.status = 422
            return build_response(r)



    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def getDLS(self, **params):
        query = parse_query_string(cherrypy.request.query_string)
        self.conf = Config(self.config_file)
        #cherrypy.response.headers["Content-Type"] = "application/json"

        output = []

        if self.conf.config['odr']['padenc']['enable'] == 'true':
            dls=None
            dlplus=None
            dlplus_data=[]
            try:
                with open(self.conf.config['odr']['padenc']['dls_fifo_file'], 'r') as f:
                    for line in f:
                        if line.startswith('#'):
                            continue
                        if line.startswith('DL_PLUS='):
                            dlplus=True
                            #continue
                        if line.startswith('DL_PLUS_TAG='):
                            v = line.split("=", 1)
                            d = v[1].split(" ")
                            dlplusCode = {
                                1: 'title',
                                2: 'album',
                                3: 'tracknumber',
                                4: 'artist',
                                5: 'composition',
                                6: 'movement',
                                7: 'conductor',
                                8: 'composer',
                                9: 'band',
                                10: 'comment',
                                11: 'genre'
                                }
                            dlplus_data.append( {'name': dlplusCode[int(d[0])], 'code': int(d[0]), 'start': int(d[1]), 'len': int(d[2])} )
                        dls = line.rstrip()
            except Exception as e:
                return {'dls': 'Fail to read DLS data'}
            else:
                if dlplus:
                    dlplus= {}
                    for d in dlplus_data:
                        dlplus[d['name']] = dls[d['start']:d['start']+d['len']+1]
                    return {'dls': str(dls), 'dlplus': dlplus}
                else:
                    return {'dls': str(dls)}
        else:
            return {'dls': 'DLS is disabled'}

    def is_program_exist(self, json, program):
        return any(p['name'] == program for p in json)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def getUser(self):
        self.conf = Config(self.config_file)
        users = self.conf.config['auth']['users']
        data = []
        for u in users:
            data.append( {'username': u['username']} )
        return {'status': '0', 'statusText': 'Ok', 'data': data}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def addUser(self):
        self.conf = Config(self.config_file)

        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        param = json.loads(rawbody.decode('utf-8'))

        output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': self.conf.config['odr'] }

        user_exists = any(u['username'] == param['username'] for u in output['auth']['users'])
        if not user_exists:
            output['auth']['users'].append({'username': param['username'], 'password': hashlib.md5(param['password']).hexdigest()});
        else:
            return {'status': '-201', 'statusText': 'User already exists'}

        # Write configuration file
        try:
            self.conf.write(output)
        except Exception as e:
            return {'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)}

        return {'status': '0', 'statusText': 'Ok'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def setPasswd(self):
        self.conf = Config(self.config_file)

        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        param = json.loads(rawbody.decode('utf-8'))

        output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': self.conf.config['odr'] }

        change = False
        for i,value in enumerate(output['auth']['users']):
            if value['username'] == param['username']:
                output['auth']['users'][i]['password'] = hashlib.md5(param['password'].encode('utf-8')).hexdigest()
                change = True
        if not change:
            return {'status': '-201', 'statusText': 'User not found: {}'.format(param['username'])}

        # Write configuration file
        try:
            self.conf.write(output)
        except Exception as e:
            return {'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)}

        return {'status': '0', 'statusText': 'Ok'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def delUser(self):
        self.conf = Config(self.config_file)

        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        param = json.loads(rawbody.decode('utf-8'))

        output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': self.conf.config['odr'] }

        change = False
        for i,value in enumerate(output['auth']['users']):
            if value['username'] == param['username']:
                output['auth']['users'].pop(i)
                change = True
        if not change:
            return {'status': '-201', 'statusText': 'User not found: {}'.format(param['username'])}

        # Write configuration file
        try:
            self.conf.write(output)
        except Exception as e:
            return {'status': '-201', 'statusText': 'Error when writing configuration file: {}'.format(e)}

        return {'status': '0', 'statusText': 'Ok'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def getStatus(self):
        self.conf = Config(self.config_file)
        server = xmlrpc_client.ServerProxy(self.conf.config['global']['supervisor_xmlrpc'])
        output = []

        try:
            output.append( server.supervisor.getProcessInfo('ODR-audioencoder') )
            output.append( server.supervisor.getProcessInfo('ODR-padencoder') )
        except Exception as e:
            return {'status': '-301', 'statusText': 'Error when getting ODR-audioencoder and ODR-padencoder status (XMLRPC): {}'.format(e)}

        if 'supervisor_additional_processes' in self.conf.config['global']:
            try:
                for proc in self.conf.config['global']['supervisor_additional_processes']:
                    output.append( server.supervisor.getProcessInfo(proc) )
            except Exception as e:
                return {'status': '-301', 'statusText': 'Error when getting additional supervisor process status (XMLRPC): {}'.format(e)}

        return {'status': '0', 'statusText': 'Ok', 'data': output}


    def serviceAction(self, action, service):
        self.conf = Config(self.config_file)

        server = xmlrpc_client.ServerProxy(self.conf.config['global']['supervisor_xmlrpc'])
        try:
            if action == 'start':
                server.supervisor.reloadConfig()
                server.supervisor.removeProcessGroup(service)
                server.supervisor.reloadConfig()
                server.supervisor.addProcessGroup(service)
                server.supervisor.reloadConfig()
                #server.supervisor.startProcess(service)
            elif action == 'stop':
                server.supervisor.stopProcess(service)
            elif action == 'restart':
                server.supervisor.stopProcess(service)

                server.supervisor.reloadConfig()
                server.supervisor.removeProcessGroup(service)
                server.supervisor.reloadConfig()
                server.supervisor.addProcessGroup(service)
                server.supervisor.reloadConfig()
                #server.supervisor.startProcess(service)
        except Exception as e:
            return { 'status': '-401', 'statusText': str(e) }
        else:
            return { 'status': '0', 'statusText': 'Ok', 'data': [] }

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def start(self):
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        data = odr = json.loads(rawbody.decode('utf-8'))

        return self.serviceAction('start', data['service'])

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def stop(self):
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        data = odr = json.loads(rawbody.decode('utf-8'))

        return self.serviceAction('stop', data['service'])

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @require()
    def restart(self):
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        data = odr = json.loads(rawbody.decode('utf-8'))

        return self.serviceAction('restart', data['service'])
