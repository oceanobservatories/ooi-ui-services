#!/usr/bin/env python
'''
ooiservices.controller.array

InstrumentController
'''
from flask import request
from ooiservices.controller.base import ObjectController, ListController
from ooiservices.model.array import ArrayModel

__author__ = "Matt Campbell"

array_model = None

class ArrayObjectController(ObjectController):
    array_model = None

    def get(self, id):
        result = self.array_model.read({'id' : id})
        if not result:
            return self.response_HTTP204()
        return result[0]

class ArrayListController(ListController):
    array_model = None

    def get(self):
        result = self.array_model.read(request.args)
        return result