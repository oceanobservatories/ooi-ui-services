#!/usr/bin/env python
'''
ooiservices

Initializes the application and necessary application logic
'''
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask_environments import Environments

basedir = os.path.abspath(os.path.dirname(__file__))

login_manager = LoginManager()
login_manager.session_protection = 'strong'

db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    env = Environments(app, default_env=config_name)
    env.from_yaml(os.path.join(basedir, 'config.yml'))

    #Adding logging capabilities.
    if app.config['LOGGING'] == True:
        import logging
        logger = logging.getLogger('replicate')
        logger.setLevel(logging.DEBUG)

        log_directory = basedir + app.config['LOG_FILE_PTAH']
        log_filename = log_directory + app.config['LOG_FILE']
        if not os.path.exists(os.path.dirname(log_filename)):
            os.makedirs(os.path.dirname(log_filename))
        file_handler = logging.FileHandler(log_filename, mode='a+')

        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(process)d - %(name)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
        #app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.DEBUG)
        app.logger.info('Application Process Started')

    db.init_app(app)
    login_manager.init_app(app)

    from ooiservices.app.main import api as main_blueprint
    app.register_blueprint(main_blueprint)

    from ooiservices.app.uframe import uframe as uframe_blueprint
    app.register_blueprint(uframe_blueprint)

    from ooiservices.app.redmine import redmine as redmine_blueprint
    app.register_blueprint(redmine_blueprint)

    return app
