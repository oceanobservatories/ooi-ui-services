#!/usr/bin/env python
'''
ooiservices.controller.user

UserAdd
UserLogin
'''
from ooiservices import app
from ooiservices.controller.base import ObjectController
from ooiservices.model.user import UserModel
from flask import request
from flask.ext.restful import Resource
from itsdangerous import URLSafeSerializer as Serializer, BadSignature, BadData

__author__ = "Matt Campbell"

class UserAdd(ObjectController):

    model = UserModel()

    def __init__(self):
        ObjectController.__init__(self)

    def put(self, id):
        #Using a salt to ensure that the id is the id and the password is in the arguments
        jsonSerial_id = Serializer(app.config['SECRET_KEY'], salt='id')
        jsonSerial_args = Serializer(app.config['SECRET_KEY'], salt='args')

        #using custom error handling, will check that the encoding is consistent.
        try:
            #decode the id
            id = jsonSerial_id.loads(id)

            #args is still encoded
            args = request.args
            params = args.items()
            doc = {}
            if params:
                for item in params:
                    #args is decoded here, specifically the password hash.
                    doc[item[0]] = jsonSerial_args.loads(item[1])
            doc['id'] = id
            result = self.model.create(doc)
            return result

        except BadSignature, e:
            print 'nope!'
            encoded_payload = e.payload
            pass

        finally:
            #make sure these get cleared.
            jsonSerial_id = None
            jsonSerial_args = None

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