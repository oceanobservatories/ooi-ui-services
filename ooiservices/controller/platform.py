#!/usr/bin/env python
'''
ooiservices.controller.platform.py

PlatformController

'''

from ooiservices.controller.base import ObjectController
from ooiservices.controller.base import ListController
from ooiservices.model.platform import PlatformModel
from flask import request

__author__ = "Brian McKenna"

class PlatformObjectController(ObjectController):
    model = None


    def __init__(self):
        ObjectController.__init__(self)

    def get(self, id):
        result = self.platform.read(id)
        if not result:
            return self.response_HTTP204()
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
    model = None


    def get(self):
        args = request.args
        if args:
            result = self.process_args(self.model, args,'array_id')
        else:
            result = self.model.read()
        if not result:
            return self.response_HTTP204()
        return result