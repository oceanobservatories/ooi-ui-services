#!/usr/bin/env python
'''
ooiservices

Initializes the application and necessary application logic
'''
from flask import Flask


app = Flask(__name__)

import ooiservices.routes # initialize the routes

#This line should be moved to a defaults.py in the future
app.config['LOG_FILE'] = True
#Adding logging capabilities.
if app.config.get('LOG_FILE') == True:
    import logging
    logger = logging.getLogger('replicate')
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('logs/ooiservices.txt')
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(process)d - %(name)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler) 
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('Application Process Started')

