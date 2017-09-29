#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:   lizs
# Site:     http://alizs.cc
# Time:     9/28/17 8:25 PM

import os
from logging.config import fileConfig
from ConfigParser import ConfigParser


def get_root_dir():
    """Get the project root directory."""
    return os.path.realpath(__file__).rpartition('libs/common.py')[0]


def get_config(section, option=None, filename=None):
    """Get the config in config file.*"""
    # get the database config
    if section == 'database' and not option:
        return get_db_config()
    if not option:
        return None
    filename = filename if filename else os.path.join(get_root_dir(),
                                                      'conf/config.ini')
    cp = ConfigParser()
    cp.read(filename)
    return cp.get(section=section, option=option)


def get_db_config(filename=None):
    """Get database config."""
    config = {}
    # filename = get_config('path', 'db_config_file')
    filename = filename if filename else os.path.join(get_root_dir(),
                                                      'conf/config.ini')
    cp = ConfigParser()
    cp.read(filename)
    config['host'] = cp.get('database', 'host')
    config['port'] = int(cp.get('database', 'port'))
    config['user'] = cp.get('database', 'user')
    config['password'] = cp.get('database', 'password')
    config['db'] = cp.get('database', 'db')
    return config


def logging_config():
    """logging Configuration."""
    logging_file = os.path.join(get_root_dir(), 'conf/logging.ini')
    fileConfig(logging_file)
