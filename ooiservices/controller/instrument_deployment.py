#!/usr/bin/env python
'''
ooiservices.controller.instrument

InstrumentController
'''

from ooiservices.controller.base import ObjectController
from ooiservices.controller.base import ListController
from ooiservices.model.instrument_deployment import InstrumentDeploymentModel
from flask import request


class InstrumentDeploymentController(ObjectController):
    pass

class InstrumentDeploymentListController(ListController):
    pass