#!/usr/bin/env python
'''
ooiservices.mode.user.py

UserModel
'''

__author__ = 'Matt Campbell'

from ooiservices.model.interface.sqlmodel import SqlModel

from werkzeug.security import generate_password_hash, check_password_hash

class UserModel(SqlModel):
	#figure out this should be initalized as.
    password_hash = None

    def __init__(self):
        SqlModel.__init__(self, table_name='ooi_users', where_param='user_id')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)