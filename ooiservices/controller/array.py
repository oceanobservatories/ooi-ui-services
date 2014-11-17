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

class ArrayController(ObjectController):

    newArray = ArrayModel()

    def __init__(self):
        ObjectController.__init__(self)

    def get(self):
        result = self.newArray.read()
        return result