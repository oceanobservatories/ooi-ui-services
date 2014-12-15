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

    newStream = StreamModel()

    def __init__(self):
        ObjectController.__init__(self)

    def get(self, id):
        result = self.newStream.read(id)
        return result

class StreamListController(ListController):

    newStream = StreamModel()

    def get(self):
        result = self.newStream.read()
        return result