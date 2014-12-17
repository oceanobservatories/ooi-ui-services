#!/usr/bin/env python
'''
ooiservices.controller.array

InstrumentController
'''

from ooiservices.controller.base import ObjectController, ListController
from ooiservices.model.array import ArrayModel
from flask import request
from flask.ext.restful import Resource

__author__ = "Matt Campbell"

class ArrayObjectController(ObjectController):

    newArray = ArrayModel()

    def __init__(self):
        ObjectController.__init__(self)

    def get(self, id):
        result = self.newArray.read(id)
        if not result:
            return self.response_HTTP204()
        return result

class ArrayListController(ListController):

    newArray = ArrayModel()

    def get(self):
        if not result:
            return self.response_HTTP204()
        return result