#!/usr/bin/env python
'''
ooiservices.controller.instrument

InstrumentController
'''

from ooiservices.controller.base import ObjectController, ListController
from ooiservices.model.instrument import InstrumentModel

__author__ = "Matt Campbell"

class InstrumentObjectController(ObjectController):

    newInstrument = InstrumentModel()

    def __init__(self):
        ObjectController.__init__(self)

    def get(self,id):
        result = self.newInstrument.read(id)
        return result

class InstrumentListController(ListController):

    newInstrument = InstrumentModel()

    def get(self):
        result = self.newInstrument.read()
        return result