#!/usr/bin/env python
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

# Pour compiler la MIB vous devez utiliser le script "mibdump.py"
# mibdump.py ./AVT-AE1-DABPLUS-GO-MIB


from pysnmp.hlapi import *
#from pysnmp.smi.view import MibViewController
import sys
import argparse
import json
import time
import datetime


class AVT():

    def __init__(self, snmp_host, snmp_port=161, snmp_community='public', snmp_version='v2c', snmp_timeout=1, snmp_retries=1):
        # Set SNMP version
        self.snmp_host = snmp_host
        self.snmp_port = snmp_port
        self.snmp_community = snmp_community
        if snmp_version == 'v1':
            self.snmp_version = 0
        elif snmp_version == 'v2c':
            self.snmp_version = 1
        else:
            self.snmp_version = 1
        self.snmp_timeout = snmp_timeout
        self.snmp_retries = snmp_retries

    def hexTimestampToDate(self, timestamp):
        def hextodec(h):
            return int(h, 16)

        if int(timestamp, 16) == 0:
            return 0
        else:
            year = '0x%s' % (timestamp[2:6])
            month = '0x%s' % (timestamp[6:8])
            day = '0x%s' % (timestamp[8:10])
            hour = '0x%s' % (timestamp[10:12])
            minutes = '0x%s' % (timestamp[12:14])
            seconds = '0x%s' % (timestamp[14:16])
            x= datetime.datetime(hextodec(year), hextodec(month), hextodec(day), hextodec(hour), hextodec(minutes), hextodec(seconds))
            return x.strftime('%Y-%m-%d %H:%M:%S')

    def get_AE1AlarmsTable(self):
        Table = []
        alarmNameIdx = {'2':'AlarmName', '3':'AlarmState', '4':'AlarmCount', '5':'AlarmBlockCount', '6':'AlarmDateTime'}
        alarmStateIdx = {'1':'true', '2':'false'}
        for errorIndication, \
            errorStatus, \
            errorIndex, \
            varBinds in nextCmd(SnmpEngine(),
                        CommunityData(self.snmp_community, mpModel=self.snmp_version),
                        UdpTransportTarget((self.snmp_host, self.snmp_port), timeout=self.snmp_timeout, retries=self.snmp_retries),
                        ContextData(),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.11.10.20.11.1.2')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.11.10.20.11.1.3')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.11.10.20.11.1.4')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.11.10.20.11.1.5')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.11.10.20.11.1.6')),
                        lookupMib=False,
                        lexicographicMode=False):

            if errorIndication:
                return { 'status': -10, 'statusText': str(errorIndication), 'data': [] }
            elif errorStatus:
                return { 'status': -10, 'statusText': str('%s at %s' % (
                        errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex)-1][0] or '?'
                    )), 'data': [] }
            else:
                pr = {}
                for varBind in varBinds:
                    p = '='.join([ x.prettyPrint() for x in varBind ])
                    p_idx = p[(p.rfind(".")+1):(p.find("="))]
                    p_name_idx = p[(p.rfind(".")-1):(p.find(".%s=" % (p_idx)))]
                    p_value = p[(p.find("=")+1):]

                    if p_name_idx == '3':
                        pr[alarmNameIdx[p_name_idx]] = alarmStateIdx[p_value]
                    elif p_name_idx == '6':
                        pr[alarmNameIdx[p_name_idx]] = self.hexTimestampToDate(p_value)
                    else:
                        pr[alarmNameIdx[p_name_idx]] = p_value
                Table.append(pr)

        if len(Table) >> 0:
            return { 'status': 0, 'statusText': 'Ok', 'data': Table }
        else:
            return { 'status': -1, 'statusText': 'Empty', 'data': [] }

    def get_AE1EncoderTable(self):
        Table = []
        encoderNameIdx = {'10':'Algorithm', '11':'AudioMode', '12':'SamplFreq', '13':'DataRate', '20':'PadRate', '30':'AudioLevelLeft', '31':'AudioLevelRight', '40':'State', '50':'OnAir'}
        encoderAlgorithmIdx = {'1':'dabL2', '2':'dabPlusAac'}
        encoderAudioModeIdx = {'9':'mono', '10':'stereo', '11':'parametricStereo', '12':'monoSbr', '13':'stereoSbr'}
        encoderStateIdx = {'1':'disconnect', '2':'running', '3':'noNetwork', '4':'audioError', '5':'inactive', '6':'audioErrorCleared'}
        encoderOnAirIdx = {'1':'true', '2':'false'}
        for errorIndication, \
            errorStatus, \
            errorIndex, \
            varBinds in nextCmd(SnmpEngine(),
                        CommunityData(self.snmp_community, mpModel=self.snmp_version),
                        UdpTransportTarget((self.snmp_host, self.snmp_port), timeout=self.snmp_timeout, retries=self.snmp_retries),
                        ContextData(),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.11.10.50.11.1.10')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.11.10.50.11.1.11')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.11.10.50.11.1.12')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.11.10.50.11.1.13')),

                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.11.10.50.11.1.20')),

                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.11.10.50.11.1.30')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.11.10.50.11.1.31')),

                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.11.10.50.11.1.40')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.11.10.50.11.1.50')),
                        lookupMib=False,
                        lexicographicMode=False):

            if errorIndication:
                return { 'status': -10, 'statusText': str(errorIndication), 'data': [] }
            elif errorStatus:
                return { 'status': -10, 'statusText': str('%s at %s' % (
                        errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex)-1][0] or '?'
                    )), 'data': [] }
            else:
                pr = {}
                for varBind in varBinds:
                    p = '='.join([ x.prettyPrint() for x in varBind ])
                    p_idx = p[(p.rfind(".")+1):(p.find("="))]
                    p_name_idx = p[(p.rfind(".")-2):(p.find(".%s=" % (p_idx)))]
                    p_value = p[(p.find("=")+1):]

                    if p_name_idx == '10':
                        pr[encoderNameIdx[p_name_idx]] = encoderAlgorithmIdx[p_value]
                    elif p_name_idx == '11':
                        pr[encoderNameIdx[p_name_idx]] = encoderAudioModeIdx[p_value]
                    elif p_name_idx == '40':
                        pr[encoderNameIdx[p_name_idx]] = encoderStateIdx[p_value]
                    elif p_name_idx == '50':
                        pr[encoderNameIdx[p_name_idx]] = encoderOnAirIdx[p_value]
                    else:
                        pr[encoderNameIdx[p_name_idx]] = p_value
                Table.append(pr)
        if len(Table) >> 0:
            return { 'status': 0, 'statusText': 'Ok', 'data': Table }
        else:
            return { 'status': -1, 'statusText': 'Empty', 'data': [] }

    def get_AE4AlarmsTable(self):
        Table = []
        alarmNameIdx = {'2':'AlarmName', '3':'AlarmState', '4':'AlarmCount', '5':'AlarmBlockCount', '6':'AlarmDateTime'}
        alarmStateIdx = {'1':'true', '2':'false'}
        for errorIndication, \
            errorStatus, \
            errorIndex, \
            varBinds in nextCmd(SnmpEngine(),
                        CommunityData(self.snmp_community, mpModel=self.snmp_version),
                        UdpTransportTarget((self.snmp_host, self.snmp_port), timeout=self.snmp_timeout, retries=self.snmp_retries),
                        ContextData(),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.20.20.20.1.2')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.20.20.20.1.3')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.20.20.20.1.4')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.20.20.20.1.5')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.20.20.20.1.6')),
                        lookupMib=False,
                        lexicographicMode=False):

            if errorIndication:
                return { 'status': -10, 'statusText': str(errorIndication), 'data': [] }
            elif errorStatus:
                return { 'status': -10, 'statusText': str('%s at %s' % (
                        errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex)-1][0] or '?'
                    )), 'data': [] }
            else:
                pr = {}
                for varBind in varBinds:
                    p = '='.join([ x.prettyPrint() for x in varBind ])
                    p_idx = p[(p.rfind(".")+1):(p.find("="))]
                    p_name_idx = p[(p.rfind(".")-1):(p.find(".%s=" % (p_idx)))]
                    p_value = p[(p.find("=")+1):]

                    if p_name_idx == '3':
                        pr[alarmNameIdx[p_name_idx]] = alarmStateIdx[p_value]
                    elif p_name_idx == '6':
                        pr[alarmNameIdx[p_name_idx]] = self.hexTimestampToDate(p_value)
                    else:
                        pr[alarmNameIdx[p_name_idx]] = p_value
                Table.append(pr)

        if len(Table) >> 0:
            return { 'status': 0, 'statusText': 'Ok', 'data': Table }
        else:
            return { 'status': -1, 'statusText': 'Empty', 'data': [] }

    def get_AE4EncoderTable(self):
        Table = []
        encoderNameIdx = {'10':'Instance', '11':'Name', '12':'Source', '13':'State', '14':'OnAir',
                          '20': 'Algorithm', '21': 'AudioMode', '22': 'SamplingFrequency', '23': 'DataRate',
                          '30': 'PadRate', '31': 'UsedPadServer',
                          '40':'AudioLevelLeft', '41':'AudioLevelRight'}
        encoderSourceIdx = {'1': 'aesEbuInput1', '2': 'aesEbuInput2', '3': 'aesEbuInput3', '4': 'aesEbuInput4', '5': 'analogue'}
        encoderAlgorithmIdx = {'1':'dabL2', '2':'dabPlusAac'}
        encoderAudioModeIdx = {'9':'mono', '10':'stereo', '11':'parametricStereo', '12':'monoSbr', '13':'stereoSbr'}
        encoderStateIdx = {'1':'disconnect', '2':'running', '3':'noNetwork', '4':'audioError', '5':'inactive', '6':'audioErrorCleared'}
        encoderOnAirIdx = {'1':'true', '2':'false'}
        for errorIndication, \
            errorStatus, \
            errorIndex, \
            varBinds in nextCmd(SnmpEngine(),
                        CommunityData(self.snmp_community, mpModel=self.snmp_version),
                        UdpTransportTarget((self.snmp_host, self.snmp_port), timeout=self.snmp_timeout, retries=self.snmp_retries),
                        ContextData(),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.40.10.20.1.10')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.40.10.20.1.11')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.40.10.20.1.12')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.40.10.20.1.13')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.40.10.20.1.14')),

                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.40.10.20.1.20')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.40.10.20.1.21')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.40.10.20.1.22')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.40.10.20.1.23')),

                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.40.10.20.1.30')),
                        #ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.40.10.20.1.31')),

                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.40.10.20.1.40')),
                        ObjectType(ObjectIdentity('1.3.6.1.4.1.26196.10.3.12.10.40.10.20.1.41')),
                        lookupMib=False,
                        lexicographicMode=False):

            if errorIndication:
                return { 'status': -10, 'statusText': str(errorIndication), 'data': [] }
            elif errorStatus:
                return { 'status': -10, 'statusText': str('%s at %s' % (
                        errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex)-1][0] or '?'
                    )), 'data': [] }
            else:
                pr = {}
                for varBind in varBinds:
                    p = '='.join([ x.prettyPrint() for x in varBind ])
                    p_idx = p[(p.rfind(".")+1):(p.find("="))]
                    p_name_idx = p[(p.rfind(".")-2):(p.find(".%s=" % (p_idx)))]
                    p_value = p[(p.find("=")+1):]

                    if p_name_idx == '12':
                        pr[encoderNameIdx[p_name_idx]] = encoderSourceIdx[p_value]
                    elif p_name_idx == '13':
                        pr[encoderNameIdx[p_name_idx]] = encoderStateIdx[p_value]
                    elif p_name_idx == '14':
                        pr[encoderNameIdx[p_name_idx]] = encoderOnAirIdx[p_value]

                    elif p_name_idx == '20':
                        pr[encoderNameIdx[p_name_idx]] = encoderAlgorithmIdx[p_value]
                    elif p_name_idx == '21':
                        pr[encoderNameIdx[p_name_idx]] = encoderAudioModeIdx[p_value]
                    else:
                        pr[encoderNameIdx[p_name_idx]] = p_value
                Table.append(pr)
        if len(Table) >> 0:
            return { 'status': 0, 'statusText': 'Ok', 'data': Table }
        else:
            return { 'status': -1, 'statusText': 'Empty', 'data': [] }

    def get_oid_value(self, oid):
        for (errorIndication,
            errorStatus,
            errorIndex,
            varBinds) in bulkCmd(SnmpEngine(),
                                CommunityData(self.snmp_community, mpModel=self.snmp_version),
                                UdpTransportTarget((self.snmp_host, self.snmp_port), timeout=self.snmp_timeout, retries=self.snmp_retries),
                                ContextData(),
                                0, 25,
                                ObjectType(ObjectIdentity(oid)),
                                lookupMib=False,
                                lexicographicMode=False):

            if errorIndication:
                return { 'status': -10, 'statusText': str(errorIndication), 'data': [] }
            elif errorStatus:
                return { 'status': -10, 'statusText': str('%s at %s' % (
                        errorStatus.prettyPrint(),
                        errorIndex and varBinds[int(errorIndex)-1][0] or '?'
                    )), 'data': [] }
            else:
                value = [str(v) for (k, v) in varBinds]
                return { 'status': 0, 'statusText': 'Ok', 'data': value[0] }

    def getAE1(self):
        avt = {}

        sysDescr = self.get_oid_value('1.3.6.1.2.1.1.1')
        if sysDescr['status'] == 0:
            avt['sysDescr'] = sysDescr['data']

        Uptime = self.get_oid_value('1.3.6.1.2.1.1.3')
        if Uptime['status'] == 0:
            avt['Uptime'] = Uptime['data']

        sysContact = self.get_oid_value('1.3.6.1.2.1.1.4')
        if sysContact['status'] == 0:
            avt['sysContact'] = sysContact['data']

        sysLocation = self.get_oid_value('1.3.6.1.2.1.1.6')
        if sysLocation['status'] == 0:
            avt['sysLocation'] = sysLocation['data']

        FirmwareVersion = self.get_oid_value('1.3.6.1.4.1.26196.10.3.11.10.30.10.1')
        if FirmwareVersion['status'] == 0:
            avt['FirmwareVersion'] = FirmwareVersion['data']

        MainboardTemperature = self.get_oid_value('1.3.6.1.4.1.26196.10.3.11.10.30.10.10.1')
        if MainboardTemperature['status'] == 0:
            avt['MainboardTemperature'] = MainboardTemperature['data']

        MainboardDsp1Workload = self.get_oid_value('1.3.6.1.4.1.26196.10.3.11.10.30.10.10.2')
        if MainboardDsp1Workload['status'] == 0:
            avt['MainboardDsp1Workload'] = MainboardDsp1Workload['data']

        ClockSourceIdx = {'1':'internal', '3':'recoveredAesEbu', '4':'ntp'}
        ClockSource = self.get_oid_value('1.3.6.1.4.1.26196.10.3.11.10.40.10')
        if ClockSource['status'] == 0:
            try:
                avt['ClockSource'] = ClockSourceIdx[ClockSource['data']]
            except:
                avt['ClockSource'] = 'ID not recognized (%s)' % (ClockSource['data'])

        Alarms = self.get_AE1AlarmsTable()
        if Alarms['status'] == 0:
            avt['Alarms'] = Alarms['data']

        Encoder = self.get_AE1EncoderTable()
        if Encoder['status'] == 0:
            avt['Encoder'] = Encoder['data']

        return avt

    def getAE4(self):
        avt = {}

        sysDescr = self.get_oid_value('1.3.6.1.2.1.1.1')
        if sysDescr['status'] == 0:
            avt['sysDescr'] = sysDescr['data']

        Uptime = self.get_oid_value('1.3.6.1.2.1.1.3')
        if Uptime['status'] == 0:
            avt['Uptime'] = Uptime['data']

        sysContact = self.get_oid_value('1.3.6.1.2.1.1.4')
        if sysContact['status'] == 0:
            avt['sysContact'] = sysContact['data']

        sysLocation = self.get_oid_value('1.3.6.1.2.1.1.6')
        if sysLocation['status'] == 0:
            avt['sysLocation'] = sysLocation['data']

        FirmwareVersion = self.get_oid_value('1.3.6.1.4.1.26196.10.3.12.10.10.10.10')
        if FirmwareVersion['status'] == 0:
            avt['FirmwareVersion'] = FirmwareVersion['data']

        MainboardTemperature = self.get_oid_value('1.3.6.1.4.1.26196.10.3.12.10.10.10.30')
        if MainboardTemperature['status'] == 0:
            avt['MainboardTemperature'] = MainboardTemperature['data']

        MainboardDsp1Workload = self.get_oid_value('1.3.6.1.4.1.26196.10.3.12.10.10.10.40')
        if MainboardDsp1Workload['status'] == 0:
            avt['MainboardDsp1Workload'] = MainboardDsp1Workload['data']

        MainboardDsp2Workload = self.get_oid_value('1.3.6.1.4.1.26196.10.3.12.10.10.10.50')
        if MainboardDsp2Workload['status'] == 0:
            avt['MainboardDsp2Workload'] = MainboardDsp2Workload['data']

        ClockSourceIdx = {'1':'internal', '2': 'external', '3':'recoveredAesEbu', '4':'ntp'}
        ClockSource = self.get_oid_value('1.3.6.1.4.1.26196.10.3.12.10.20.10.10')
        if ClockSource['status'] == 0:
            try:
                avt['ClockSource'] = ClockSourceIdx[ClockSource['data']]
            except:
                avt['ClockSource'] = 'ID not recognized (%s)' % (ClockSource['data'])

        Alarms = self.get_AE4AlarmsTable()
        if Alarms['status'] == 0:
            avt['Alarms'] = Alarms['data']

        Encoder = self.get_AE4EncoderTable()
        if Encoder['status'] == 0:
            avt['Encoder'] = Encoder['data']

        return avt

    def getAll(self):
        avt = {}

        sysObjectID = self.get_oid_value('1.3.6.1.2.1.1.2')
        if sysObjectID['status'] == 0:
            avt['sysObjectID'] = sysObjectID['data']
            if not avt['sysObjectID'].startswith('1.3.6.1.4.1.26196'):
                return { 'status': '-1', 'statusText': 'Target does not appear to be an AVT appliance', 'data': '' }
            else:
                # AVT AE1
                if avt['sysObjectID'] == '1.3.6.1.4.1.26196.10.3.11':
                    avt = self.getAE1()
                # AVT AE4
                elif avt['sysObjectID'] == '1.3.6.1.4.1.26196.10.3.12':
                    avt = self.getAE4()
                    print('AE4')
                else:
                    return { 'status': '-1', 'statusText': 'Target does not appear to be an AVT AE1 or AE4', 'data': '' }
        else:
            return { 'status': '-1', 'statusText': sysObjectID['statusText'], 'data': avt }

        return { 'status': '0', 'statusText': 'Ok', 'data': avt }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='check_avt')
    parser.add_argument('-H','--host', help='SNMP host', required=True)
    parser.add_argument('-p','--port', help='SNMP port (default: 161)', default=161, required=False)
    parser.add_argument('-C','--snmp_community', help='SNMP community (default: public)', default='public', required=False)
    parser.add_argument('-P','--snmp_version', help='SNMP version (default: v2c)', default='v2c', required=False)
    parser.add_argument('-d','--debug', help='display all content', action='store_true', required=False)
    cli_args = parser.parse_args()

    # Get all information
    avt = AVT(snmp_host=cli_args.host, snmp_port=cli_args.port, snmp_community=cli_args.snmp_community, snmp_version=cli_args.snmp_version)
    print ( json.dumps(avt.getAll(), indent=4, separators=(',', ': ')) )
    #print ( json.dumps(avt.get_EncoderTable(), indent=4, separators=(',', ': ')) )
