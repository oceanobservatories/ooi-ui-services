#!/usr/bin/env python
'''
ooiservices.controller.base.py

BaseController
'''

from flask import request
from flask.ext.restful import Resource

from ooiservices.model.base import BaseModel
from flask import make_response
from flask import jsonify

__author__ = "Brian McKenna"

class BaseController(Resource):

    """
    Implements Flask-RESTful Resource

    Provides two abstract HTTP routes:
        ObjectController implements methods GET/PUT/DELETE (requires id of object)
        ListController implements methods GET/POST (accepts filters via query_string)

    Resources should be added to Flask app via:
        restful.Api.add_resource(FooListController, '/foos')
        restful.Api.add_resource(FooObjectController, '/foos/<string:id>')
    where:
        /foos accepts GET to return list of all objects and POST to create object(s)
        /foos/<id> acts on specific object and implements GET/PUT/DELETE
    """


    def response_HTTP204(self):
        return make_response('', 204)

    def response_HTTP404(self):
        return make_response(jsonify({'error': 'Not Found'} ), 404)

    def response_HTTP500(self):
        return make_response(jsonify({'error': 'internal server error'} ), 500)

    def process_args(self,model, args, key):
        result = None
        if key in args:
            value = request.args.get(key, '')
            self.model.where_param = key
            result = self.model.read(value)
        return result


class ObjectController(BaseController):
    model = None

    def get(self, id):
        result = self.model.read({'id' : id})
        if not result:
            return self.response_HTTP204()
        return result[0]

    def put(self, id):
        raise NotImplementedError()

    def delete(self, id):
        raise NotImplementedError()

class ListController(BaseController):
    model = None

    def get(self):
        result = self.model.read(request.args)
        return result

    def post(self):
        raise NotImplementedError()

