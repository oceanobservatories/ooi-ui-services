#!/usr/bin/env python

'''
ooiservices.model.base.py

BaseModel
'''
from flask import make_response
from flask import jsonify

class BaseModel(object):
    '''
    The base model class

    Usage:
    model = BaseModel(id="id", name="name")
    '''
    __cols__ = ['id', 'name']
    id   = None
    name = None

    def __init__(self, *args, **kwargs):
        '''
        Instantiates new base model
        '''

        # A really obscure bug that causes a severe headache down the road
        object.__init__(self)

        for key, val in kwargs.iteritems():
            if key not in self.__cols__:
                # TODO: maybe log an error or something
                continue 
            setattr(self, key, val) 

    def __repr__(self):
        '''
        Standard representation
        '''
        return '<%s:%s>' % (self.__class__.__name__, self.to_doc()) 

    def to_doc(self):
        '''
        Returns python dictionary of the attributes of this instance
        '''
        doc = {}
        for col in self.__cols__:
            doc[col] = getattr(self, col, None) # 
        return doc

    # abstract CRUD methods
    def create(self, obj):
        raise NotImplementedError()

    def read(self, id):
        raise NotImplementedError()

    def update(self, obj):
        raise NotImplementedError()

    def delete(self, id):
        raise NotImplementedError()

    # HTTP error responses
    def response_HTTP204(self):
        return make_response('', 204)

    def response_HTTP404(self):
        return make_response(jsonify({'error': 'Not Found'} ), 404)

    def response_HTTP500(self):
        return make_response(jsonify({'error': 'internal server error'} ), 500)
