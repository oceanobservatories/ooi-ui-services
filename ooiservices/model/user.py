#!/usr/bin/env python
'''
ooiservices.mode.user.py

UserModel
'''

__author__ = 'Matt Campbell'

from ooiservices.model.interface.sqlmodel import SqlModel
from ooiservices import app

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class UserModel(SqlModel):
	#figure out how this should be initalized as.
    password_hash = None

    def __init__(self):
        SqlModel.__init__(self, table_name='ooi_users', where_param='id')

    #password methods may be moved out of here, and setup in the ui's user form.
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #TODO: Placeholder, not ready to use this.
    def generate_auth_token(self, id, expiration = 600):
        timed_serial_token = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return timed_serial_token.dumps({ 'id': id })

    #TODO: Placeholder, not ready to use this.
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user