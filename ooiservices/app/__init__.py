#!/usr/bin/env python
'''
ooiservices

Initializes the application and necessary application logic
'''
import os
from flask import Flask, jsonify, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask_environments import Environments
from flask.ext.cache import Cache
from flask_wtf.csrf import CsrfProtect
from sqlalchemy_searchable import make_searchable
from celery import Celery
from flask_redis import Redis
from flask_cors import CORS

basedir = os.path.abspath(os.path.dirname(__file__))

login_manager = LoginManager()
login_manager.session_protection = 'strong'

cache = Cache(config={'CACHE_TYPE': 'simple'})
db = SQLAlchemy()
make_searchable()
csrf = CsrfProtect()
celery = Celery('__main__')
redis_store = Redis()
cors = CORS()

def create_app(config_name):
    app = Flask(__name__)
    env = Environments(app, default_env=config_name)
    if os.path.exists(os.path.join(basedir, 'config_local.yml')):
        env.from_yaml(os.path.join(basedir, 'config_local.yml'))
    else:
        env.from_yaml(os.path.join(basedir, 'config.yml'))
    celery.conf.update(BROKER_URL=app.config['REDIS_URL'],
                CELERY_RESULT_BACKEND=app.config['REDIS_URL'])

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

    #SSL
    if not app.debug and not app.testing and app.config['SSL_DISABLE']:
        from flask.ext.sslify import SSLify
        sslify = SSLify(app)

    # handle proxy server headers
    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)

    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)
    redis_store.init_app(app)
    cors.init_app(app)

    from ooiservices.app.main import api as main_blueprint
    app.register_blueprint(main_blueprint)

    from ooiservices.app.uframe import uframe as uframe_blueprint
    app.register_blueprint(uframe_blueprint, url_prefix='/uframe')

    from ooiservices.app.redmine import redmine as redmine_blueprint
    app.register_blueprint(redmine_blueprint, url_prefix='/redmine')

    from ooiservices.app.alfresco import alfresco as alfresco_blueprint
    app.register_blueprint(alfresco_blueprint, url_prefix='/alfresco')

    from ooiservices.app.m2m import m2m as m2m_blueprint
    app.register_blueprint(m2m_blueprint, url_prefix='/m2m')

    # If debug is enabled add route for site-map
    if app.config['DEBUG']:
        app.add_url_rule('/site-map', 'site_map', site_map)


    return app

def has_no_empty_params(rule):
    '''
    Something to do with empty params?
    '''
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

#route("/site-map")
def site_map():
    '''
    Returns a json structure for the site routes and handlers
    '''
    from flask import current_app as app
    get_links = []
    post_links = []
    put_links = []
    delete_links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint)
            get_links.append((url, rule.endpoint))
        if "PUT" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint)
            put_links.append((url, rule.endpoint))
        if "POST" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint)
            post_links.append((url, rule.endpoint))
        if "DELETE" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint)
            delete_links.append((url, rule.endpoint))
    # links is now a list of url, endpoint tuples
    doc = {
        'get_links' : get_links,
        'put_links' : put_links,
        'post_links' : post_links,
        'delete_links' : delete_links
    }

    return jsonify(**doc)
