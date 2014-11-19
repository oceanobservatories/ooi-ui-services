#!/usr/bin/env python
'''
ooiservices.controller.instrument

InstrumentController
'''

from ooiservices.controller.base import ObjectController
from ooiservices.controller.base import ListController
from ooiservices.model.instrument import InstrumentModel
from flask import request

__author__ = "Matt Campbell"

class InstrumentObjectController(ObjectController):

    model = InstrumentModel()

    def __init__(self):
        ObjectController.__init__(self)

    def get(self,id):
        result = self.model.read(id)
        if not result:
            return self.response_HTTP204()
        return result

class InstrumentListController(ListController):

    model = InstrumentModel()

    def get(self):
        args = request.args
        if args:
            result = self.process_args(self.model, args,'platform_id')
        else:
            result = self.model.read()
        if not result:
            return self.response_HTTP204()
        return result
