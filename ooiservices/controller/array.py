#!/usr/bin/env python
'''
ooiservices.controller.array

InstrumentController
'''

from ooiservices.controller.base import ObjectController, ListController
from ooiservices.model.array import ArrayModel

__author__ = "Matt Campbell"

class ArrayObjectController(ObjectController):
    # Instantiate the model during import
    array_model = ArrayModel()

    def get(self, id):
        result = self.array_model.read(id)
        return result

class ArrayListController(ListController):
    # Instantiate the model during import
    array_model = ArrayModel()

    def get(self):
        result = self.array_model.read()
        return result

