#!/usr/bin/env python
'''
ooiservices

Initializes the application and necessary application logic
'''

async_mode = None

if async_mode is None:
    try:
        from gevent import monkey
        async_mode = 'gevent'
    except ImportError:
        pass

    if async_mode is None:
        async_mode = 'threading'

    # print('\n ***** async_mode is: ' + async_mode)


import os
from flask import Flask, jsonify, url_for, render_template, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask_environments import Environments
from flask.ext.cache import Cache
from flask.ext.security import current_user, login_required, RoleMixin, Security, \
    SQLAlchemyUserDatastore, UserMixin, utils
from flask_security.utils import encrypt_password
from flask_wtf.csrf import CsrfProtect
from sqlalchemy_searchable import make_searchable
from flask_redis import Redis
from flask_cors import CORS
from flask_socketio import SocketIO


from flask_security.utils import encrypt_password
from flask_environments import Environments
from flask_mail import Mail
from flask.ext import login
from flask.ext.admin.base import MenuLink, Admin, BaseView, expose
from flask.ext.admin.contrib import sqla
from wtforms import PasswordField

from collections import OrderedDict
from datetime import datetime
from redis import Redis as RedisAdmin
from flask.ext.admin.contrib import rediscli

basedir = os.path.abspath(os.path.dirname(__file__))

login_manager = LoginManager()
login_manager.session_protection = 'strong'

cache = Cache()
db = SQLAlchemy()
make_searchable()
csrf = CsrfProtect()
redis_store = Redis()
cors = CORS()
sio = None
thread = None
security = Security()

class UserAdmin(sqla.ModelView):

    # Don't display the password on the list of Users
    column_exclude_list = ('_password',)

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('_password',)

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True

    # Prevent administration of Users unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserAdmin, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField('New Password')
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank...
        if len(model.password2):

            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model._password = utils.encrypt_password(model.password2)


# Customized Role model for SQL-Admin
class RoleAdmin(sqla.ModelView):

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True

    # Prevent administration of Roles unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')

# Create menu links classes with reloaded accessible
class AuthenticatedMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated


class NotAuthenticatedMenuLink(MenuLink):
    def is_accessible(self):
        return not current_user.is_authenticated


class ResetMenuLink(MenuLink):
    def is_accessible(self):
        return not current_user.is_authenticated


class RedisView(rediscli.RedisCli):

    def is_accessible(self):
        return current_user.has_role('redis')





def create_app(config_name):
    app = Flask(__name__)
    env = Environments(app, default_env=config_name)
    if os.path.exists(os.path.join(basedir, 'config_local.yml')):
        env.from_yaml(os.path.join(basedir, 'config_local.yml'))
    else:
        env.from_yaml(os.path.join(basedir, 'config.yml'))

    # Uses REDIS_URL from config.yml to set the connection to the redis-server
    cache.config = {
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': app.config['REDIS_URL']}

    # Adding logging capabilities.
    if app.config['LOGGING'] is True:
        import logging
        logger = logging.getLogger('replicate')
        logger.setLevel(logging.DEBUG)

        log_directory = basedir + app.config['LOG_FILE_PTAH']
        log_filename = log_directory + app.config['LOG_FILE']
        if not os.path.exists(os.path.dirname(log_filename)):
            os.makedirs(os.path.dirname(log_filename))
        file_handler = logging.FileHandler(log_filename, mode='a+')

        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(process)d - %(name)s - ' +
            '%(module)s:%(lineno)d - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
        # app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.DEBUG)
        app.logger.info('Application Process Started')

    # SSL
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
    global sio
    sio = SocketIO(app, async_mode=async_mode)
    # sio.emit('my result', {'data': 'initializing in __init__'}, broadcast=True, namespace='/test')

    # Flask-Security Init
    from ooiservices.app.models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    # security = Security(app, user_datastore)
    security.init_app(app, datastore=user_datastore, register_blueprint=False)

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


    # @app.route('/')
    # @login_required
    # def index():
    #     return redirect('admin')
    #
    # @app.route('/login')
    # def login_view():
    #     return redirect(url_for('security.login'))
    #
    # @app.route('/logout/')
    # def logout_view():
    #     login.logout_user()
    #     # return redirect(url_for('security.logout'))
    #
    # @app.route('/reset')
    # def reset_password():
    #     login.logout_user()
    #     return render_template('index.html')

    admin = Admin(app, name='OOI User Admin')

    # Add Flask-Admin views for Users and Roles
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(RoleAdmin(Role, db.session))

    # Adds redis-cli view
    redis_host = app.config['REDIS_URL'].split('://')[1].split(':')[0]
    redis_port = app.config['REDIS_URL'].rsplit(':', 1)[1]
    r = RedisAdmin(host=redis_host, port=redis_port)
    admin.add_view(RedisView(r, name='Redis CLI'))

    # Add login link
    admin.add_link(NotAuthenticatedMenuLink(name='Login',
                                            endpoint='login_view'))

    # Add logout link
    admin.add_link(AuthenticatedMenuLink(name='Logout',
                                         endpoint='logout_view'))

    # # Add reset password
    # admin.add_link(ResetMenuLink(name='Reset Password',
    #                              endpoint='reset_password'))

    # Add OOI link
    admin.add_link(MenuLink(name='OOI Home Page', category='Links', url='http://ooinet.oceanobservatories.org/'))

    # If debug is enabled add route for site-map
    if app.config['DEBUG']:
        app.add_url_rule('/site-map', 'site_map', site_map)

    return app

from celery import Celery

def create_celery_app(env, app=None):
    app = app or create_app(env)
    celery = Celery('__main__', broker='redis://localhost:6379/0')
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def has_no_empty_params(rule):
    '''
    Something to do with empty params?
    '''
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


# route("/site-map")
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
        'get_links': get_links,
        'put_links': put_links,
        'post_links': post_links,
        'delete_links': delete_links
    }

    return jsonify(**doc)
