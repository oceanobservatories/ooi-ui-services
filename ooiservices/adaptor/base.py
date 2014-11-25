#!/usr/bin/env python
'''
ooiservices.adaptor.base

Definitions for the BaseAdaptor 
'''
from flask import make_response
from flask import jsonify

class BaseAdaptor:
    '''
    Base class for adaptor implementations
    '''
    def response_HTTP204(self):
        return make_response('', 204)

    def response_HTTP404(self):
        return make_response(jsonify({'error': 'Not Found'} ), 404)

    def response_HTTP500(self):
        return make_response(jsonify({'error': 'internal server error'} ), 500)
