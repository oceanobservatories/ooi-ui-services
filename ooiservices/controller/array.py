#!/usr/bin/env python
'''
ooiservices.controller.array

InstrumentController
'''

from ooiservices.controller.base import ObjectController, ListController
from ooiservices.model.array import ArrayModel

__author__ = "Matt Campbell"

array_model = None

class ArrayObjectController(ObjectController):
    array_model = None

    def get(self, id):
        result = self.array_model.read(id)
        return result

class ArrayListController(ListController):
    array_model = None

    def get(self):
        result = self.array_model.read()
        return result

def initialize_model():
    '''
    Initializes the model for the controllers
    this function is to be called by app
    '''
    ArrayObjectController.array_model = ArrayModel()
    ArrayListController.array_model = ArrayModel()
