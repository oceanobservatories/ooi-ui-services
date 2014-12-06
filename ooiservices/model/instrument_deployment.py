#!/usr/bin/env python
'''
ooiservices.model.instrument_deployment

Model for InstrumentDeployment
'''

from ooiservices.model.sqlmodel import SqlModel

class InstrumentDeploymentModel(SqlModel):
    table_name = 'instrument_deployments'
    where_params = ['id', 'platform_deployment_id']
