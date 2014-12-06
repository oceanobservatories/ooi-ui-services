#!/usr/bin/env python
'''
ooiservices.controller.stream

StreamObjectController
StreamListController
'''

from ooiservices.controller.base import ObjectController, ListController
from ooiservices.model.stream import StreamModel
from flask import request
from flask.ext.restful import Resource

__author__ = "Matt Campbell"

class StreamObjectController(ObjectController):
    model = None


    def __init__(self):
        ObjectController.__init__(self)

    def get(self, id):
        result = self.model.read(id)
        return result

class StreamListController(ListController):
    model = None

    def get(self):
        result = self.model.read()
        return result

def initialize_model():
    '''
    Initializes the model for the controllers
    this function is to be called by app
    '''
    StreamObjectController.model = StreamModel()
    StreamListController.model = StreamModel()
