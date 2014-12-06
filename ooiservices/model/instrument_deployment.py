#!/usr/bin/env python
'''
ooiservices.model.instrument_deployment

Model for InstrumentDeployment
'''

from ooiservices.model.sqlmodel import SqlModel

class InstrumentDeploymentModel(SqlModel):
    def __init__(self):
        SqlModel.__init__(self, table_name='instrument_deployments', where_param='id')
