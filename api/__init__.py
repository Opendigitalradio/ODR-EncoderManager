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
import xmlrpclib

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
        return """This is the api area."""
    
    @cherrypy.expose
    @require()
    def reboot(self):
        command = 'sudo /sbin/shutdown -r now'
        p_status = subprocess.call(command, shell=True)

        cherrypy.response.headers["Content-Type"] = "application/json"
        if int(p_status) != 0:
            return json.dumps({'status': '-299', 'statusText': 'Can not process reboot - %s ' % (int(p_status))})
        else:
            return json.dumps({'status': '0', 'statusText': 'Ok'})

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
            except Exception,e:
                pass
            
            # Read tmp config.json file
            with open('/tmp/config.json') as data_file:
                output = json.load(data_file)

            # Remove config.json file
            try:
                os.remove('/tmp/config.json')
            except Exception,e:
                pass

            # Write configuration file
            try:
                self.conf.write(output)
            except Exception,e:
                cherrypy.response.headers["Content-Type"] = "application/json"
                return json.dumps({'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)})

            # Generate supervisor files
            try:
                self.conf.generateSupervisorFiles(output)
            except Exception,e:
                cherrypy.response.headers["Content-Type"] = "application/json"
                return json.dumps({'status': '-202', 'statusText': 'Error generating supervisor files' + str(e)})
            
            # Generate network files
            try:
                self.conf.generateNetworkFiles(output)
            except Exception,e:
                cherrypy.response.headers["Content-Type"] = "application/json"
                return json.dumps({'status': '-202', 'statusText': 'Error when writing network file' + str(e)})


            # Check if ODR program availaible in supervisor ProcessInfo and try to add it

            # Retreive supervisor process
            server = xmlrpclib.Server(self.conf.config['global']['supervisor_xmlrpc'])
            programs = server.supervisor.getAllProcessInfo()

            # Check for ODR-audioencoder
            if not self.is_program_exist(programs, 'ODR-audioencoder'):
                try:
                    server.supervisor.reloadConfig()
                    server.supervisor.addProcessGroup('ODR-audioencoder')
                except:
                    cherrypy.response.headers["Content-Type"] = "application/json"
                    return json.dumps({'status': '-206', 'statusText': 'Error when starting ODR-audioencoder (XMLRPC): ' + str(e)})

            # Check for ODR-padencoder
            if not self.is_program_exist(programs, 'ODR-padencoder'):
                try:
                    server.supervisor.reloadConfig()
                    server.supervisor.addProcessGroup('ODR-padencoder')
                except:
                    cherrypy.response.headers["Content-Type"] = "application/json"
                    return json.dumps({'status': '-207', 'statusText': 'Error when starting ODR-padencoder (XMLRPC): ' + str(e)})

            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '0', 'statusText': 'Ok'})
        else:
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '-200', 'statusText': 'Uploaded file is not a zip file'})

    @cherrypy.expose
    @require()
    def getNetworkDNS(self, **params):
        self.conf = Config(self.config_file)
        query = parse_query_string(cherrypy.request.query_string)

        data = self.conf.config['global']['network']['dns']
        
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps({'status': '0', 'statusText': 'Ok', 'data': data})

    @cherrypy.expose
    @require()
    def setNetworkDNS(self):
        self.conf = Config(self.config_file)
        
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        param = json.loads(rawbody)
        
        output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': self.conf.config['odr'] }
        
        output['global']['network']['dns'] = param
        
        # Write configuration file
        try:
            self.conf.write(output)
        except Exception,e:
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)})
        
        
        # Generate network files
        try:
            self.conf.generateNetworkFiles(output)
        except Exception,e:
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '-201', 'statusText': 'Error when writing network file: ' + str(e)})
        
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps({'status': '0', 'statusText': 'Ok'})
    
    @cherrypy.expose
    @require()
    def getNetworkNTP(self, **params):
        self.conf = Config(self.config_file)
        query = parse_query_string(cherrypy.request.query_string)

        data = self.conf.config['global']['network']['ntp']
        
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps({'status': '0', 'statusText': 'Ok', 'data': data})

    @cherrypy.expose
    @require()
    def setNetworkNTP(self):
        self.conf = Config(self.config_file)
        
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        param = json.loads(rawbody)
        
        output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': self.conf.config['odr'] }
        
        output['global']['network']['ntp'] = param
        
        # Write configuration file
        try:
            self.conf.write(output)
        except Exception,e:
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)})
        
        
        # Generate network files
        try:
            self.conf.generateNetworkFiles(output)
        except Exception,e:
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '-201', 'statusText': 'Error when writing network file: ' + str(e)})
        
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps({'status': '0', 'statusText': 'Ok'})

    @cherrypy.expose
    @require()
    def restartNTP(self):
        command = 'sudo /usr/sbin/service ntp restart'
        p_status = subprocess.call(command, shell=True)

        cherrypy.response.headers["Content-Type"] = "application/json"
        if int(p_status) != 0:
            return json.dumps({'status': '-299', 'statusText': 'Can not process restart - %s ' % (int(p_status))})
        else:
            return json.dumps({'status': '0', 'statusText': 'Ok'})

    @cherrypy.expose
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
            
        
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps({'status': '0', 'statusText': 'Ok', 'data': data})
    
    @cherrypy.expose
    @require()
    def setNetworkCard(self):
        self.conf = Config(self.config_file)
        
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        param = json.loads(rawbody)
        
        output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': self.conf.config['odr'] }
        
        change = None    
        for i,value in enumerate(output['global']['network']['cards']):
            if value['card'] == param['card']:
                output['global']['network']['cards'][i]['dhcp'] = param['dhcp']
                output['global']['network']['cards'][i]['ip'] = param['ip']
                output['global']['network']['cards'][i]['netmask'] = param['netmask']
                output['global']['network']['cards'][i]['gateway'] = param['gateway']
                change = True
        if not change:
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '-201', 'statusText': 'Card not found: ' + str(e)})
                
        # Write configuration file
        try:
            self.conf.write(output)
        except Exception,e:
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)})
        
        
        # Generate network files
        try:
            self.conf.generateNetworkFiles(output)
        except Exception,e:
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '-202', 'statusText': 'Error generating network files' + str(e)})
        
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps({'status': '0', 'statusText': 'Ok'})
        
    @cherrypy.expose
    @require()
    def getConfig(self):
        self.conf = Config(self.config_file)
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps({'status': '0', 'statusText': 'Ok', 'data': self.conf.config['odr']})
    
    @cherrypy.expose
    @require()
    def getAlsaDevices(self):
        cherrypy.response.headers["Content-Type"] = "application/json"
        command = '/usr/bin/arecord -l'
        try:
                output = subprocess.check_output(command,
                                    shell=True,
                                    stderr=subprocess.STDOUT)
        except:
                return json.dumps({'status': '-200', 'statusText': 'Error listing alsa devices', 'data': ''})
        return json.dumps({'status': '0', 'statusText': 'Ok', 'data': output})
    
    @cherrypy.expose
    @require()
    def setConfig(self):
        self.conf = Config(self.config_file)
        
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        odr = json.loads(rawbody)
        
        output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': odr }
        
        # Write configuration file
        try:
            self.conf.write(output)
        except Exception,e:
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)})
        
        # Generate supervisor files
        try:
            self.conf.generateSupervisorFiles(output)
        except Exception,e:
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '-202', 'statusText': 'Error generating supervisor files' + str(e)})
        
        
        # Check if ODR program availaible in supervisor ProcessInfo and try to add it
        
        # Retreive supervisor process
        server = xmlrpclib.Server(self.conf.config['global']['supervisor_xmlrpc'])
        programs = server.supervisor.getAllProcessInfo()
        
        # Check for ODR-audioencoder
        if not self.is_program_exist(programs, 'ODR-audioencoder'):
            try:
                server.supervisor.reloadConfig()
                server.supervisor.addProcessGroup('ODR-audioencoder')
            except:
                cherrypy.response.headers["Content-Type"] = "application/json"
                return json.dumps({'status': '-206', 'statusText': 'Error when starting ODR-audioencoder (XMLRPC): ' + str(e)})
        
        # Check for ODR-padencoder
        if not self.is_program_exist(programs, 'ODR-padencoder'):
            try:
                server.supervisor.reloadConfig()
                server.supervisor.addProcessGroup('ODR-padencoder')
            except:
                cherrypy.response.headers["Content-Type"] = "application/json"
                return json.dumps({'status': '-207', 'statusText': 'Error when starting ODR-padencoder (XMLRPC): ' + str(e)})
        
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps({'status': '0', 'statusText': 'Ok'})
    
    
    @cherrypy.expose
    def setDLS(self, **params):
        self.conf = Config(self.config_file)
        
        query = parse_query_string(cherrypy.request.query_string)

        # Check is json output is needed
        if 'json' in query:
            ojson = True
        else:
            ojson = None  
        
        # DLS (odr-padenc process) is enable
        if self.conf.config['odr']['padenc']['enable'] == 'true':
            # dls parameters is present and override all other
            if 'dls' in query:
                try:
                    with codecs.open(self.conf.config['odr']['padenc']['dls_fifo_file'], 'w', 'utf-8') as outfile:
                        outfile.write(query['dls'])
                except Exception,e:
                    r = {'status': '-210', 'statusText': 'Fail to write dls data'}
                    if ojson:
                        cherrypy.response.headers["Content-Type"] = "application/json"
                        return json.dumps(r)
                    else:
                        return r['statusText']
                else:
                    r = {'status': '0', 'statusText': 'Ok', 'dls': query['dls']}
                    if ojson:
                       cherrypy.response.headers["Content-Type"] = "application/json"
                       return json.dumps(r)
                    else:
                       return r['statusText']
            # dls is not present and artist and title are available    
            elif ('artist' in query) and ('title' in query):
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
                    except Exception,e:
                        r = {'status': '-210', 'statusText': 'Fail to write dls data'}
                        if ojson:
                            cherrypy.response.headers["Content-Type"] = "application/json"
                            return json.dumps(r)
                        else:
                            return r['statusText']
                    else:
                        r = {'status': '0', 'statusText': 'Ok', 'dls': { 'artist': query['artist'], 'title': query['title']} }
                        if ojson:
                            cherrypy.response.headers["Content-Type"] = "application/json"
                            return json.dumps(r)
                        else:
                            return r['statusText']
                else:
                    r = {'status': '-215', 'statusText': 'Error, artist or title are blank'}
                    if ojson:
                        cherrypy.response.headers["Content-Type"] = "application/json"
                        return json.dumps(r)
                    else:
                        return r['statusText']

            # no needed parameters available
            else:
                r = {'status': '-209', 'statusText': 'Error, you need to use dls or artist + title parameters'}
                if ojson:
                    cherrypy.response.headers["Content-Type"] = "application/json"
                    return json.dumps(r)
                else:
                    return r['statusText']

        # DLS (odr-padenc process) is disable
        else:
            r = {'status': '-208', 'statusTest': 'DLS is disable'}
            if ojson:
                cherrypy.response.headers["Content-Type"] = "application/json"
                return json.dumps(r)
            else:
                return r['statusText']
    
    
    
    @cherrypy.expose
    @require()
    def getDLS(self):
        dls=None
        dlplus=None
        self.conf = Config(self.config_file)
        cherrypy.response.headers["Content-Type"] = "application/json"
        
        if self.conf.config['odr']['padenc']['enable'] == 'true':
            try:
                with open(self.conf.config['odr']['padenc']['dls_fifo_file'], 'r') as f:
                    for line in f:
                        if line.startswith('#'):
                            continue
                        if line.startswith('DL_PLUS='):
                            #dlplus={'artist': '', 'title': ''}
                            continue
                        if line.startswith('DL_PLUS_TAG='):
                            #v = line.split("=", 1)
                            #d = v[1].split(" ")
                            #if d[0] == 4:
                                #dartist={'start': d[1], 'len': d[2]}
                            #if d[0] == 1:
                                #dtitle={'start': d[1], 'len': d[2]}
                            continue
                        dls = line.rstrip()
            except Exception,e:
                return json.dumps({'dls': 'Fail to read dls data'})
            else:
                ## TODO : add DL PLUS Support to return
                if dlplus:
                    dlplus['artist'] = ''
                    dlplus['title'] = ''
                    return json.dumps({'dls': str(dls), 'dlplus': dlplus})
                else:
                    return json.dumps({'dls': str(dls)})
        else:
            return json.dumps({'dls': 'DLS is disable ...'})
    
    def is_program_exist(self, json, program):
        ex = False
        for p in json:
            if p['name'] == program :
                ex = True
        return ex
    
    @cherrypy.expose
    @require()
    def getUser(self):
        self.conf = Config(self.config_file)
        cherrypy.response.headers["Content-Type"] = "application/json"
        users = self.conf.config['auth']['users']
        data = []
        for u in users :
            data.append( {'username': u['username']} )
        return json.dumps({'status': '0', 'statusText': 'Ok', 'data': data})
    
    @cherrypy.expose
    @require()
    def addUser(self):
        self.conf = Config(self.config_file)
        
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        param = json.loads(rawbody)
        
        output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': self.conf.config['odr'] }
        
        userexist = None    
        for i,value in enumerate(output['auth']['users']):
            if value['username'] == param['username']:
                userexist = True
        if not userexist:
            output['auth']['users'].append({'username': param['username'], 'password': hashlib.md5(param['password']).hexdigest()});
        else:
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '-201', 'statusText': 'User already exist'})
                
        # Write configuration file
        try:
            self.conf.write(output)
        except Exception,e:
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)})
        
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps({'status': '0', 'statusText': 'Ok'})
    
    @cherrypy.expose
    @require()
    def setPasswd(self):
        self.conf = Config(self.config_file)
        
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        param = json.loads(rawbody)
        
        output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': self.conf.config['odr'] }
        
        change = None    
        for i,value in enumerate(output['auth']['users']):
            if value['username'] == param['username']:
                output['auth']['users'][i]['password'] = hashlib.md5(param['password']).hexdigest()
                change = True
        if not change:
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '-201', 'statusText': 'User not found: ' + str(e)})
                
        # Write configuration file
        try:
            self.conf.write(output)
        except Exception,e:
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)})
        
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps({'status': '0', 'statusText': 'Ok'})
        
    @cherrypy.expose
    @require()
    def delUser(self):
        self.conf = Config(self.config_file)
        
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        param = json.loads(rawbody)
        
        output = { 'global': self.conf.config['global'], 'auth': self.conf.config['auth'], 'odr': self.conf.config['odr'] }
        
        change = None    
        for i,value in enumerate(output['auth']['users']):
            if value['username'] == param['username']:
                output['auth']['users'].pop(i)
                change = True
        if not change:
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '-201', 'statusText': 'User not found: ' + str(e)})
                
        # Write configuration file
        try:
            self.conf.write(output)
        except Exception,e:
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps({'status': '-201', 'statusText': 'Error when writing configuration file: ' + str(e)})
        
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps({'status': '0', 'statusText': 'Ok'})
    
    @cherrypy.expose
    @require()
    def getStatus(self):
        self.conf = Config(self.config_file)
        cherrypy.response.headers["Content-Type"] = "application/json"
        server = xmlrpclib.Server(self.conf.config['global']['supervisor_xmlrpc'])
        output = []
        
        try:
            output.append( server.supervisor.getProcessInfo('ODR-audioencoder') )
            output.append( server.supervisor.getProcessInfo('ODR-padencoder') )
        except Exception,e:
            return json.dumps({'status': '-301', 'statusText': 'Error when getting ODR-audioencoder and ODR-padencoder status (XMLRPC): ' + str(e)})
        
        return json.dumps({'status': '0', 'statusText': 'Ok', 'data': output})
    
    
    def serviceAction(self, action, service):
        self.conf = Config(self.config_file)
        
        server = xmlrpclib.Server(self.conf.config['global']['supervisor_xmlrpc'])
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
        except Exception,e:
            return { 'status': '-401', 'statusText': str(e) }
        else:
            return { 'status': '0', 'statusText': 'Ok', 'data': [] }
    
    @cherrypy.expose
    @require()
    def start(self):
        cherrypy.response.headers["Content-Type"] = "application/json"
        
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        data = odr = json.loads(rawbody)
        
        return json.dumps(self.serviceAction('start', data['service']))
        
    @cherrypy.expose
    @require()
    def stop(self):
        cherrypy.response.headers["Content-Type"] = "application/json"
        
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        data = odr = json.loads(rawbody)
        
        return json.dumps(self.serviceAction('stop', data['service']))
    
    @cherrypy.expose
    @require()
    def restart(self):
        cherrypy.response.headers["Content-Type"] = "application/json"
        
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        data = odr = json.loads(rawbody)
        
        return json.dumps(self.serviceAction('restart', data['service']))
