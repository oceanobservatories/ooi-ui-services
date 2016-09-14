
"""
Asset Remote Resources routes.

Routes:
[GET]  /remote_resources/<int:asset_id>             # Get all remote resources for asset using asset id.
[GET]  /remote_resources/<string:asset_uid>         # Get all remote resources for asset using asset uid.
[GET]  /remote_resource/<int:resource_id>           # Get remote resource by remoteResourceId.

[POST]  /remote_resource/<string:asset_uid>       # Create a remote resource for an asset
[PUT]   /remote_resource/<string:asset_uid>       # Update a remote resource for an asset

"""
__author__ = 'Edna Donoughe'


from flask import request, jsonify, current_app
from ooiservices.app.main.errors import (bad_request, conflict)
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required
from ooiservices.app.uframe.assets_create_update import (_create_remote_resource, _update_remote_resource,
                                                         _get_remote_resources_by_asset_id,
                                                         _get_remote_resources_by_asset_uid,
                                                         _get_remote_resource_by_resource_id)
import json


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Remote Resources routes.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Get the remote resources for an asset using asset id.
@auth.login_required
@scope_required(u'asset_manager')
@api.route('/remote_resources/<int:asset_id>', methods=['GET'])
def get_remote_resources_by_asset_id(asset_id):
    """ Create a new remote resource for an asset.
    """
    try:
        remote_resources = _get_remote_resources_by_asset_id(asset_id)
        result = jsonify({'remote_resources': remote_resources}), 201
        return result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get the remote resources for an asset using asset uid.
@auth.login_required
@scope_required(u'asset_manager')
@api.route('/remote_resources/<string:asset_uid>', methods=['GET'])
def get_remote_resources_by_asset_uid(asset_uid):
    """ Create a new remote resource for an asset.
    """
    try:
        remote_resources = _get_remote_resources_by_asset_uid(asset_uid)
        result = jsonify({'remote_resources': remote_resources}), 201
        return result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get a remote resource by remote resource id.
@auth.login_required
@scope_required(u'asset_manager')
@api.route('/remote_resource/<int:resource_id>', methods=['GET'])
def get_remote_resource_by_resource_id(resource_id):
    """ Create a new remote resource for an asset.
    """
    try:
        remote_resource = _get_remote_resource_by_resource_id(resource_id)
        return jsonify({'remote_resource': remote_resource})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Create a remote resource for an asset.
@auth.login_required
@scope_required(u'asset_manager')
@api.route('/remote_resource/<string:asset_uid>', methods=['POST'])
def create_remote_resource(asset_uid):
    """ Create a new remote resource for an asset.
    """
    try:
        if not request.data:
            message = 'No data provided to create a remote resource.'
            raise Exception(message)
        data = json.loads(request.data)
        remote_resource = _create_remote_resource(asset_uid, data)
        if not remote_resource:
            message = 'Failed to create remote resource for asset.'
            return conflict(message)
        return jsonify({'remote_resource': remote_resource}), 201
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Update a remote resource by asset uid.
@auth.login_required
@scope_required(u'asset_manager')
@api.route('/remote_resource/<string:asset_uid>', methods=['PUT'])
def update_remote_resource(asset_uid):
    """ Update a remote resource for an asset.
    """
    try:
        if not request.data:
            message = 'No data provided to update a remote resource.'
            raise Exception(message)
        data = json.loads(request.data)
        remote_resource = _update_remote_resource(asset_uid, data)
        if not remote_resource:
            message = 'Unable to get update remote resource for asset uid \'%s\'.' % asset_uid
            return conflict(message)
        return jsonify({'remote_resource': remote_resource})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)