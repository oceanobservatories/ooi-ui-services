#!/usr/bin/env python
'''
ooiservices.model.platform_deployment

PlatformDeploymentModel
'''

class PlatformDeployment(SqlModel):
    table_name = 'platform_deployments'
    where_params = ['id', 'array_id']
