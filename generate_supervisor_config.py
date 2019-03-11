#!/usr/bin/python
# -*- coding: utf-8 -*-
# -*- encoding: UTF-8 -*-
#
# Form based authentication for CherryPy. Requires the
# Session tool to be loaded.
#

import os
import argparse
from config import Config
import sys
import uuid

if __name__ == '__main__':

    # Get configuration file in argument
    parser = argparse.ArgumentParser(description='ODR Encoder Manager (Tools to generate supervisor config file)')
    parser.add_argument('-c','--config', help='configuration filename',required=True)
    cli_args = parser.parse_args()

    # Check if configuration exist and is readable
    if os.path.isfile(cli_args.config) and os.access(cli_args.config, os.R_OK):
        print("Use configuration file %s" % cli_args.config)
    else:
        print("Configuration file is missing or is not readable - %s" % cli_args.config)
        sys.exit(1)

    # Load configuration
    config = Config(cli_args.config)

    # Check if configuration file need to be updated to support multi encoder
    if isinstance(config.config['odr'], dict):
        print ( 'Convert configuration file to support multi encoder ...' )

        odr = config.config['odr']
        odr['name'] = 'default coder'
        odr['uniq_id'] = str(uuid.uuid4())
        odr['description'] = 'This is the default coder converted from previous version'
        output = { 'global': config.config['global'], 'auth': config.config['auth'], 'odr': [ odr ] }

        # Write configuration file
        try:
            config.write(output)
        except Exception as e:
            print ( 'Error when writing configuration file: ' + str(e) )
            sys.exit(2)

        # Check if configuration file need to be updated with new key
        config.checkConfigurationFile()

        # Check supervisor process and add or remove it if necessary
        config.checkSupervisorProcess()

    # Generate supervisor files
    try:
        config.generateSupervisorFiles(config.config)
    except Exception as e:
        print('Error generating supervisor files: ' + str(e))
