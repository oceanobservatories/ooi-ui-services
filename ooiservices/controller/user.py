#!/usr/bin/env python
'''
ooiservices.controller.user

UserAdd
UserLogin
'''

from ooiservices.controller.base import ObjectController
from ooiservices.model.user import UserModel
from flask import request
from flask.ext.restful import Resource

__author__ = "Matt Campbell"

class UserAdd(ObjectController):

    model = UserModel()

    def __init__(self):
        ObjectController.__init__(self)

    def put(self, id):
        result = self.model.read(id)
        if not result:
            return self.response_HTTP204()
        return result

    def get(self, id):
        result = self.model.read(id)
        if not result:
            return self.response_HTTP204()
        return result

class UserLogin(ObjectController):

    model = UserModel()

    def __init__(self):
        ObjectController.__init__(self)

    def get(self, id):
        result = self.model.read(id)
        if not result:
            return self.response_HTTP204()
        return result