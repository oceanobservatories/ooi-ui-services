#!/usr/bin/env python
'''
ooiservices.controller.instrument

InstrumentController
'''

from ooiservices.controller.base import BaseController
from ooiservices.model.instrument import InstrumentModel

__author__ = "Matt Campbell"

class InstrumentController(BaseController):

    inst = InstrumentModel()

    def __init__(self):
        BaseController.__init__(self)

    def get(self):
        result = self.inst.read()
        return result