#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2019 Yoann QUERET <yoann@queret.net>
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

class Config():
    def __init__(self, config_file):
        self.config_file = config_file
        self.load(config_file)

    def load(self, config_file):
        with open(self.config_file) as data_file:
            self.config = json.load(data_file)

    def initConfigurationChanged(self):
        global configurationChanged
        configurationChanged = {}
        for coder in self.config['odr']:
            #configurationChanged[coder['uniq_id']] = {'ODR-audioencoder': False, 'ODR-padencoder': False}
            self.addConfigurationChanged(coder['uniq_id'])

    def addConfigurationChanged(self, uniq_id):
        configurationChanged[uniq_id] = {'ODR-audioencoder': False, 'ODR-padencoder': False}

    def delConfigurationChanged(self, uniq_id):
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

                        if coderNew['source']['type'] != coderOld['source']['type']:
                            self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                        else:
                            if coderNew['source']['type'] == 'stream':
                                if coderNew['source']['driftcomp'] != coderOld['source']['driftcomp']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['source']['silence_detect'] != coderOld['source']['silence_detect']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['source']['silence_duration'] != coderOld['source']['silence_duration']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['source']['stream_url'] != coderOld['source']['stream_url']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['source']['stream_writeicytext'] != coderOld['source']['stream_writeicytext']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                            if coderNew['source']['type'] == 'alsa':
                                if coderNew['source']['driftcomp'] != coderOld['source']['driftcomp']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['source']['silence_detect'] != coderOld['source']['silence_detect']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['source']['silence_duration'] != coderOld['source']['silence_duration']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['source']['alsa_device'] != coderOld['source']['alsa_device']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                            if coderNew['source']['type'] == 'avt':
                                if coderNew['source']['avt_input_uri'] != coderOld['source']['avt_input_uri']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['source']['avt_control_uri'] != coderOld['source']['avt_control_uri']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['source']['avt_pad_port'] != coderOld['source']['avt_pad_port']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['source']['avt_jitter_size'] != coderOld['source']['avt_jitter_size']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['source']['avt_timeout'] != coderOld['source']['avt_timeout']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                            if coderNew['source']['type'] == 'aes67':
                                if coderNew['source']['aes67_sdp'] != coderOld['source']['aes67_sdp']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['source']['aes67_sdp_file'] != coderOld['source']['aes67_sdp_file']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)

                        if coderNew['output']['type'] != coderOld['output']['type']:
                            self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                        else:
                            if coderNew['output']['type'] == 'dabp':
                                if coderNew['output']['bitrate'] != coderOld['output']['bitrate']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['output']['channels'] != coderOld['output']['channels']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['output']['samplerate'] != coderOld['output']['samplerate']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)

                                if coderNew['output']['dabp_sbr'] != coderOld['output']['dabp_sbr']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['output']['dabp_ps'] != coderOld['output']['dabp_ps']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['output']['dabp_afterburner'] != coderOld['output']['dabp_afterburner']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)

                                # check output
                                if isOutputNotEqual(coderNew['output']['zmq_output'], coderOld['output']['zmq_output'], ['name']):
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)

                            if coderNew['output']['type'] == 'dab':
                                if coderNew['output']['bitrate'] != coderOld['output']['bitrate']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['output']['channels'] != coderOld['output']['channels']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['output']['samplerate'] != coderOld['output']['samplerate']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)

                                if coderNew['output']['dab_dabmode'] != coderOld['output']['dab_dabmode']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                if coderNew['output']['dab_dabpsy'] != coderOld['output']['dab_dabpsy']:
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)

                                # check output
                                if isOutputNotEqual(coderNew['output']['zmq_output'], coderOld['output']['zmq_output'], ['name']):
                                    self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)

                        if coderNew['padenc']['enable'] != coderOld['padenc']['enable']:
                            self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                            self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-padencoder', True)
                        else:
                            if coderNew['padenc']['slide_sleeping'] != coderOld['padenc']['slide_sleeping']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-padencoder', True)
                            if coderNew['padenc']['slide_directory'] != coderOld['padenc']['slide_directory']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-padencoder', True)
                            if coderNew['padenc']['slide_once'] != coderOld['padenc']['slide_once']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-padencoder', True)
                            if coderNew['padenc']['raw_dls'] != coderOld['padenc']['raw_dls']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-padencoder', True)
                            if coderNew['padenc']['uniform'] != coderOld['padenc']['uniform']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-padencoder', True)
                            if coderNew['padenc']['uniform_init_burst'] != coderOld['padenc']['uniform_init_burst']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-padencoder', True)
                            if coderNew['padenc']['uniform_label'] != coderOld['padenc']['uniform_label']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-padencoder', True)
                            if coderNew['padenc']['uniform_label_ins'] != coderOld['padenc']['uniform_label_ins']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-padencoder', True)
                            if coderNew['padenc']['pad'] != coderOld['padenc']['pad']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-padencoder', True)
                            if coderNew['padenc']['pad_fifo'] != coderOld['padenc']['pad_fifo']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-padencoder', True)
                            if coderNew['padenc']['dls_file'] != coderOld['padenc']['dls_file']:
                                self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-audioencoder', True)
                                self.setConfigurationChanged(coderNew['uniq_id'], 'ODR-padencoder', True)


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
        self.load(self.config_file)
        odr = []
        for coder in self.config['odr']:
            if 'padenc' in coder:
                if not 'uniform' in coder['padenc']:
                    coder['padenc']['uniform'] = 'false'
                if 'pad_fifo_file' in coder['padenc']:
                    coder['padenc']['pad_fifo'] = coder['padenc']['pad_fifo_file']
                    del coder['padenc']['pad_fifo_file']
                if 'dls_fifo_file' in coder['padenc']:
                    coder['padenc']['dls_file'] = coder['padenc']['dls_fifo_file']
                    del coder['padenc']['dls_fifo_file']
            if 'source' in coder:
                if not 'stream_writeicytext' in coder['source']:
                    coder['source']['stream_writeicytext'] = 'true'
                if not 'silence_detect' in coder['source']:
                    coder['source']['silence_detect'] = 'false'
                if not 'silence_duration' in coder['source']:
                    coder['source']['silence_duration'] = '30'
                if 'device' in coder['source']:
                    coder['source']['alsa_device'] = coder['source']['device']
                    del coder['source']['device']
                if 'url' in coder['source']:
                    coder['source']['stream_url'] = coder['source']['url']
                    del coder['source']['url']
            odr.append(coder)
        # Write configuration file
        output = { 'global': self.config['global'], 'auth': self.config['auth'], 'odr': odr }
        self.write(output, False)
        self.load(self.config_file)

    def checkSupervisorProcess(self):
        self.load(self.config_file)
        try:
            server = xmlrpc_client.ServerProxy(self.config['global']['supervisor_xmlrpc'])
        except Exception as e:
            return {'status': '-211', 'statusText': 'Error when connect to supervisor XMLRPC: ' + str(e)}

        try:
            programs = server.supervisor.getAllProcessInfo()
        except Exception as e:
            return {'status': '-212', 'statusText': 'Error when retreive supervisor process: ' + str(e)}

        # Remove unused ODR-audioencoder & ODR-padencoder
        for process in programs:
            if process['name'].startswith('ODR-audioencoder') or process['name'].startswith('ODR-padencoder'):
                if process['name'].startswith('ODR-audioencoder'):
                    uuid = process['name'][17:]

                if process['name'].startswith('ODR-padencoder'):
                    uuid = process['name'][15:]

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
                if coder['padenc']['enable'] == 'true':
                    if not self.is_program_exist(programs, 'ODR-padencoder-%s'  % (coder['uniq_id'])):
                        try:
                            server.supervisor.reloadConfig()
                            server.supervisor.addProcessGroup('ODR-padencoder-%s' % (coder['uniq_id']))
                        except Exception as e:
                            return {'status': '-207', 'statusText': 'Error when starting ODR-padencoder (XMLRPC): ' + str(e)}

                if not self.is_program_exist(programs, 'ODR-audioencoder-%s' % (coder['uniq_id'])):
                    try:
                        server.supervisor.reloadConfig()
                        server.supervisor.addProcessGroup('ODR-audioencoder-%s' % (coder['uniq_id']))
                    except Exception as e:
                        return {'status': '-206', 'statusText': 'Error when starting ODR-audioencoder (XMLRPC): ' + str(e)}

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
                    command = odr['path']['padenc_path']
                    command += ' -v'
                    if odr['padenc']['slide_directory'].strip() != '':
                        # Check if config.mot_slide_directory exist
                        if os.path.exists(odr['padenc']['slide_directory']):
                            command += ' --dir=%s' % (odr['padenc']['slide_directory'])
                            if odr['padenc']['slide_once'] == 'true':
                                command += ' --erase'
                        else:
                            # Try to create slide_directory
                            try:
                                os.makedirs(odr['padenc']['slide_directory'])
                            except Exception as e:
                                raise ValueError('Error when creating slide directory: {}'.format(e))

                            # If config.mot_slide_directory start with /pad/slide/live/, try to create carousel directory if not exist
                            # Ideally check if /pad/slide/live/ is tmfs
                            if odr['padenc']['slide_directory'].startswith('/pad/slide/live/'):
                                try:
                                    os.makedirs('/pad/slide/carousel/'+odr['padenc']['slide_directory'].replace('/pad/slide/live/', ''))
                                except Exception as e:
                                    raise ValueError('Error when creating slide directory: {}'.format(e))

                    # Check if config.mot_dls_file exist and create it if needed.
                    if not os.path.isfile(odr['padenc']['dls_file']):
                        try:
                            f = open(odr['padenc']['dls_file'], 'w')
                            f.close()
                            os.chmod(odr['padenc']['dls_file'], 0o775)
                        except Exception as e:
                            raise ValueError('Error when create DLS file: {}'.format(e))

                    # Check if config.mot_pad_fifo exist and create it if needed.
                    if not os.path.exists(odr['padenc']['pad_fifo']):
                        try:
                            os.mkfifo(odr['padenc']['pad_fifo'])
                        except Exception as e:
                            raise ValueError('Error when create PAD fifo: {}'.format(e))
                    else:
                        if not stat.S_ISFIFO(os.stat(odr['padenc']['pad_fifo']).st_mode):
                            #File %s is not a fifo
                            pass

                    if odr['padenc']['slide_sleeping']:
                        command += ' --sleep=%s' % (odr['padenc']['slide_sleeping'])
                    else:
                        command += ' --sleep=10'
                    if odr['padenc']['pad']:
                        command += ' --pad=%s' % (odr['padenc']['pad'])
                    else:
                        command += ' --pad=34'
                    command += ' --dls=%s' % (odr['padenc']['dls_file'])
                    command += ' --output=%s' % (odr['padenc']['pad_fifo'])

                    if odr['padenc']['raw_dls'] == 'true':
                        command += ' --raw-dls'

                    # UNIFORM
                    if odr['padenc']['uniform'] == 'true':
                        # DAB+
                        if odr['output']['type'] == 'dabp':
                            if odr['output']['dabp_sbr'] == 'false':
                                # AAC_LC
                                if odr['output']['samplerate'] == '48000':
                                    command += ' --frame-dur=20'
                                elif odr['output']['samplerate'] == '32000':
                                    command += ' --frame-dur=30'
                            elif odr['output']['dabp_sbr'] == 'true':
                                # HE_AAC
                                if odr['output']['samplerate'] == '48000':
                                    command += ' --frame-dur=40'
                                elif odr['output']['samplerate'] == '32000':
                                    command += ' --frame-dur=60'

                        # DAB
                        if odr['output']['type'] == 'dab':
                            if odr['output']['samplerate'] == '48000':
                                command += ' --frame-dur=24'
                            elif odr['output']['samplerate'] == '24000':
                                command += ' --frame-dur=48'

                        # DAB+ / DAB Common
                        if odr['padenc']['uniform_label']:
                            command += ' --label=%s' % (odr['padenc']['uniform_label'])
                        else:
                            command += ' --label=12'

                        if odr['padenc']['uniform_label_ins']:
                            command += ' --label-ins=%s' % (odr['padenc']['uniform_label_ins'])
                        else:
                            command += ' --label-ins=1200'

                        if odr['padenc']['uniform_init_burst']:
                            command += ' --init-burst=%s' % (odr['padenc']['uniform_init_burst'])
                        else:
                            command += ' --init-burst=12'


                    supervisorConfig += "# %s\n" % (odr['name'])
                    supervisorConfig += "[program:ODR-padencoder-%s]\n" % (odr['uniq_id'])
                    supervisorConfig += "command=%s\n" % (command)
                    supervisorConfig += "autostart=true\n"
                    supervisorConfig += "autorestart=true\n"
                    supervisorConfig += "priority=10\n"
                    supervisorConfig += "user=odr\n"
                    supervisorConfig += "group=odr\n"
                    supervisorConfig += "stderr_logfile=/var/log/supervisor/ODR-padencoder-%s.log\n" % (odr['uniq_id'])
                    supervisorConfig += "stdout_logfile=/var/log/supervisor/ODR-padencoder-%s.log\n" % (odr['uniq_id'])
                    supervisorConfig += "\n"

                # Write supervisor audioencoder section
                # Encoder path
                if odr['source']['type'] == 'alsa' or odr['source']['type'] == 'stream' or odr['source']['type'] == 'aes67':
                    command = odr['path']['encoder_path']
                if odr['source']['type'] == 'avt':
                    command = odr['path']['sourcecompanion_path']

                # Input stream
                if odr['source']['type'] == 'alsa':
                    command += ' --device %s' % (odr['source']['alsa_device'])
                if odr['source']['type'] == 'stream':
                    command += ' --vlc-uri=%s' % (odr['source']['stream_url'])
                if odr['source']['type'] == 'aes67':
                    command += ' --vlc-uri=file://%s' % (odr['source']['aes67_sdp_file'])
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
                    command += ' --drift-comp'

                # silence restart for alsa or stream or aes input type only
                if ( odr['source']['type'] == 'alsa' or odr['source']['type'] == 'stream' or odr['source']['type'] == 'aes67' ) and odr['source']['silence_detect'] == 'true' and odr['source']['silence_duration'] != '' and int(odr['source']['silence_duration']) >> 0:
                    command += ' --silence=%s' % (odr['source']['silence_duration'])

                # bitrate, samplerate, channels for all input type
                command += ' --bitrate=%s' % (odr['output']['bitrate'])
                command += ' --rate=%s' % (odr['output']['samplerate'])
                command += ' --channels=%s' % (odr['output']['channels'])

                # DAB specific option only for alsa or stream or aes input type
                if ( odr['source']['type'] == 'alsa' or odr['source']['type'] == 'stream' or odr['source']['type'] == 'aes67' ) and odr['output']['type'] == 'dab':
                    command += ' --dab'
                    command += ' --dabmode=%s' % (odr['output']['dab_dabmode'])
                    command += ' --dabpsy=%s' % (odr['output']['dab_dabpsy'])

                # DAB+ specific option for all input type
                if odr['output']['type'] == 'dabp':
                    if odr['output']['dabp_sbr'] == 'true':
                        command += ' --sbr'
                    if odr['output']['dabp_ps'] == 'true':
                        command += ' --ps'
                    if odr['output']['dabp_sbr'] == 'false' and config['odr']['output']['dabp_ps'] == 'false':
                        command += ' --aaclc'
                    # Disable afterburner only for alsa or stream or aes input type
                    if ( odr['source']['type'] == 'alsa' or odr['source']['type'] == 'stream' or odr['source']['type'] == 'aes67' ) and odr['output']['dabp_afterburner'] == 'false':
                        command += ' --no-afterburner'

                # PAD encoder
                if odr['padenc']['enable'] == 'true':
                    if os.path.exists(odr['padenc']['pad_fifo']) and stat.S_ISFIFO(os.stat(odr['padenc']['pad_fifo']).st_mode):
                        command += ' --pad=%s' % (odr['padenc']['pad'])
                        command += ' --pad-fifo=%s' % (odr['padenc']['pad_fifo'])
                        # Write icy-text only for stream input type and if writeicytext is true
                        if odr['source']['type'] == 'stream' and odr['source']['stream_writeicytext'] == 'true':
                            command += ' --write-icy-text=%s' % (odr['padenc']['dls_file'])

                # AVT input type specific option
                if odr['source']['type'] == 'avt':
                    command += ' --input-uri=%s' % (odr['source']['avt_input_uri'])
                    command += ' --control-uri=%s' % (odr['source']['avt_control_uri'])
                    command += ' --timeout=%s' % (odr['source']['avt_timeout'])
                    command += ' --jitter-size=%s' % (odr['source']['avt_jitter_size'])
                    if odr['padenc']['enable'] == 'true':
                        command += ' --pad-port=%s' % (odr['source']['avt_pad_port'])

                # Output
                for out in odr['output']['zmq_output']:
                    if out['enable'] == 'true':
                        command += ' -o tcp://%s:%s' % (out['host'], out['port'])

                supervisorConfig += "# %s\n" % (odr['name'])
                supervisorConfig += "[program:ODR-audioencoder-%s]\n" % (odr['uniq_id'])
                supervisorConfig += "command=%s\n" % (command)
                supervisorConfig += "autostart=true\n"
                supervisorConfig += "autorestart=true\n"
                supervisorConfig += "priority=10\n"
                supervisorConfig += "user=odr\n"
                supervisorConfig += "group=odr\n"
                supervisorConfig += "stderr_logfile=/var/log/supervisor/ODR-audioencoder-%s.log\n" % (odr['uniq_id'])
                supervisorConfig += "stdout_logfile=/var/log/supervisor/ODR-audioencoder-%s.log\n" % (odr['uniq_id'])
                supervisorConfig += "\n"

        try:
            with open(config['global']['supervisor_file'], 'w') as supfile:
                supfile.write(supervisorConfig)
        except Exception as e:
            raise ValueError('Error when writing supervisor file: {}'.format(e))
