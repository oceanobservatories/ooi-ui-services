#!/usr/bin/env python
'''
ooiservices.controller.platform.py

PlatformController

'''

from ooiservices.controller.base import ObjectController, ListController
from ooiservices.model.platform import PlatformModel
from flask.ext.restful import Resource
from flask import request

__author__ = "Brian McKenna"

class PlatformObjectController(ObjectController):

    platform = PlatformModel()

    def __init__(self):
        ObjectController.__init__(self)

    def get(self, id):
        result = self.platform.read(id)
        return result

    def put(self, id):
        args = request.args
        params = args.items()
        doc = {}
        if params:
            for item in params:
                doc[item[0]] = item[1]
        doc['id'] = id
        result = self.platform.update(doc)
        return result

    def delete(self, id):
        return self.platform.delete(id)

class PlatformListController(ListController):

    platform = PlatformModel()

    def get(self):
        result = self.platform.read()
        return result
