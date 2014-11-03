#!/usr/bin/env python

from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
parser.read('ooiservices/config.ini')

dbName = parser.get('DataSource', 'DBName')