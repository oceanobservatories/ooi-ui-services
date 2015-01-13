#!/usr/bin/env python
'''
Application manager.  Responsible for starting the service,
performing db migrations, testing.

'''
import os
from config import basedir
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True,include=basedir + '/app/*')
    COV.start()
from app import create_app, db
from app.models import User, UserScope, Array, PlatformDeployment, InstrumentDeployment, \
Stream, StreamParameter
from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('OOI_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app,db)

def make_shell_context():
    return dict(app=app, db=db, User=User, UserScope=UserScope, Array=Array, \
    PlatformDeployment=PlatformDeployment, InstrumentDeployment=InstrumentDeployment, \
    Stream=Stream, StreamParameter=StreamParameter)

manager.add_command("runserver", Server(host="127.0.0.1", port=4000))
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.erase()

@manager.option('--password', help='Initial password')
def deploy(password):
    from flask.ext.migrate import upgrade
    db.create_all()
    # migrate database to latest revision
    upgrade()
    #Add in the default user and scope.
    UserScope.insert_scopes()
    User.insert_user(password)


@manager.command
def destroy():
    db.session.remove()
    db.drop_all()


if __name__ == '__main__':
    manager.run()