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
from ooiservices.app.models import PlatformDeployment, User, UserScope, UserScopeLink, DisabledStreams
from datetime import datetime
import sqlalchemy.exc
import codecs

import yaml
if os.path.exists(os.path.join(basedir, '/app/config_local.yml')):
    with open(basedir + '/app/config_local.yml', 'r') as f:
        doc = yaml.load(f)
else:
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
    from ooiservices.app.models import SystemEvent, SystemEventDefinition, UserEventNotification

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
           "Organization": Organization,
           "SystemEvent": SystemEvent,
           "SystemEventDefinition": SystemEventDefinition,
           "UserEventNotification": UserEventNotification}
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


@manager.option('--production', default=False)
@manager.option('-p', '--password', required=True)
@manager.option('-u', '--psqluser', default='postgres')
def deploy(password, production, psqluser):
    from flask.ext.migrate import upgrade
    from ooiservices.app.models import User, UserScope, UserScopeLink, Array, Organization
    from ooiservices.app.models import PlatformDeployment, InstrumentDeployment, Stream, StreamParameterLink
    from sh import psql
    if production:
        app.logger.info('Creating PRODUCTION Database')
        try:
            psql('-c', 'CREATE ROLE postgres LOGIN SUPERUSER')
        except:
            pass
        psql('-c', 'create database ooiuiprod;', '-U', psqluser)
        psql('ooiuiprod', '-c', 'create schema ooiui', '-U', psqluser)
        psql('ooiuiprod', '-c', 'create extension postgis', '-U', psqluser)
    else:
        try:
            psql('-c', 'CREATE ROLE postgres LOGIN SUPERUSER')
        except:
            pass
        #Create the local database
        app.logger.info('Creating DEV and TEST Databases')
        psql('-c', 'create database ooiuidev;', '-U', psqluser)
        psql('ooiuidev', '-c', 'create schema ooiui', '-U', psqluser)
        psql('ooiuidev', '-c', 'create extension postgis', '-U', psqluser)
        #Create the local test database
        psql('-c', 'create database ooiuitest;', '-U', psqluser)
        psql('ooiuitest', '-c', 'create schema ooiui', '-U', psqluser)
        psql('ooiuitest', '-c', 'create extension postgis', '-U', psqluser)

    from sqlalchemy.orm.mapper import configure_mappers
    configure_mappers()
    db.create_all()

    if production:
        app.logger.info('Populating Production Database . . .')
        with open('db/ooiui_schema_data.sql') as f:
            psql('-U', psqluser, 'ooiuiprod', _in=f)
        with open('db/ooiui_params_streams_data.sql') as h:
            psql('-U', psqluser, 'ooiuiprod', _in=h)
        with open('db/ooiui_vocab.sql') as i:
            psql('-U', psqluser, 'ooiuiprod', _in=i)
        app.logger.info('Production Database loaded.')
    else:
        app.logger.info('Populating Dev Database . . .')
        with open('db/ooiui_schema_data.sql') as f:
            psql('-U', psqluser, 'ooiuidev', _in=f)
        with open('db/ooiui_params_streams_data.sql') as h:
            psql('-U', psqluser, 'ooiuidev', _in=h)
        with open('db/ooiui_vocab.sql') as i:
            psql('-U', psqluser, 'ooiuidev', _in=i)
        app.logger.info('Dev Database loaded.')

    # migrate database to latest revision
    #upgrade()
    if not os.getenv('TRAVIS'):
        UserScope.insert_scopes()
        app.logger.info('Insert default user, name: admin')
        User.insert_user(password=password)
        admin = User.query.first()
        admin.scopes.append(UserScope.query.filter_by(scope_name='user_admin').first())
        admin.scopes.append(UserScope.query.filter_by(scope_name='sys_admin').first())
        admin.scopes.append(UserScope.query.filter_by(scope_name='data_manager').first())
        admin.scopes.append(UserScope.query.filter_by(scope_name='redmine').first())
        db.session.add(admin)
        db.session.commit()


@manager.option('-s', '--schema', required=True)
@manager.option('-o', '--schema_owner', required=True)
@manager.option('-u', '--save_users', required=True)
@manager.option('-ds', '--save_disabled_streams', required=False)
@manager.option('-au', '--admin_username', required=False)
@manager.option('-ap', '--admin_password', required=False)
@manager.option('-af', '--first_name', required=False)
@manager.option('-al', '--last_name', required=False)
@manager.option('-ae', '--email', required=False)
@manager.option('-ao', '--org_name', required=False)
def rebuild_schema(schema, schema_owner, save_users, save_disabled_streams, admin_username, admin_password, first_name, last_name, email, org_name):
    """
    Creates the OOI UI Services schema based on models.py
    :usage: python manage.py rebuild_schema --schema ooiui --schema_owner postgres --save_users False --save_disabled_streams True --admin_username admin --admin_password password --first_name Default --last_name Admin --email defaultadmin@ooi.rutgers.edu --org_name Rutgers
    :param schema:
    :param schema_owner:
    :return:
    """
    # Check if schema exists
    timestamp = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())
    sql = "SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{0}'".format(schema)
    sql_result = db.engine.execute(sql).first()
    if sql_result != None:
        # Move current schema to _timestamp
        app.logger.info('Backing up schema container {0} to {0}_{1}'.format(schema, timestamp))
        db.engine.execute('ALTER SCHEMA {0} RENAME TO {0}_{1}'.format(schema, timestamp))

    app.logger.info('Creating schema container: {0}'.format(schema))
    db.engine.execute('CREATE SCHEMA IF NOT EXISTS {0} AUTHORIZATION {1}'.format(schema, schema_owner))

    app.logger.info('Building schema objects')
    db.create_all()

    app.logger.info('Adding base user_scopes')
    UserScope.insert_scopes()
    db.session.commit()

    app.logger.info('Loading default data into database')
    load_data('ooiui_schema_data.sql')
    db.session.commit()

    app.logger.info('Loading params data into database')
    load_data(sql_file='ooiui_params_streams_data.sql')
    db.session.commit()

    app.logger.info('Loading new vocab data into database')
    load_data(sql_file='ooiui_vocab.sql')
    db.session.commit()

    if save_disabled_streams == 'True':
        app.logger.info('Re-populating disabledstreams table from backup schema')
        ds_sql = 'SELECT * FROM {0}_{1}.disabledstreams'.format(schema, timestamp)
        sql_result = db.engine.execute(ds_sql)
        fa = sql_result.fetchall()
        for sresult in fa:
            ds_record = DisabledStreams()
            ds_record.id = sresult.id
            ds_record.ref_des = getattr(sresult, 'ref_des', '')
            ds_record.stream_name = getattr(sresult, 'stream_name', '')
            ds_record.disabled_by = getattr(sresult, 'disabled_by', '')
            ds_record.timestamp = getattr(sresult, 'timestamp', '')
            db.session.add(ds_record)
            db.engine.execute("SELECT nextval('ooiui.disabledstreams_id_seq')")
            db.session.commit()

    if save_users == 'True':
        app.logger.info('Re-populating users from backup schema')
        users_sql = 'SELECT * FROM {0}_{1}.users'.format(schema, timestamp)
        sql_result = db.engine.execute(users_sql)
        fa = sql_result.fetchall()
        for sresult in fa:
            try:
                new_user = User()
                new_user.id = sresult.id
                new_user.user_id = getattr(sresult, 'user_id', '')
                if hasattr(sresult, 'pass_hash'):
                    new_user._password = getattr(sresult, 'pass_hash', '')
                else:
                    new_user._password = getattr(sresult, '_password', '')
                new_user.email = getattr(sresult, 'email', '')
                new_user.user_name = getattr(sresult, 'user_name', '')
                new_user.active = getattr(sresult, 'active', '')
                new_user.confirmed_at = getattr(sresult, 'confirmed_at', '')
                new_user.first_name = getattr(sresult, 'first_name', '')
                new_user.last_name = getattr(sresult, 'last_name', '')
                new_user.phone_primary = getattr(sresult, 'phone_primary', '')
                new_user.phone_alternate = getattr(sresult, 'phone_alternate', '')
                new_user.role = getattr(sresult, 'role', '')
                new_user.email_opt_in = getattr(sresult, 'email_opt_in', '')
                new_user.organization_id = getattr(sresult, 'organization_id', '')
                new_user.other_organization = getattr(sresult, 'other_organization', '')
                new_user.vocation = getattr(sresult, 'vocation', '')
                new_user.country = getattr(sresult, 'country', '')
                new_user.state = getattr(sresult, 'state', '')
                db.session.add(new_user)
                db.engine.execute("SELECT nextval('ooiui.users_id_seq')")
                db.session.commit()
            except sqlalchemy.exc.IntegrityError, exc:
                app.logger.info('Failure: rebuild_schema failed: ')
                reason = exc.message
                app.logger.info('Cause: ' + reason)
                app.logger.info('Restoring to previous version')
                app.logger.info('Restoring schema container {0}_{1} to {0}'.format(schema, timestamp))
                db.engine.execute('ALTER SCHEMA {0} RENAME TO {0}_{1}_failed'.format(schema, timestamp))
                db.engine.execute('ALTER SCHEMA {0}_{1} RENAME TO {0}'.format(schema, timestamp))


        user_scope_link_sql = 'SELECT * FROM {0}_{1}.user_scope_link'.format(schema, timestamp)
        sql_resultc = db.engine.execute(user_scope_link_sql)
        fac = sql_resultc.fetchall()
        for scresult in fac:
            try:
                new_user_scope_link = UserScopeLink()
                new_user_scope_link.id = scresult.id
                new_user_scope_link.user_id = scresult.user_id
                new_user_scope_link.scope_id = scresult.scope_id
                db.session.add(new_user_scope_link)
                db.engine.execute("SELECT nextval('ooiui.user_scope_link_id_seq')")
                db.session.commit()
            except sqlalchemy.exc.IntegrityError, exc:
                app.logger.info('Failure: rebuild_schema failed: ')
                reason = exc.message
                app.logger.info('Cause: ' + reason)
                app.logger.info('Restoring to previous version')
                app.logger.info('Restoring schema container {0}_{1} to {0}'.format(schema, timestamp))
                db.engine.execute('ALTER SCHEMA {0} RENAME TO {0}_{1}_failed'.format(schema, timestamp))
                db.engine.execute('ALTER SCHEMA {0}_{1} RENAME TO {0}'.format(schema, timestamp))

        # db.engine.execute('INSERT INTO {0}.users SELECT * FROM {0}_{1}.users'.format(schema, timestamp))
        # db.engine.execute('INSERT INTO {0}.user_scope_link SELECT * FROM {0}_{1}.user_scope_link'.format(schema, timestamp))

    else:
        app.logger.info('Adding the default admin user')
        if admin_username is None:
            app.logger.info('Admin username set to: admin')
            admin_username = 'admin@ooi.rutgers.edu'
        if admin_password is None:
            app.logger.info('Admin password set to: password')
            admin_password = 'password'
        if first_name is None:
            app.logger.info('Admin first_name set to: Default')
            first_name = 'Default'
        if last_name is None:
            app.logger.info('Admin last_name set to: Admin')
            last_name = 'Admin'
        if email is None:
            app.logger.info('Admin email set to: defaultadmin@ooi.rutgers.edu')
            email = 'admin@ooi.rutgers.edu'
        if org_name is None:
            app.logger.info('Admin org_name set to: Rutgers')
            org_name = 'Rutgers'
        add_admin_user(username=admin_username, password=admin_password, first_name=first_name, last_name=last_name, email=email, org_name=org_name)


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
    app.logger.info('Insert user_name: %s' % username)
    User.insert_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email, org_name=org_name)
    admin = User.query.filter_by(user_name=username).first()
    admin.scopes.append(UserScope.query.filter_by(scope_name='user_admin').first())
    admin.scopes.append(UserScope.query.filter_by(scope_name='sys_admin').first())
    admin.scopes.append(UserScope.query.filter_by(scope_name='data_manager').first())
    admin.scopes.append(UserScope.query.filter_by(scope_name='redmine').first())
    db.session.add(admin)
    db.session.commit()

@manager.command
def load_data(sql_file):
    '''
    Bulk loads the OOI UI data
    :return:
    '''
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
    APP_DB = os.path.join(APP_ROOT, '..', 'db')
    with codecs.open(os.path.join(APP_DB, sql_file), "r", "utf-8") as f:
        try:
            from ooiservices.app.models import __schema__
            db.session.execute("SET search_path = {0}, public, pg_catalog;".format(__schema__))
            db.session.execute(f.read())
            db.session.commit()
            app.logger.info('Success: Bulk data loaded from file: ' + sql_file)
        except sqlalchemy.exc.IntegrityError, exc:
            app.logger.info('Failure: Bulk data NOT loaded from file: ' + sql_file)
            reason = exc.message
            app.logger.info('Cause: ' + reason)


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
        try:
            psql('-c', 'drop database ooiuiprod', '-U', 'postgres')
        except:
            print 'prod db not found'
            pass
        try:
            psql('-c', 'drop database ooiuidev', '-U', 'postgres')
        except:
            print 'dev db not found'
            pass
        try:
            psql('-c', 'drop database ooiuitest', '-U', 'postgres')
        except:
            print 'test db not found'
            pass
        app.logger.info('Databases have been dropped.')

if __name__ == '__main__':
    manager.run()
