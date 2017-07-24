#!/usr/bin/env python

import requests

from flask import Response
from flask import current_app, jsonify
from flask import request
from requests.exceptions import ConnectionError, Timeout
from werkzeug.datastructures import MultiDict
from ooiservices.app.m2m import m2m as api
from ooiservices.app.models import User
from ooiservices.app.m2m.help_tools import build_url, get_port_path_help, get_help
from ooiservices.app.m2m.exceptions import BadM2MException
import json


@api.route('/', methods=['GET'], defaults={'path': ''})
@api.route('/<path:path>', methods=['GET'])
def m2m_handler(path):
    """ Issue GET request to uframe server.
    """
    debug = False
    if debug: print '\n debug -- Entered m2m GET ...'
    transfer_header_fields = ['Date', 'Content-Type']
    request_method = 'GET'
    try:
        # Determine if help request, if so return help information.
        port, updated_path, help_request = get_port_path_help(path)
        if help_request:
            help_response_data = get_help(port, updated_path, request_method)
            if not help_response_data:
                help_response_data = 'No help information available at this time.'
            return jsonify({'message': help_response_data, 'status_code': 200}), 200

        if request.data:
            data = request.data
        else:
            data = None

        # Verify user information has been provide in request and has permission for the request submitted.
        user = User.get_user_from_token(request.authorization['username'], request.authorization['password'])
        if user:
            params = MultiDict(request.args)
            params['user'] = user.user_name
            params['email'] = user.email

            # Build and issue request to uframe server.
            url = build_url(path)
            timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
            timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
            if data is None:
                response = requests.get(url, timeout=(timeout, timeout_read), params=params, stream=True)
            else:
                response = requests.get(url, timeout=(timeout, timeout_read), params=params, stream=True, data=data)
            if debug: print '\n debug-- response.status_code: ', response.status_code
            if response.status_code != 200:
                tmp = json.loads(response.text)
                message = tmp['message']
                return jsonify({'message': message, 'status_code': response.status_code}), response.status_code
            headers = dict(response.headers)
            headers = {k: headers[k] for k in headers if k in transfer_header_fields}
            return Response(response.iter_content(1024), response.status_code, headers)
        else:
            message = 'Authentication failed.'
            current_app.logger.info(message)
            return jsonify({'message': message, 'status_code': 401}), 401
    except BadM2MException as e:
        current_app.logger.info(e.message)
        return jsonify({'message': e.message, 'status_code': 403}), 403
    except ConnectionError:
        message = 'ConnectionError when getting annotation data from uframe.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 500}), 500
    except Timeout:
        message = 'Timeout when getting annotation data from uframe.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 500}), 500
    except Exception as err:
        return jsonify({'message': err.message, 'status_code': 500}), 500


@api.route('/', methods=['POST'], defaults={'path': ''})
@api.route('/<path:path>', methods=['POST'])
def m2m_handler_post(path):
    """ Issue POST request to uframe server.
    """
    debug = True
    if debug: print '\n debug -- Entered m2m POST...'
    transfer_header_fields = ['Date', 'Content-Type']
    request_method = 'POST'
    try:
        # Determine if help request, if so return help information.
        port, updated_path, help_request = get_port_path_help(path)
        if help_request:
            help_response_data = get_help(port, updated_path, request_method)
            if not help_response_data:
                help_response_data = 'No help information available at this time.'
            return jsonify({'message': help_response_data, 'status_code': 200}), 200

        # Check request data - required for POST
        if not request.data:
            message = 'No request data provided for POST.'
            current_app.logger.info(message)
            return jsonify({'message': message, 'status_code': 401}), 401

        if debug: print '\n debug -- m2m POST request.data: ', request.data

        # Verify user information has been provide in request and has permission for the request submitted.
        if debug: print '\n debug -- POST - before get user...'
        user = User.get_user_from_token(request.authorization['username'], request.authorization['password'])
        if debug: print '\n debug -- POST - after get user...'
        if user:
            if debug: print '\n debug -- POST - have user...'
            scopes = user.scopes
            scope_names = []
            for s in scopes:
                scope_names.append(s.scope_name)
            params = MultiDict(request.args)
            params['user'] = user.user_name
            params['email'] = user.email

            # Build and issue POST request to uframe server.
            url = build_url(path, request_method='POST', scope_names=scope_names)
            if debug: print '\n debug -- m2m POST url: ', url
            timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
            timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
            response = requests.post(url, timeout=(timeout, timeout_read), params=params, stream=True,
                                     data=request.data,
                                     headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
            if debug: print '\n debug-- response.status_code: ', response.status_code
            if response.status_code != 201:
                tmp = json.loads(response.text)
                message = tmp['message']
                return jsonify({'message': message, 'status_code': response.status_code}), response.status_code
            headers = dict(response.headers)
            headers = {k: headers[k] for k in headers if k in transfer_header_fields}
            return Response(response.iter_content(1024), response.status_code, headers)
        else:
            if debug: print '\n debug -- POST - do not have user...'
            message = 'Authentication failed.'
            current_app.logger.info(message)
            return jsonify({'message': message, 'status_code': 401}), 401
    except BadM2MException as e:
        current_app.logger.info(e.message)
        return jsonify({'message': e.message, 'status_code': 403}), 403
    except ConnectionError:
        message = 'ConnectionError during POST annotation data to uframe.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 500}), 500
    except Timeout:
        message = 'Timeout during POST annotation data to uframe.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 500}), 500
    except Exception as e:
        return jsonify({'message': e.message, 'status_code': 500}), 500


@api.route('/', methods=['PUT'], defaults={'path': ''})
@api.route('/<path:path>', methods=['PUT'])
def m2m_handler_put(path):
    """ Issue PUT request to uframe server.
    """
    debug = False
    if debug: print '\n debug -- Entered m2m PUT...'
    transfer_header_fields = ['Date', 'Content-Type']
    request_method = 'PUT'
    try:
        # Determine if help request, if so return help information.
        port, updated_path, help_request = get_port_path_help(path)
        if help_request:
            help_response_data = get_help(port, updated_path, request_method)
            if not help_response_data:
                help_response_data = 'No help information available at this time.'
            return jsonify({'message': help_response_data, 'status_code': 200}), 200

        # Check request data - required for PUT
        if not request.data:
            message = 'No request data provided on PUT.'
            current_app.logger.info(message)
            return jsonify({'message': message, 'status_code': 401}), 401

        # Verify user information has been provide in request and has permission for the request submitted.
        user = User.get_user_from_token(request.authorization['username'], request.authorization['password'])
        if user:
            scopes = user.scopes
            scope_names = []
            for s in scopes:
                scope_names.append(s.scope_name)
            params = MultiDict(request.args)
            params['user'] = user.user_name
            params['email'] = user.email

            # Build and issue PUT request to uframe server.
            url = build_url(path, request_method='PUT', scope_names=scope_names)
            timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
            timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
            response = requests.put(url, timeout=(timeout, timeout_read), params=params, stream=True,
                                    data=request.data,
                                    headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
            if debug: print '\n debug-- response.status_code: ', response.status_code
            if response.status_code != 200:
                tmp = json.loads(response.text)
                message = tmp['message']
                return jsonify({'message': message, 'status_code': response.status_code}), response.status_code
            headers = dict(response.headers)
            headers = {k: headers[k] for k in headers if k in transfer_header_fields}
            return Response(response.iter_content(1024), response.status_code, headers)
        else:
            message = 'Authentication failed.'
            current_app.logger.info(message)
            return jsonify({'message': message, 'status_code': 401}), 401
    except BadM2MException as e:
        current_app.logger.info(e.message)
        return jsonify({'message': e.message, 'status_code': 403}), 403
    except ConnectionError:
        message = 'ConnectionError during PUT annotation data to uframe.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 500}), 500
    except Timeout:
        message = 'Timeout during PUT annotation data to uframe.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 500}), 500
    except Exception as e:
        return jsonify({'message': e.message, 'status_code': 500}), 500