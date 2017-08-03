#!/usr/bin/python
#-*- coding: utf8 -*-


import sys
import time
import os
import socket
import argparse

from api import API
from config import Config
from lcd import LcdMatrix

PORT_SERIE = '/dev/ttyACM0' #identification du port série sur lequel le LCD USB est connecté

LCD_COLS = 16 # Taille du LCD 16 caractères x 2 lignes
LCD_ROWS = 2

def wtitle(title, msg):
    lcd.clear_screen()
    lcd.position( 1, 1 )
    lcd.write( title )
    
    if len(msg) <= 16:
        lcd.position( 2, 1 )
        lcd.write( msg )
        time.sleep(2)
    else:
        i=0
        while i != len(msg)-15:
            m = msg[i:i+16]
            lcd.position( 2, 1 )
            lcd.write( m )
            if i == 0:
                time.sleep(2)
            else:
                time.sleep(0.5)
            i=i+1
        time.sleep(1)

if __name__ == '__main__':
    # Get configuration file in argument
    parser = argparse.ArgumentParser(description='ODR Encoder Manager (LCD)')
    parser.add_argument('-c','--config', help='configuration filename',required=True)
    cli_args = parser.parse_args()
    
    # Check if configuration exist and is readable
    if os.path.isfile(cli_args.config) and os.access(cli_args.config, os.R_OK):
        print "Use configuration file %s" % (cli_args.config)
    else:
        print "Configuration file is missing or is not readable - %s" % (cli_args.config)
        sys.exit(1)
        
    # Load configuration
    config = Config(cli_args.config)

    # Load LcdMatrix
    lcd = LcdMatrix( PORT_SERIE )
        
    # Initialiser la taille du LCD (et sauver dans l'EEPROM)
    lcd.set_lcd_size( LCD_COLS, LCD_ROWS )
    lcd.clear_screen()
    
    # Set splash screen
    lcd.set_splashscreen( 'DAB+ Encoder    Starting ...    ' )
    
    # Activer le rétro-éclairage
    lcd.activate_lcd( True )
    
    # Luminosité max
    lcd.brightness( 255 )
    
    #  Background RGB
    lcd.color( 120, 120, 255 ) 
    
    while True:
        # Retreive NETWORK IFACE IP
        try:
            config_ip = os.popen('ip addr show eth0').read().split("inet ")[1].split("/")[0]
        except:
            config_ip = False
            
        try:
            net1_ip = os.popen('ip addr show eth1').read().split("inet ")[1].split("/")[0]
        except:
            net1_ip = False
        
        try:
            net2_ip = os.popen('ip addr show eth2').read().split("inet ")[1].split("/")[0]
        except:
            net2_ip = False
        
        lcd.autoscroll( False )
        # Display hostname and admin ip
        lcd.clear_screen()
        lcd.write( 'DAB+ Encoder')
        time.sleep( 2 )
        if config_ip:
            lcd.clear_screen()
            lcd.write( 'IP iface CONFIG')
            lcd.position( 2, 1 )
            lcd.write( config_ip )
            time.sleep( 4 )
        if net1_ip:
            lcd.clear_screen()
            lcd.write( 'IP iface NET1')
            lcd.position( 2, 1 )
            lcd.write( net1_ip )
            time.sleep( 4 )
        if net2_ip:
            lcd.clear_screen()
            lcd.write( 'IP iface NET2')
            lcd.position( 2, 1 )
            lcd.write( net2_ip )
            time.sleep( 4 )
        
        with open(config.config['odr']['padenc']['dls_fifo_file'], 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                if line.startswith('DL_PLUS='):
                    continue
                if line.startswith('DL_PLUS_TAG='):
                    continue
                dls = line.rstrip()
                
        wtitle('DAB+ Encoder DLS', dls)
        

