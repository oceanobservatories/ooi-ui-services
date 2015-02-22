#!/usr/bin/env python
'''
Application manager.  Responsible for starting the service,
performing db migrations, testing.

'''
import os
basedir = os.path.abspath(os.path.dirname(__file__))
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True,include=basedir + '/app/*')
    COV.start()
from ooiservices.app import create_app, db
from flask.ext.script import Manager, Shell, Server, prompt_bool
from flask.ext.migrate import Migrate, MigrateCommand
import flask.ext.whooshalchemy as whooshalchemy
from ooiservices.app.models import PlatformDeployment, User, UserScope
from datetime import datetime

import yaml
with open(basedir + '/app/config.yml', 'r') as f:
    doc = yaml.load(f)
env = doc['ENV_NAME']

app = create_app(env)
manager = Manager(app)
migrate = Migrate(app,db)
app.config['WHOOSH_BASE'] = 'ooiservices/whoosh_index'
whooshalchemy.whoosh_index(app, PlatformDeployment)

##------------------------------------------------------------------
## M@Campbell 02/10/2015
##
## Helper function to build index of models that are loaded manually (from .sql file)
#
#   Usage:
#       From shell:
#       > from ooiservices.manage import rebuild_index
#       > rebuild_index(model_name)
##------------------------------------------------------------------
def rebuild_index(model):
    import whoosh
    import flask_whooshalchemy
    """Rebuild search index of Flask-SQLAlchemy model"""
    app.logger.info("Rebuilding {0} index...".format(model.__name__))
    primary_field = model.pure_whoosh.primary_key_name
    searchables = model.__searchable__
    index_writer = flask_whooshalchemy.whoosh_index(app, model)

    # Fetch all data
    entries = model.query.all()

    entry_count = 0
    with index_writer.writer() as writer:
        for entry in entries:
            index_attrs = {}
            for field in searchables:
                index_attrs[field] = unicode(getattr(entry, field))

            index_attrs[primary_field] = unicode(getattr(entry, primary_field))
            writer.update_document(**index_attrs)
            entry_count += 1

    app.logger.info("Rebuilt {0} {1} search index entries.".format(str(entry_count), model.__name__))

def make_shell_context():
    from ooiservices.app.models import User, UserScope, UserScopeLink, Array
    from ooiservices.app.models import PlatformDeployment, InstrumentDeployment, Stream, StreamParameter, Watch
    from ooiservices.app.models import OperatorEvent
    from ooiservices.app.models import Platformname, Instrumentname, Annotation, Organization

    ctx = {"app": app,
           "db": db,
           "User": User,
           "UserScope": UserScope,
           "UserScopeLink": UserScopeLink,
           "Array": Array,
           "PlatformDeployment": PlatformDeployment,
           "InstrumentDeployment": InstrumentDeployment,
           "Stream": Stream,
           "Watch": Watch,
           "OperatorEvent": OperatorEvent,
           "StreamParameter": StreamParameter,
           "Platformname": Platformname,
           "Instrumentname": Instrumentname,
           "Annotation": Annotation,
           "Organization": Organization}
    return ctx

@manager.command
def runserver():
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=True)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test(coverage=False, testmodule=None):
    """
    Unit testing
    usage:
        python.exe manage.py test
        python.exe manage.py test --coverage
        python.exe manage.py test --coverage --testmodule=test_basics.py
    :param coverage:
    :return:
    """
    import sys

    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    if COV:
        COV.start()

    import unittest
    # Allow user to choose test module to run
    if testmodule == None:
        tests = unittest.TestLoader().discover(start_dir='tests')
    else:
        tests = unittest.TestLoader().discover(start_dir='tests', pattern=testmodule)

    retval = unittest.TextTestRunner(verbosity=2).run(tests)

    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.erase()
    if retval.errors:
        sys.exit(1)
    if retval.failures:
        sys.exit(1)

@manager.option('-bl', '--bulkload', default=False)
@manager.option('-p', '--password', required=True)
def deploy(password, bulkload):
    from flask.ext.migrate import upgrade
    from ooiservices.app.models import User, UserScope, UserScopeLink, Array, Organization
    from ooiservices.app.models import PlatformDeployment, InstrumentDeployment, Stream, StreamParameterLink
    from sh import psql
    #Create the local database
    app.logger.info('Creating DEV and TEST Databases')
    psql('-c', 'create database ooiuidev;', '-U', 'postgres')
    psql('ooiuidev', '-c', 'create schema ooiui')
    psql('ooiuidev', '-c', 'create extension postgis')
    #Create the local test database
    psql('-c', 'create database ooiuitest;', '-U', 'postgres')
    psql('ooiuitest', '-c', 'create schema ooiui')
    psql('ooiuitest', '-c', 'create extension postgis')
    db.create_all()
    if bulkload:
        with open('db/ooiui_schema_data.sql') as f:
            psql('ooiuidev', _in=f)
        app.logger.info('Bulk test data loaded.')

    # migrate database to latest revision
    #upgrade()
    Organization.insert_org()
    UserScope.insert_scopes()
    app.logger.info('Insert default user, name: admin')
    User.insert_user(password=password)
    admin = User.query.first()
    admin.scopes.append(UserScope.query.filter_by(scope_name='user_admin').first())
    db.session.add(admin)
    db.session.commit()

@manager.option('-s', '--schema', required=True)
@manager.option('-o', '--schema_owner', required=True)
def rebuild_schema(schema, schema_owner):
    """
    Creates the OOI UI Services schema based on models.py
    :usage: python manage.py rebuild_schema --schema ooiui --schema_owner postgres --backup_schema True
    :param schema:
    :param schema_owner:
    :return:
    """

    # Check if schema exists
    sql = "SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{0}'".format(schema)
    sql_result = db.engine.execute(sql).first()
    if sql_result != None:
        # Move current schema to _timestamp
        timestamp = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())
        app.logger.info('Backing up schema container {0} to {0}_{1}'.format(schema, timestamp))
        db.engine.execute('ALTER SCHEMA {0} RENAME TO {0}_{1}'.format(schema, timestamp))

    #app.logger.info('Dropping schema container: {0}'.format(schema))
    #db.engine.execute('DROP SCHEMA %s CASCADE' % schema)

    app.logger.info('Creating schema container: {0}'.format(schema))
    db.engine.execute('CREATE SCHEMA IF NOT EXISTS {0} AUTHORIZATION {1}'.format(schema, schema_owner))

    app.logger.info('Building schema objects')
    db.create_all()

    app.logger.info('Adding base user_scopes')
    UserScope.insert_scopes()

@manager.option('-u', '--username', required=True)
@manager.option('-p', '--password', required=True)
@manager.option('-f', '--first_name', required=True)
@manager.option('-l', '--last_name', required=True)
@manager.option('-e', '--email', required=True)
@manager.option('-o', '--org_name', required=True)
def add_admin_user(username, password, first_name, last_name, email, org_name):
    '''
    Creates a 'user_admin' scoped user using the supplied username and password
    :param username:
    :param password:
    :return:
    '''
    app.logger.info('Insert user, name: %s' % username)
    User.insert_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email, org_name=org_name)
    admin = User.query.filter_by(user_name=username).first()
    admin.scopes.append(UserScope.query.filter_by(scope_name='user_admin').first())
    db.session.add(admin)
    db.session.commit()

@manager.command
def load_data():
    '''
    Bulk loads the OOI UI data
    :return:
    '''
    with open('db/ooiui_schema_data.sql') as f:
        try:
            from ooiservices.app.models import __schema__
            db.session.execute("SET search_path = {0}, public, pg_catalog;".format(__schema__))
            db.session.execute(f.read())
            app.logger.info('Bulk test data loaded.')
        except Exception, err:
            app.logger.error('Bulk test data failed: ' + err.message)

@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()

@staticmethod
@manager.command
def destroy():
    from sh import psql
    db_check = str(db.engine)
    if prompt_bool(
        "Are you sure you want to do drop %s" % db_check
    ):
        if (db_check == 'Engine(postgres://postgres:***@localhost/ooiuidev)'):
            psql('-c', 'drop database ooiuidev')
            psql('-c', 'drop database ooiuitest')
            app.logger.info('ooiuidev and ooiuitest databases have been dropped.')
        else:
            print 'Must be working on LOCAL_DEVELOPMENT to destroy db'

if __name__ == '__main__':
    manager.run()
