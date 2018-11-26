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

if __name__ == '__main__':

    # Get configuration file in argument
    parser = argparse.ArgumentParser(description='ODR Encoder Manager (Tools to generate supervisor config file)')
    parser.add_argument('-c','--config', help='configuration filename',required=True)
    cli_args = parser.parse_args()

    # Check if configuration exist and is readable
    if os.path.isfile(cli_args.config) and os.access(cli_args.config, os.R_OK):
        print(("Use configuration file %s" % cli_args.config))
    else:
        print(("Configuration file is missing or is not readable - %s" % cli_args.config))
        sys.exit(1)

    # Load configuration
    config = Config(cli_args.config)

    # Generate supervisor files
    try:
        config.generateSupervisorFiles(config.config)
        print('Wrote supervisor config')
    except Exception as e:
        print('Error generating supervisor files: {}'.format(e))
