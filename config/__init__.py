#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2020 Yoann QUERET <yoann@queret.net>
"""

"""
This file is part of ODR-EncoderManager.

ODR-EncoderManager is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ODR-EncoderManager is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ODR-EncoderManager.  If not, see <http://www.gnu.org/licenses/>.
"""

#import ConfigParser
import os
import sys
import json
import stat
import socket
import yaml
import uuid
import time

if sys.version_info >= (3, 0):
    from xmlrpc import client as xmlrpc_client
else:
    import xmlrpclib as xmlrpc_client



def is_network(config_file):
    conf = Config(config_file)
    if ('network' in conf.config['global']) and ('networkInterfaces_file' in conf.config['global']):
        return True
    else:
        return False
    
def is_adcast(config_file):
    conf = Config(config_file)
    if ('adcast' in conf.config['global']) and (conf.config['global']['adcast'] == True or conf.config['global']['adcast'] == 'true'):
        if ('slide_mgnt' in conf.config['global']) and (conf.config['global']['slide_mgnt'] == True or conf.config['global']['slide_mgnt'] == 'true'):
            return True
        else:
            return False
    else:
        return False
    
def is_slide_mgnt(config_file):
    conf = Config(config_file)
    if ('slide_mgnt' in conf.config['global']) and (conf.config['global']['slide_mgnt'] == True or conf.config['global']['slide_mgnt'] == 'true'):
        return True
    else:
        return False

class Config():
    def __init__(self, config_file):
        self.config_file = config_file
        self.load(config_file)

    def load(self, config_file):
        with open(self.config_file) as data_file:
            self.config = json.load(data_file)

    ## Audio socket Management
    def initAudioSocket(self):
        global audioSocket
        audioSocket = {}

    def addAudioSocket(self):
        self.load(self.config_file)
        for coder in self.config['odr']:
            if all (k in coder for k in ("source","output","padenc","path")):
                if not coder['uniq_id'] in audioSocket:
                    print ('add stats socket %s' % (coder['uniq_id']), flush=True)
                    audioSocket[coder['uniq_id']] = {}
                    audioSocket[coder['uniq_id']]['uniq_id'] = coder['uniq_id']
                    audioSocket[coder['uniq_id']]['stats_socket'] = coder['source']['stats_socket']
                    audioSocket[coder['uniq_id']]['status'] = '-504'
                    audioSocket[coder['uniq_id']]['statusText'] = 'Unknown'
                    audioSocket[coder['uniq_id']]['data'] = {}
                    audioSocket[coder['uniq_id']]['timestamp'] = None
                    audioSocket[coder['uniq_id']]['socket'] = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
                    #audioSocket[coder['uniq_id']]['socket'].settimeout(1)
                    audioSocket[coder['uniq_id']]['socket'].setblocking(False)
                    if os.path.exists(audioSocket[coder['uniq_id']]['stats_socket']):
                        #print ('Socket already exist try to unlink %s' % (audioSocket[coder['uniq_id']]['stats_socket']), flush=True)
                        try:
                            os.unlink(audioSocket[coder['uniq_id']]['stats_socket'])
                        except OSError:
                            #print ('!! Could not unlink socket', flush=True)
                            audioSocket[coder['uniq_id']]['status'] = '-502'
                            audioSocket[coder['uniq_id']]['statusText'] = 'Could not unlink socket'
                            audioSocket[coder['uniq_id']]['data'] = {}
                        else:
                            #print ('Ok', flush=True)
                            audioSocket[coder['uniq_id']]['status'] = '-512'
                            audioSocket[coder['uniq_id']]['statusText'] = 'Ok - Waiting first data'
                            audioSocket[coder['uniq_id']]['data'] = {}
                    
                    #print ('Try to bind socket %s' % (audioSocket[coder['uniq_id']]['stats_socket']), flush=True)
                    try:
                        audioSocket[coder['uniq_id']]['socket'].bind(audioSocket[coder['uniq_id']]['stats_socket'])
                    except socket.timeout as err:
                        #print ('!! socket timeout', flush=True)
                        audioSocket[coder['uniq_id']]['status'] = '-503'
                        audioSocket[coder['uniq_id']]['statusText'] = 'socket timeout'
                        audioSocket[coder['uniq_id']]['data'] = {}
                    except socket.error as err:
                        #print ('!! socket error: %s' % (err), flush=True)
                        audioSocket[coder['uniq_id']]['status'] = '-503'
                        audioSocket[coder['uniq_id']]['statusText'] = 'socket error: %s' % (err)
                        audioSocket[coder['uniq_id']]['data'] = {}
                    else:
                        #print ('Ok', flush=True)
                        audioSocket[coder['uniq_id']]['status'] = '-513'
                        audioSocket[coder['uniq_id']]['statusText'] = 'Ok - Waiting first data'
                        audioSocket[coder['uniq_id']]['data'] = {}
                else:
                    if audioSocket[coder['uniq_id']]['stats_socket'] != coder['source']['stats_socket']:
                        # Stats socket changed - remove entry (recreated next loop)
                        print ('stats socket changed, remove it %s' % (coder['uniq_id']), flush=True)
                        audioSocket[coder['uniq_id']]['socket'].close()
                        del audioSocket[coder['uniq_id']]


        # Remove old socket #
        audioSocketToRemove = []
        for uniq_id in audioSocket:
            if not any(c['uniq_id'] == uniq_id for c in self.config['odr']):
                audioSocketToRemove.append(uniq_id)

        for uniq_id in audioSocketToRemove:
            #print ('del socket', uniq_id)
            print ('remove stats socket %s' % (audioSocket[uniq_id]), flush=True)
            audioSocket[uniq_id]['socket'].close()
            del audioSocket[uniq_id]

    def retreiveAudioSocket(self):
        for uniq_id in audioSocket:
            try:
                data, addr = audioSocket[uniq_id]['socket'].recvfrom(1024)
            except socket.timeout as err:
                audioSocket[uniq_id]['status'] = '-502'
                audioSocket[uniq_id]['statusText'] = 'socket timeout'
                audioSocket[uniq_id]['data'] = {}
            except socket.error as err:
                if err.errno != 11:
                    audioSocket[uniq_id]['status'] = '-502'
                    audioSocket[uniq_id]['statusText'] = 'socket error: %s' % (err)
                    audioSocket[uniq_id]['data'] = {}
                else:
                    if audioSocket[uniq_id]['timestamp'] and ((time.time() - audioSocket[uniq_id]['timestamp']) > 2):
                        audioSocket[uniq_id]['status'] = '-501'
                        audioSocket[uniq_id]['statusText'] = 'no data'
                        audioSocket[uniq_id]['data'] = {}
            else:
                ydata = yaml.load(data)
                audioSocket[uniq_id]['status'] = '0'
                audioSocket[uniq_id]['statusText'] = 'Ok'
                audioSocket[uniq_id]['data'] = ydata
                audioSocket[uniq_id]['timestamp'] = time.time()

    def delAudioSocket(self, uniq_id):
        audioSocket[uniq_id]['socket'].close()
        del audioSocket[uniq_id]

    def getAudioSocket(self, uniq_id):
        if uniq_id in audioSocket:
            output = {'uniq_id': audioSocket[uniq_id]['uniq_id'],
                      'stats_socket': audioSocket[uniq_id]['stats_socket'],
                      'status': audioSocket[uniq_id]['status'],
                      'statusText': audioSocket[uniq_id]['statusText'],
                      'data': audioSocket[uniq_id]['data'],
                      'timestamp': audioSocket[uniq_id]['timestamp'],
                      }
            return output
        else:
            output = {'uniq_id': uniq_id,
                      'status': '-500',
                      'statusText': 'No running stats socket available for this uniq_id',
                      'data': {},
                      }
            return output

    # Configuration Change Management
    def initConfigurationChanged(self):
        global configurationChanged
        configurationChanged = {}
        for coder in self.config['odr']:
            self.addConfigurationChanged(coder['uniq_id'])

    def addConfigurationChanged(self, uniq_id):
        configurationChanged[uniq_id] = {'odr-audioencoder': False, 'odr-padencoder': False, 'slide-mgnt': False, 'adcast': False}

    def delConfigurationChanged(self, uniq_id):
        if uniq_id in configurationChanged:
            del configurationChanged[uniq_id]

    def getConfigurationChanged(self, uniq_id, process):
        if uniq_id in configurationChanged:
            return configurationChanged[uniq_id][process]
        else:
            return None

    def setConfigurationChanged(self, uniq_id, service, status):
        configurationChanged[uniq_id][service] = status

    def applyConfigurationChanged(self, config):
        def isOutputNotEqual(new, old, ignore_keys = []):
            newTemp = []
            oldTemp = []

            for l in new:
                v = {}
                for dk, dv in l.items():
                    if dk in ignore_keys:
                        pass
                    else:
                        v[dk] = dv
                newTemp.append(v)
            for l in old:
                v = {}
                for dk, dv in l.items():
                    if dk in ignore_keys:
                        pass
                    else:
                        v[dk] = dv
                oldTemp.append(v)

            return newTemp != oldTemp

        for coderNew in config['odr']:
            for coderOld in self.config['odr']:
                if coderNew['uniq_id'] == coderOld['uniq_id']:
                    if all (k in coderOld for k in ("source","output","padenc","path")):

                        if coderNew['uniq_id'] not in configurationChanged:
                            self.addConfigurationChanged(coderNew['uniq_id'])

                        if coderNew['source']['stats_socket'] != coderOld['source']['stats_socket']:
                            self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)

                        # odr-audioencoder
                        if coderNew['source']['type'] != coderOld['source']['type']:
                            self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                        else:
                            if coderNew['source']['type'] == 'stream':
                                if coderNew['source']['driftcomp'] != coderOld['source']['driftcomp']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['source']['silence_detect'] != coderOld['source']['silence_detect']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['source']['silence_duration'] != coderOld['source']['silence_duration']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['source']['stream_url'] != coderOld['source']['stream_url']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['source']['stream_writeicytext'] != coderOld['source']['stream_writeicytext']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['source']['stream_lib'] != coderOld['source']['stream_lib']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                            if coderNew['source']['type'] == 'alsa':
                                if coderNew['source']['driftcomp'] != coderOld['source']['driftcomp']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['source']['silence_detect'] != coderOld['source']['silence_detect']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['source']['silence_duration'] != coderOld['source']['silence_duration']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['source']['alsa_device'] != coderOld['source']['alsa_device']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                            if coderNew['source']['type'] == 'avt':
                                if coderNew['source']['avt_input_uri'] != coderOld['source']['avt_input_uri']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['source']['avt_control_uri'] != coderOld['source']['avt_control_uri']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['source']['avt_pad_port'] != coderOld['source']['avt_pad_port']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['source']['avt_jitter_size'] != coderOld['source']['avt_jitter_size']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['source']['avt_timeout'] != coderOld['source']['avt_timeout']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                            if coderNew['source']['type'] == 'aes67':
                                if coderNew['source']['driftcomp'] != coderOld['source']['driftcomp']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['source']['silence_detect'] != coderOld['source']['silence_detect']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['source']['silence_duration'] != coderOld['source']['silence_duration']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['source']['aes67_sdp'] != coderOld['source']['aes67_sdp']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['source']['aes67_sdp_file'] != coderOld['source']['aes67_sdp_file']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)

                        if coderNew['output']['type'] != coderOld['output']['type']:
                            self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                        else:
                            if coderNew['output']['bitrate'] != coderOld['output']['bitrate']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                            if coderNew['output']['channels'] != coderOld['output']['channels']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                            if coderNew['output']['samplerate'] != coderOld['output']['samplerate']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                            
                            if coderNew['output']['type'] == 'dabp':
                                if coderNew['output']['dabp_sbr'] != coderOld['output']['dabp_sbr']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['output']['dabp_ps'] != coderOld['output']['dabp_ps']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['output']['dabp_afterburner'] != coderOld['output']['dabp_afterburner']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)

                            if coderNew['output']['type'] == 'dab':
                                if coderNew['output']['dab_dabmode'] != coderOld['output']['dab_dabmode']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                if coderNew['output']['dab_dabpsy'] != coderOld['output']['dab_dabpsy']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)

                                    
                            # check output
                            if isOutputNotEqual(coderNew['output']['output'], coderOld['output']['output'], ['name']):
                                self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                            
                            # check EDI specific parameters
                            if coderNew['output']['edi_identifier'] != coderOld['output']['edi_identifier']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                            if coderNew['output']['edi_timestamps_delay'] != coderOld['output']['edi_timestamps_delay']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)

                        # odr-padenc
                        if coderNew['padenc']['enable'] != coderOld['padenc']['enable']:
                            self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                        else:
                            if coderNew['padenc']['slide_sleeping'] != coderOld['padenc']['slide_sleeping']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'odr-padencoder', True)
                            if coderNew['padenc']['slide_directory'] != coderOld['padenc']['slide_directory']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'odr-padencoder', True)
                                if ('slide_mgnt' in config['global'] and (config['global']['slide_mgnt'] == True or config['global']['slide_mgnt'] == 'true') ):
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'slide-mgnt', True)
                                    
                            # CHECK ADCAST / SLIDE-MGNT slide directory 
                            if ('slide_mgnt' in config['global'] and (config['global']['slide_mgnt'] == True or config['global']['slide_mgnt'] == 'true') )\
                                and 'slide_directory_live' in coderNew['padenc']\
                                and 'slide_directory_live' in coderOld['padenc']\
                                and coderNew['padenc']['slide_directory_live'] != coderOld['padenc']['slide_directory_live']:        
                                self.setConfigurationChanged(coderNew['uniq_id'], 'slide-mgnt', True)
                                
                            if ('slide_mgnt' in config['global'] and (config['global']['slide_mgnt'] == True or config['global']['slide_mgnt'] == 'true') )\
                                and 'slide_directory_carousel' in coderNew['padenc']\
                                and 'slide_directory_carousel' in coderOld['padenc']\
                                and coderNew['padenc']['slide_directory_carousel'] != coderOld['padenc']['slide_directory_carousel']:        
                                self.setConfigurationChanged(coderNew['uniq_id'], 'slide-mgnt', True)
                                
                            if ('slide_mgnt' in config['global'] and (config['global']['slide_mgnt'] == True or config['global']['slide_mgnt'] == 'true') )\
                                and 'slide_directory_ads' in coderNew['padenc']\
                                and 'slide_directory_ads' in coderOld['padenc']\
                                and coderNew['padenc']['slide_directory_ads'] != coderOld['padenc']['slide_directory_ads']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'slide-mgnt', True)
                                if ('adcast' in config['global'] and (config['global']['adcast'] == True or config['global']['adcast'] == 'true') )\
                                    and 'adcast' in coderNew\
                                    and 'adcast' in coderOld:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'adcast', True)
                            
                            # CHECK SLIDE-MGNT slide interval/liftime
                            if ('slide_mgnt' in config['global'] and (config['global']['slide_mgnt'] == True or config['global']['slide_mgnt'] == 'true') )\
                                and 'slide_carousel_interval' in coderNew['padenc']\
                                and 'slide_carousel_interval' in coderOld['padenc']\
                                and coderNew['padenc']['slide_carousel_interval'] != coderOld['padenc']['slide_carousel_interval']:        
                                self.setConfigurationChanged(coderNew['uniq_id'], 'slide-mgnt', True)
                                
                            if ('slide_mgnt' in config['global'] and (config['global']['slide_mgnt'] == True or config['global']['slide_mgnt'] == 'true') )\
                                and 'slide_live_interval' in coderNew['padenc']\
                                and 'slide_live_interval' in coderOld['padenc']\
                                and coderNew['padenc']['slide_live_interval'] != coderOld['padenc']['slide_live_interval']:        
                                self.setConfigurationChanged(coderNew['uniq_id'], 'slide-mgnt', True)
                                
                            if ('slide_mgnt' in config['global'] and (config['global']['slide_mgnt'] == True or config['global']['slide_mgnt'] == 'true') )\
                                and 'slide_live_lifetime' in coderNew['padenc']\
                                and 'slide_live_lifetime' in coderOld['padenc']\
                                and coderNew['padenc']['slide_live_lifetime'] != coderOld['padenc']['slide_live_lifetime']:        
                                self.setConfigurationChanged(coderNew['uniq_id'], 'slide-mgnt', True)
                                
                                
                            
                            if coderNew['padenc']['slide_once'] != coderOld['padenc']['slide_once']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'odr-padencoder', True)
                            if coderNew['padenc']['raw_dls'] != coderOld['padenc']['raw_dls']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'odr-padencoder', True)
                            if coderNew['padenc']['raw_slides'] != coderOld['padenc']['raw_slides']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'odr-padencoder', True)
                            if coderNew['padenc']['uniform_label'] != coderOld['padenc']['uniform_label']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'odr-padencoder', True)
                            if coderNew['padenc']['uniform_label_ins'] != coderOld['padenc']['uniform_label_ins']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'odr-padencoder', True)
                            if coderNew['padenc']['pad'] != coderOld['padenc']['pad']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                            if coderNew['padenc']['dls_file'] != coderOld['padenc']['dls_file']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'odr-audioencoder', True)
                                self.setConfigurationChanged(coderNew['uniq_id'], 'odr-padencoder', True)
                            
                        # adcast
                        if ('adcast' in config['global'] and (config['global']['adcast'] == True or config['global']['adcast'] == 'true') )\
                            and ('slide_mgnt' in config['global'] and (config['global']['slide_mgnt'] == True or config['global']['slide_mgnt'] == 'true') ):
                            if 'adcast' not in coderOld:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'adcast', True)
                            else:
                                if coderNew['adcast']['enable'] != coderOld['adcast']['enable']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'adcast', True)
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'slide-mgnt', True)
                                if coderNew['adcast']['api_token'] != coderOld['adcast']['api_token']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'adcast', True)
                                if coderNew['adcast']['uuid'] != coderOld['adcast']['uuid']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'adcast', True)
                                if coderNew['adcast']['api_url'] != coderOld['adcast']['api_url']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'adcast', True)
                                if coderNew['adcast']['listen_addr'] != coderOld['adcast']['listen_addr']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'adcast', True)
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'slide-mgnt', True)
                                
                                

    def write(self, config, checkConfigurationChanged=True):
        if checkConfigurationChanged:
            self.applyConfigurationChanged(config)

        try:
            with open(self.config_file, 'w') as outfile:
                data = json.dumps(config, indent=4, separators=(',', ': '))
                outfile.write(data)
        except Exception as e:
            raise ValueError(str(e))

    def is_program_exist(self, json, program):
        return any(p['name'] == program for p in json)

    def is_program_running(self, json, program):
        return any(p['name'] == program and p['statename'] == 'RUNNING' for p in json)

    def checkConfigurationFile(self):
        print ('Check configuration file ...')
        self.load(self.config_file)
        odr = []
        for coder in self.config['odr']:
            if not 'name' in coder:
                coder['name'] = 'my coder'
                print ('- add coder name in configuration file')
            if not 'description' in coder:
                coder['description'] = 'my coder description'
                print ('- add coder description in configuration file')
            if not 'uniq_id' in coder:
                coder['uniq_id'] = str(uuid.uuid4())
                print ('- add coder uniq_id in configuration file')
            if not 'autostart' in coder:
                coder['autostart'] = 'true'

            if 'padenc' in coder:
                if 'uniform' in coder['padenc']:
                    del coder['padenc']['uniform']
                    print ('- remove uniform in configuration file')
                if 'uniform_init_burst' in coder['padenc']:
                    del coder['padenc']['uniform_init_burst']
                    print ('- remove uniform_init_burst in configuration file')
                if not 'uniform_label' in coder['padenc']:
                    coder['padenc']['uniform_label'] = '12'
                    print ('- add uniform_label pad in configuration file')
                if not 'uniform_label_ins' in coder['padenc']:
                    coder['padenc']['uniform_label_ins'] = '1200'
                    print ('- add uniform_label pad in configuration file')
                if 'pad_fifo_file' in coder['padenc']:
                    del coder['padenc']['pad_fifo_file']
                    print ('- remove pad_fifo_file in configuration file')
                if 'pad_fifo' in coder['padenc']:
                    del coder['padenc']['pad_fifo']
                    print ('- remove pad_fifo in configuration file')
                if 'dls_fifo_file' in coder['padenc']:
                    coder['padenc']['dls_file'] = coder['padenc']['dls_fifo_file']
                    del coder['padenc']['dls_fifo_file']
                    print ('- rename dls_fifo_file to dls_file in configuration file')    
                if not 'slide_carousel_interval' in coder['padenc']:
                    coder['padenc']['slide_carousel_interval'] = ''
                if not 'slide_live_interval' in coder['padenc']:
                    coder['padenc']['slide_live_interval'] = ''
                if not 'slide_live_lifetime' in coder['padenc']:
                    coder['padenc']['slide_live_lifetime'] = ''
                if not 'raw_slides' in coder['padenc']:
                    coder['padenc']['raw_slides'] = 'false'
                    
            if 'source' in coder:
                if not 'stats_socket' in coder['source']:
                    coder['source']['stats_socket'] = '/var/tmp/'+coder['uniq_id']+'.stats'
                    print ('- add stats_socket in configuration file')
                if not 'stream_writeicytext' in coder['source']:
                    coder['source']['stream_writeicytext'] = 'true'
                    print ('- add stream_writeicytext in configuration file')
                if not 'silence_detect' in coder['source']:
                    coder['source']['silence_detect'] = 'false'
                    print ('- add silence_detect in configuration file')
                if not 'silence_duration' in coder['source']:
                    coder['source']['silence_duration'] = '30'
                    print ('- add silence_duration in configuration file')
                if 'device' in coder['source']:
                    coder['source']['alsa_device'] = coder['source']['device']
                    del coder['source']['device']
                    print ('- rename device to alsa_device in configuration file')
                if 'url' in coder['source']:
                    coder['source']['stream_url'] = coder['source']['url']
                    del coder['source']['url']
                    print ('- rename url to stream_url in configuration file')
                if not 'stream_url' in coder['source']:
                    coder['source']['stream_url'] = ''
                    print ('- add stream_url in configuration file')
                if not 'stream_lib' in coder['source']:
                    coder['source']['stream_lib'] = 'vlc'
                    print ('- add stream_lib in configuration file')
                    
            if 'output' in coder:
                if 'zmq_output' in coder['output']:
                    print ('- rename zmq_output to output in configuration file')
                    newOutput = []
                    for o in coder['output']['zmq_output']:
                        o['type'] = 'zmq'
                        newOutput.append(o)
                    coder['output']['output'] = newOutput
                    del coder['output']['zmq_output']
                if 'edi_identifier' not in coder['output']:
                    coder['output']['edi_identifier'] = ''
                    print ('- add edi_identifier to output in configuration file')
                if 'edi_timestamps_delay' not in coder['output']:
                    coder['output']['edi_timestamps_delay'] = ''
                    print ('- add edi_timestamps_delay to output in configuration file')
            odr.append(coder)
        # Write configuration file
        output = { 'global': self.config['global'], 'auth': self.config['auth'], 'odr': odr }
        self.write(output, False)
        self.load(self.config_file)

    def checkSupervisorProcess(self):
        print ('Check supervisor process ...')
        self.load(self.config_file)
        try:
            server = xmlrpc_client.ServerProxy(self.config['global']['supervisor_xmlrpc'])
        except Exception as e:
            raise ValueError( 'Can not connect to supervisor XMLRPC: ' + str(e) )
            #return {'status': '-211', 'statusText': 'Error when connect to supervisor XMLRPC: ' + str(e)}

        try:
            programs = server.supervisor.getAllProcessInfo()
        except Exception as e:
            raise ValueError( 'Can not retreive supervisor process: ' + str(e) )
            #return {'status': '-212', 'statusText': 'Error when retreive supervisor process: ' + str(e)}

        # Remove unused ODR-audioencoder & ODR-padencoder
        for process in programs:
            if process['name'].startswith('odr-audioencoder-') or process['name'].startswith('odr-padencoder-') or process['name'].startswith('slide-mgnt-') or process['name'].startswith('adcast-'):
                uuid = process['name'][-36:]

                if not any(c['uniq_id'] == uuid for c in self.config['odr']):
                    try:
                        if self.is_program_running(programs, process['name']):
                            server.supervisor.stopProcess(process['name'])
                            server.supervisor.reloadConfig()
                        server.supervisor.removeProcessGroup(process['name'])
                        server.supervisor.reloadConfig()
                    except Exception as e:
                        raise ValueError( 'Error when removing process %s (XMLRPC): %s' % (process['name'], str(e)) )

        # Add new ODR-audioencoder & ODR-padencoder
        try:
            self.generateSupervisorFiles(self.config)
        except Exception as e:
            raise ValueError( 'Error when generating new supervisor files: ' + str(e) )

        # Add new supervisor configuration
        for coder in self.config['odr']:
            if all (k in coder for k in ("source","output","padenc","path")):
                
                # odr-audioencoder
                if not self.is_program_exist(programs, 'odr-audioencoder-%s' % (coder['uniq_id'])):
                    try:
                        server.supervisor.reloadConfig()
                        server.supervisor.addProcessGroup('odr-audioencoder-%s' % (coder['uniq_id']))
                    except Exception as e:
                        raise ValueError( 'Error when starting odr-audioencoder (XMLRPC): ' % (process['name'], str(e)) )
                
                # odr-padencoder
                if coder['padenc']['enable'] == 'true':
                    if not self.is_program_exist(programs, 'odr-padencoder-%s'  % (coder['uniq_id'])):
                        try:
                            server.supervisor.reloadConfig()
                            server.supervisor.addProcessGroup('odr-padencoder-%s' % (coder['uniq_id']))
                        except Exception as e:
                            raise ValueError( 'Error when starting odr-padencoder (XMLRPC): ' % (process['name'], str(e)) )
                    
                # slide-mgnt
                if coder['padenc']['enable'] == 'true'\
                    and 'slide_mgnt' in self.config['global']\
                    and (self.config['global']['slide_mgnt'] == True or self.config['global']['slide_mgnt'] == 'true')\
                    and 'slide_directory_live' in coder['padenc']\
                    and 'slide_directory_carousel' in coder['padenc']\
                    and 'slide_directory_ads' in coder['padenc']:
                        
                    if not self.is_program_exist(programs, 'slide-mgnt-%s'  % (coder['uniq_id'])):
                        try:
                            server.supervisor.reloadConfig()
                            server.supervisor.addProcessGroup('slide-mgnt-%s' % (coder['uniq_id']))
                        except Exception as e:
                            raise ValueError( 'Error when starting slide-mgnt (XMLRPC): ' % (process['name'], str(e)) )
                
                # adcast
                if coder['padenc']['enable'] == 'true'\
                    and ('slide_mgnt' in self.config['global'] and (self.config['global']['slide_mgnt'] == True or self.config['global']['slide_mgnt'] == 'true') )\
                    and ('adcast' in self.config['global'] and (self.config['global']['adcast'] == True or self.config['global']['adcast'] == 'true') )\
                    and ('adcast' in coder and coder['adcast']['enable'] == 'true'):
                        
                    if not self.is_program_exist(programs, 'adcast-%s'  % (coder['uniq_id'])):
                        try:
                            server.supervisor.reloadConfig()
                            server.supervisor.addProcessGroup('adcast-%s' % (coder['uniq_id']))
                        except Exception as e:
                            raise ValueError( 'Error when starting adcast (XMLRPC): ' % (process['name'], str(e)) )

    def generateNetworkFiles(self, config):
        # Write network/interfaces file
        networkInterfaces  = "# This file is generated by ODR-EncoderManager\n"
        networkInterfaces += "# Please use WebGUI to make changes\n"
        networkInterfaces += "\n"
        networkInterfaces += "auto lo\n"
        networkInterfaces += "iface lo inet loopback\n"
        networkInterfaces += "\n"
        for card in config['global']['network']['cards']:
            if card['dhcp'] == "true":
                networkInterfaces += "allow-hotplug %s\n" % (card['card'])
                networkInterfaces += "iface %s inet %s\n" % (card['card'], 'dhcp')
            else:
                if (card['ip'].strip() != "") and (card['netmask'].strip() != ""):
                    networkInterfaces += "allow-hotplug %s\n" % (card['card'])
                    networkInterfaces += "iface %s inet %s\n" % (card['card'], 'static')
                    networkInterfaces += "    address %s\n" % (card['ip'])
                    networkInterfaces += "    netmask %s\n" % (card['netmask'])
                    if card['gateway'].strip() != "":
                        networkInterfaces += "    gateway %s\n" % (card['gateway'])
            if 'route' in card:
              for route in card['route']:
                networkInterfaces += "    up /bin/ip route add %s dev %s\n" % (route.strip(), card['card'])
            networkInterfaces += "\n"

        try:
            with open(config['global']['networkInterfaces_file'], 'w') as supfile:
                supfile.write(networkInterfaces)
        except Exception as e:
            raise ValueError('Error when writing network/interfaces file: {}'.format(e))

        # Write network/DNS file
        networkDNS  = "# This file is generated by ODR-EncoderManager\n"
        networkDNS += "# Please use WebGUI to make changes\n"
        networkDNS += "\n"
        for server in config['global']['network']['dns']:
            networkDNS += "nameserver %s\n" % (server)
        networkDNS += "\n"

        try:
            with open(config['global']['networkDNS_file'], 'w') as supfile:
                supfile.write(networkDNS)
        except Exception as e:
            raise ValueError('Error when writing network/DNS file: {}'.format(e))

        # Write network/NTP file
        networkNTP  = "# This file is generated by ODR-EncoderManager\n"
        networkNTP += "# Please use WebGUI to make changes\n"
        networkNTP += "\n"
        networkNTP += "driftfile /var/lib/ntp/ntp.drift\n"
        networkNTP += "\n"
        networkNTP += "statistics loopstats peerstats clockstats\n"
        networkNTP += "filegen loopstats file loopstats type day enable\n"
        networkNTP += "filegen peerstats file peerstats type day enable\n"
        networkNTP += "filegen clockstats file clockstats type day enable\n"
        networkNTP += "\n"
        for server in config['global']['network']['ntp']:
            networkNTP += "server %s iburst\n" % (server)
        networkNTP += "\n"
        networkNTP += "# By default, exchange time with everybody, but don't allow configuration.\n"
        networkNTP += "restrict -4 default kod notrap nomodify nopeer noquery\n"
        networkNTP += "restrict -6 default kod notrap nomodify nopeer noquery\n"
        networkNTP += "\n"
        networkNTP += "# Local users may interrogate the ntp server more closely.\n"
        networkNTP += "restrict 127.0.0.1\n"
        networkNTP += "restrict ::1\n"
        networkNTP += "\n"

        try:
            with open(config['global']['networkNTP_file'], 'w') as supfile:
                supfile.write(networkNTP)
        except Exception as e:
            raise ValueError('Error when writing network/NTP file: {}'.format(e))

    def generateSupervisorFiles(self, config):
        supervisorConfig = ""
        for odr in config['odr']:
            if all (k in odr for k in ("source","output","padenc","path")):
                # Write supervisor pad-encoder section
                if odr['padenc']['enable'] == 'true':
                    command = '%s\n' % (odr['path']['padenc_path'])
                    #command += ' -v\n'
                    if odr['padenc']['slide_directory'].strip() != '':
                        # Check if config.mot_slide_directory exist
                        if os.path.exists(odr['padenc']['slide_directory']):
                            command += ' --dir=%s\n' % (odr['padenc']['slide_directory'])
                            if odr['padenc']['slide_once'] == 'true':
                                command += ' --erase\n'
                        else:
                            # Try to create slide_directory
                            try:
                                os.makedirs(odr['padenc']['slide_directory'])
                            except Exception as e:
                                raise ValueError('Error when creating slide directory: {}'.format(e))

                    if 'slide_directory_live' in odr['padenc']:
                        if not os.path.exists(odr['padenc']['slide_directory_live']):
                            try:
                                os.makedirs(odr['padenc']['slide_directory_live'])
                            except Exception as e:
                                raise ValueError('Error when creating live slide directory: {}'.format(e))
                            
                    if 'slide_directory_carousel' in odr['padenc']:
                        if not os.path.exists(odr['padenc']['slide_directory_carousel']):
                            try:
                                os.makedirs(odr['padenc']['slide_directory_carousel'])
                            except Exception as e:
                                raise ValueError('Error when creating carousel slide directory: {}'.format(e))
                            
                    if 'slide_directory_ads' in odr['padenc']:
                        if not os.path.exists(odr['padenc']['slide_directory_ads']):
                            try:
                                os.makedirs(odr['padenc']['slide_directory_ads'])
                            except Exception as e:
                                raise ValueError('Error when creating ads slide directory: {}'.format(e))


                    # Check if config.mot_dls_file exist and create it if needed.
                    if not os.path.isfile(odr['padenc']['dls_file']):
                        # Check if directory exist
                        if not os.path.exists( os.path.dirname(odr['padenc']['dls_file']) ):
                            try:
                                os.makedirs( os.path.dirname(odr['padenc']['dls_file']) )
                            except Exception as e:
                                raise ValueError('Error when creating dls_file directory: {}'.format(e))
                        
                        # Create file
                        try:
                            f = open(odr['padenc']['dls_file'], 'w')
                            f.close()
                            os.chmod(odr['padenc']['dls_file'], 0o775)
                        except Exception as e:
                            raise ValueError('Error when create DLS file: {}'.format(e))

                    # Check if config.mot_pad_fifo exist and create it if needed.
                    #if not os.path.exists(odr['padenc']['pad_fifo']):
                        #try:
                            #os.mkfifo(odr['padenc']['pad_fifo'])
                        #except Exception as e:
                            #raise ValueError('Error when create PAD fifo: {}'.format(e))
                    #else:
                        #if not stat.S_ISFIFO(os.stat(odr['padenc']['pad_fifo']).st_mode):
                            ##File %s is not a fifo
                            #pass

                    if odr['padenc']['slide_sleeping']:
                        command += ' --sleep=%s\n' % (odr['padenc']['slide_sleeping'])
                    else:
                        command += ' --sleep=10\n'
                    command += ' --dls=%s\n' % (odr['padenc']['dls_file'])
                    command += ' --output=%s\n' % (odr['uniq_id'])

                    if odr['padenc']['raw_dls'] == 'true':
                        command += ' --raw-dls\n'
                        
                    if odr['padenc']['raw_slides'] == 'true':
                        command += ' --raw-slides\n'

                    # UNIFORM
                    # DAB+ / DAB Common
                    if odr['padenc']['uniform_label']:
                        command += ' --label=%s\n' % (odr['padenc']['uniform_label'])
                    else:
                        command += ' --label=12\n'

                    if odr['padenc']['uniform_label_ins']:
                        command += ' --label-ins=%s\n' % (odr['padenc']['uniform_label_ins'])
                    else:
                        command += ' --label-ins=1200\n'


                    supervisorConfig += "# %s\n" % (odr['name'])
                    supervisorConfig += "[program:odr-padencoder-%s]\n" % (odr['uniq_id'])
                    supervisorConfig += "command=%s" % (command)
                    
                    # -- default parameters
                    supervisorConfigParam = {}
                    supervisorConfigParam['autostart'] = odr['autostart']
                    supervisorConfigParam['autorestart'] = "true"
                    supervisorConfigParam['priority'] = "10"
                    supervisorConfigParam['user'] = "odr"
                    supervisorConfigParam['group'] = "odr"
                    supervisorConfigParam['redirect_stderr'] = "true"
                    supervisorConfigParam['stdout_logfile'] = "/var/log/supervisor/odr-padencoder-%s.log" % (odr['uniq_id'])
                    
                    # -- override default parameters or add additional parameters
                    if 'supervisor_additional_options' in odr:
                        for key in odr['supervisor_additional_options'].keys():
                            supervisorConfigParam[key] = odr['supervisor_additional_options'][key]
                    
                    # -- generate final padencoder supervisor configuration
                    for key in supervisorConfigParam.keys():
                        supervisorConfig += "%s=%s\n" % (key, supervisorConfigParam[key])
                    supervisorConfig += "\n"

                # Write supervisor audioencoder section
                # Encoder path
                if odr['source']['type'] == 'alsa' or odr['source']['type'] == 'stream' or odr['source']['type'] == 'aes67':
                    command = '%s\n' % (odr['path']['encoder_path'])
                if odr['source']['type'] == 'avt':
                    command = '%s\n' % (odr['path']['sourcecompanion_path'])

                # Input stream
                if odr['source']['type'] == 'alsa':
                    command += ' --device %s\n' % (odr['source']['alsa_device'])
                if odr['source']['type'] == 'stream':
                    if odr['source']['stream_lib'] == 'vlc':
                        command += ' --vlc-uri=%s\n' % (odr['source']['stream_url'])
                    if odr['source']['stream_lib'] == 'gst':
                        command += ' --gst-uri=%s\n' % (odr['source']['stream_url'])
                if odr['source']['type'] == 'aes67':
                    command += ' --vlc-uri=file://%s\n' % (odr['source']['aes67_sdp_file'])
                    # Write SDP file
                    # Check if config.source.aes67_sdp_file exist and create it if needed.
                    if not os.path.isfile(odr['source']['aes67_sdp_file']):
                        try:
                            f = open(odr['source']['aes67_sdp_file'], 'w')
                            f.close()
                            os.chmod(odr['source']['aes67_sdp_file'], 0o775)
                        except Exception as e:
                            raise ValueError('Error when create SDP file: {}'.format(e))
                    # Write SDP file
                    try:
                        with open(odr['source']['aes67_sdp_file'], 'w') as f:
                            f.write(odr['source']['aes67_sdp'])
                    except Exception as e:
                        raise ValueError('Error when writing SDP file: {}'.format(e))

                # driftcomp for alsa or stream or aes input type only
                if ( odr['source']['type'] == 'alsa' or odr['source']['type'] == 'stream' or odr['source']['type'] == 'aes67' ) and odr['source']['driftcomp'] == 'true':
                    command += ' --drift-comp\n'

                # silence restart for alsa or stream or aes input type only
                if ( odr['source']['type'] == 'alsa' or odr['source']['type'] == 'stream' or odr['source']['type'] == 'aes67' ) and odr['source']['silence_detect'] == 'true' and odr['source']['silence_duration'] != '' and int(odr['source']['silence_duration']) >> 0:
                    command += ' --silence=%s\n' % (odr['source']['silence_duration'])

                # bitrate, samplerate, channels for all input type
                command += ' --bitrate=%s\n' % (odr['output']['bitrate'])
                command += ' --rate=%s\n' % (odr['output']['samplerate'])
                command += ' --channels=%s\n' % (odr['output']['channels'])

                # DAB specific option only for alsa or stream or aes input type
                if ( odr['source']['type'] == 'alsa' or odr['source']['type'] == 'stream' or odr['source']['type'] == 'aes67' ) and odr['output']['type'] == 'dab':
                    command += ' --dab\n'
                    command += ' --dabmode=%s\n' % (odr['output']['dab_dabmode'])
                    command += ' --dabpsy=%s\n' % (odr['output']['dab_dabpsy'])

                # DAB+ specific option for all input type
                if odr['output']['type'] == 'dabp':
                    if odr['output']['dabp_sbr'] == 'true':
                        command += ' --sbr\n'
                    if odr['output']['dabp_ps'] == 'true':
                        command += ' --ps\n'
                    if odr['output']['dabp_sbr'] == 'false' and odr['output']['dabp_ps'] == 'false':
                        command += ' --aaclc\n'
                    ## Disable afterburner only for alsa or stream or aes input type
                    if ( odr['source']['type'] == 'alsa' or odr['source']['type'] == 'stream' or odr['source']['type'] == 'aes67' ) and odr['output']['dabp_afterburner'] == 'false':
                        command += ' --no-afterburner\n'

                # PAD encoder
                if odr['padenc']['enable'] == 'true':
                    command += ' --pad=%s\n' % (odr['padenc']['pad'])
                    command += ' --pad-socket=%s\n' % (odr['uniq_id'])
                    # Write icy-text only for stream input type and if writeicytext is true
                    if odr['source']['type'] == 'stream' and odr['source']['stream_writeicytext'] == 'true':
                        command += ' --write-icy-text=%s\n' % (odr['padenc']['dls_file'])

                # AVT input type specific option
                if odr['source']['type'] == 'avt':
                    command += ' --input-uri=%s\n' % (odr['source']['avt_input_uri'])
                    command += ' --control-uri=%s\n' % (odr['source']['avt_control_uri'])
                    command += ' --timeout=%s\n' % (odr['source']['avt_timeout'])
                    command += ' --jitter-size=%s\n' % (odr['source']['avt_jitter_size'])
                    if odr['padenc']['enable'] == 'true':
                        command += ' --pad-port=%s\n' % (odr['source']['avt_pad_port'])

                # Output
                for out in odr['output']['output']:
                    if out['enable'] == 'true':
                        if out['type'] == 'zmq':
                            command += ' -o tcp://%s:%s\n' % (out['host'], out['port'])
                        if out['type'] == 'editcp':
                            command += ' -e tcp://%s:%s\n' % (out['host'], out['port'])

                # Stats socket
                if odr['source']['stats_socket'] != '':
                    command += ' --stats=%s\n' % (odr['source']['stats_socket'])
                
                # EDI specific
                if 'edi_identifier' in odr['output'] and odr['output']['edi_identifier'] != '':
                    command += ' --identifier=%s\n' % (odr['output']['edi_identifier'])
                
                if 'edi_timestamps_delay' in odr['output'] and odr['output']['edi_timestamps_delay'] != '':
                    command += ' --timestamp-delay=%s\n' % (odr['output']['edi_timestamps_delay'])

                supervisorConfig += "# %s\n" % (odr['name'])
                supervisorConfig += "[program:odr-audioencoder-%s]\n" % (odr['uniq_id'])
                supervisorConfig += "command=%s" % (command)
                
                # -- default parameters
                supervisorConfigParam = {}
                supervisorConfigParam['autostart'] = odr['autostart']
                supervisorConfigParam['autorestart'] = "true"
                supervisorConfigParam['priority'] = "10"
                supervisorConfigParam['user'] = "odr"
                supervisorConfigParam['group'] = "odr"
                supervisorConfigParam['redirect_stderr'] = "true"
                supervisorConfigParam['stdout_logfile'] = "/var/log/supervisor/odr-audioencoder-%s.log" % (odr['uniq_id'])
                    
                # -- override default parameters or add additional parameters
                if 'supervisor_additional_options' in odr:
                    for key in odr['supervisor_additional_options'].keys():
                        supervisorConfigParam[key] = odr['supervisor_additional_options'][key]
                
                # -- generate final audioencoder supervisor configuration
                for key in supervisorConfigParam.keys():
                    supervisorConfig += "%s=%s\n" % (key, supervisorConfigParam[key])
                supervisorConfig += "\n"
                
                # Write supervisor slide_mgnt section
                # If global.slide_mgnt is true
                if odr['padenc']['enable'] == 'true'\
                    and 'slide_mgnt' in config['global']\
                    and (config['global']['slide_mgnt'] == True or config['global']['slide_mgnt'] == 'true')\
                    and 'slide_directory_live' in odr['padenc']\
                    and 'slide_directory_carousel' in odr['padenc']\
                    and 'slide_directory_ads' in odr['padenc']:
                    
                    command = 'python3 /usr/local/bin/slide-mgnt.py\n'
                    #command += ' -v\n'
                    command += ' -w %s\n' % (odr['padenc']['slide_directory'])
                    command += ' -c %s\n' % (odr['padenc']['slide_directory_carousel'])
                    command += ' -l %s\n' % (odr['padenc']['slide_directory_live'])
                    if odr['padenc']['slide_live_lifetime'] != '':
                        command += ' -t %s\n' % (odr['padenc']['slide_live_lifetime'])
                    if odr['padenc']['slide_live_interval'] != '':
                        command += ' -i %s\n' % (odr['padenc']['slide_live_interval'])
                    if odr['padenc']['slide_carousel_interval'] != '':
                        command += ' -I %s\n' % (odr['padenc']['slide_carousel_interval'])
                    command += ' -a %s\n' % (odr['padenc']['slide_directory_ads'])
                    command += ' -A 35\n'
                    if ('adcast' in odr) and (odr['adcast']['enable'] == 'true'):
                        command += ' -s %s\n' % (odr['adcast']['listen_addr'])
                    if ('adcast' in odr) and (odr['adcast']['enable'] == 'true'):
                        command += ' -r\n'
                    
                    supervisorConfig += "# %s\n" % (odr['name'])
                    supervisorConfig += "[program:slide-mgnt-%s]\n" % (odr['uniq_id'])
                    supervisorConfig += "command=%s" % (command)
                    # -- default parameters
                    supervisorConfigParam = {}
                    supervisorConfigParam['autostart'] = odr['autostart']
                    supervisorConfigParam['autorestart'] = "true"
                    supervisorConfigParam['priority'] = "10"
                    supervisorConfigParam['user'] = "odr"
                    supervisorConfigParam['group'] = "odr"
                    supervisorConfigParam['redirect_stderr'] = "true"
                    supervisorConfigParam['stdout_logfile'] = "/var/log/supervisor/slide-%s.log" % (odr['uniq_id'])
                    
                    # -- override default parameters or add additional parameters
                    if 'supervisor_additional_options' in odr:
                        for key in odr['supervisor_additional_options'].keys():
                            supervisorConfigParam[key] = odr['supervisor_additional_options'][key]
                    
                    # -- generate final slide_mgnt supervisor configuration
                    for key in supervisorConfigParam.keys():
                        supervisorConfig += "%s=%s\n" % (key, supervisorConfigParam[key])
                    supervisorConfig += "\n"

                
                # Write supervisor adcast section
                if odr['padenc']['enable'] == 'true'\
                    and ('slide_mgnt' in config['global'] and (config['global']['slide_mgnt'] == True or config['global']['slide_mgnt'] == 'true') )\
                    and ('adcast' in config['global'] and (config['global']['adcast'] == True or config['global']['adcast'] == 'true') ):
                        
                    if ('adcast' in odr) and (odr['adcast']['enable'] == 'true'):
                        command = '/opt/adcast/bin/adcast-slide-controller run\n'
                        command += ' --api-token %s\n' % (odr['adcast']['api_token'])
                        command += ' --uuid %s\n' % (odr['adcast']['uuid'])
                        command += ' --dst-dir %s\n' % (odr['padenc']['slide_directory_ads'])
                        command += ' --listen-addr %s\n' % (odr['adcast']['listen_addr'])
                        
                        supervisorConfig += "# %s\n" % (odr['name'])
                        supervisorConfig += "[program:adcast-%s]\n" % (odr['uniq_id'])
                        supervisorConfig += "command=%s" % (command)
                        # -- default parameters
                        supervisorConfigParam = {}
                        supervisorConfigParam['autostart'] = odr['autostart']
                        supervisorConfigParam['autorestart'] = "true"
                        supervisorConfigParam['priority'] = "10"
                        supervisorConfigParam['user'] = "odr"
                        supervisorConfigParam['group'] = "odr"
                        supervisorConfigParam['redirect_stderr'] = "true"
                        supervisorConfigParam['stdout_logfile'] = "/var/log/supervisor/adcast-%s.log" % (odr['uniq_id'])
                        # -- override default parameters or add additional parameters
                        if 'supervisor_additional_options' in odr:
                            for key in odr['supervisor_additional_options'].keys():
                                supervisorConfigParam[key] = odr['supervisor_additional_options'][key]
                        
                        # -- generate final adcast supervisor configuration
                        for key in supervisorConfigParam.keys():
                            supervisorConfig += "%s=%s\n" % (key, supervisorConfigParam[key])
                        supervisorConfig += "\n"
                    

                    

        try:
            with open(config['global']['supervisor_file'], 'w') as supfile:
                supfile.write(supervisorConfig)
        except Exception as e:
            raise ValueError('Error when writing supervisor file: {}'.format(e))
