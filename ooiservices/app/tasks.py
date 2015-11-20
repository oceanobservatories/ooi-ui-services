'''
Celery needs to have it's own Flask application in order to work correctly.

Create the new flask app, and use it to carry out the async tasks.
Other tasks that are added here may also need to initialize any
dependencies that it may need.

We cannot use the same config file for celery, as that would create a
circular import when trying to work with the main apps application
context.  All configuration should be placed here, so it does not
get confused with the main apps configuration.

This file should also maintain any cron tasks that may be needed.

In order to get results, access celery's result backend database using
the task id.

'''

__author__ = 'M@Campbell'

import os
from flask import Flask
from celery import Celery

'''
Create the celery app, and configure it to talk to the redis broker.
Then intialize it.
'''
celery_app = Flask(__name__)

# Celery configuration
celery_app.config['CELERY_BROKER_URL'] = os.environ.get('REDISCLOUD_URL') or \
    'redis://localhost:6379/0'
celery_app.config['CELERY_RESULT_BACKEND'] = os.environ.get('REDISCLOUD_URL') or \
    'redis://localhost:6379/0'

# Initialize Celery
celery = Celery(celery_app.name, broker=celery_app.config['CELERY_BROKER_URL'])
celery.conf.update(celery_app.config)


'''
Define the list of processes to run either on a heartbeat or simply waiting for

'''

'''
#TODO:  Set definitions here that should be run either
        periodically or simply on another process.
'''
