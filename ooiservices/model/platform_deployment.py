#!/usr/bin/env python
'''
ooiservices.model.platform_deployment

PlatformDeploymentModel
'''
__author__ = 'Matt Campbell'

from ooiservices.model.interface.sqlmodel import SqlModel

class PlatformDeploymentModel(SqlModel):

    def __init__(self):
        SqlModel.__init__(self, table_name='platform_deployments', where_param='array_code')