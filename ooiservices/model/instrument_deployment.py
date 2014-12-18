#!/usr/bin/env python
'''
ooiservices.model.instrument_deployment

Model for InstrumentDeployment
'''
__author__ = 'Matt Campbell'

from ooiservices.model.interface.sqlmodel import SqlModel

class InstrumentDeploymentModel(SqlModel):

    def __init__(self):
        SqlModel.__init__(self, table_name='instrument_deployments', where_param='platform_deployment_code')