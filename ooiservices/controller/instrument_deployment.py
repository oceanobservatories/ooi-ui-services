#!/usr/bin/env python
'''
ooiservices.controller.instrument

InstrumentController
'''

from ooiservices.controller.base import ObjectController
from ooiservices.controller.base import ListController
from ooiservices.model.instrument_deployment import InstrumentDeploymentModel
from flask import request


class InstrumentDeploymentObjectController(ObjectController):

    model = InstrumentDeploymentModel()

    def __init__(self):
        ObjectController.__init__(self)

    def get(self,id):
        result = self.model.read(id)
        if not result:
            return self.response_HTTP204()
        return result


class InstrumentDeploymentListController(ListController):

    model = InstrumentDeploymentModel()

    def get(self):
        args = request.args
        if args:
            result = self.process_args(self.model, args,'platform_reference_designator')
        else:
            result = self.model.read()
        if not result:
            return self.response_HTTP204()
        return result
