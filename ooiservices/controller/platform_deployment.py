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


def initialize_model():
    '''
    Initializes the model for the controllers
    this function is to be called by app
    '''
    PlatformDeploymentController.model = PlatformDeploymentModel()
    PlatformDeploymentListController.model = PlatformDeploymentModel()

