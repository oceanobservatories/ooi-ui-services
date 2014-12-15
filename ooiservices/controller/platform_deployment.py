#!/usr/bin/env python
'''
ooiservices.controller.platform_deployment

InstrumentController
'''
from flask import request
from ooiservices.controller.base import ObjectController, ListController
from ooiservices.model.platform_deployment import PlatformDeploymentModel



class PlatformDeploymentController(ObjectController):
    pass

class PlatformDeploymentListController(ListController):
    pass