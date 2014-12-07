#!/usr/bin/env python
'''
ooiservices.model.platform_deployment

PlatformDeploymentModel
'''

from ooiservices.model.sqlmodel import SqlModel

class PlatformDeploymentModel(SqlModel):
    table_name = 'platform_deployments'
    where_params = ['id', 'array_id', 'reference_designator']
