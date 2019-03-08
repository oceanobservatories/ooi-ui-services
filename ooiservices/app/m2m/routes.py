#!/usr/bin/env python

import requests

from flask import Response
from flask import current_app, jsonify
from flask import request
from requests.exceptions import ConnectionError, Timeout
from werkzeug.datastructures import MultiDict
from ooiservices.app.m2m import m2m as api
from ooiservices.app.models import User
from ooiservices.app.m2m.help_tools import (build_url, get_port_path_help, get_help)
from ooiservices.app.m2m.exceptions import BadM2MException
from ooiservices.app.uframe.config import (get_m2m_tmp_directory, get_uframe_timeout_info)
import json
import base64


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

            scopes = user.scopes
            scope_names = []
            for s in scopes:
                scope_names.append(s.scope_name)
            # Build and issue request to uframe server.
            url = build_url(path, request_method="GET", scope_names=scope_names)

            # Get uframe timeout values for requests.
            timeout, timeout_read = get_uframe_timeout_info()

            # Perform GET request.
            if debug: print '\n debug -- GET params: ', params
            if data is None:
                timeout = timeout * 2
                timeout_read = timeout_read * 3
                response = requests.get(url, timeout=(timeout, timeout_read), params=params, stream=True)
            else:
                response = requests.get(url, timeout=(timeout, timeout_read), params=params, stream=True, data=data)
            if debug: print '\n debug-- response.status_code: ', response.status_code
            if response.status_code != 200:
                if response.text:
                    message = json.loads(response.text)
                else:
                    message = 'No response.text content received from uframe.'
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
        message = 'ConnectionError when getting data from uframe.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 500}), 500
    except Timeout:
        message = 'Timeout when getting data from uframe.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 408}), 408
    except Exception as err:
        return jsonify({'message': err.message, 'status_code': 400}), 400


@api.route('/', methods=['POST'], defaults={'path': ''})
@api.route('/<path:path>', methods=['POST'])
def m2m_handler_post(path):
    """ Issue POST request to uframe server.
    """
    debug = False
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
        if not request.data and port != 12591:
            message = 'No request data provided for POST.'
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

            # Build and issue POST request to uframe server.
            url = build_url(path, request_method='POST', scope_names=scope_names)
            if debug: print '\n debug -- m2m POST url: ', url

            # Get uframe timeout values for requests.
            timeout, timeout_read = get_uframe_timeout_info()

            # Get request data, except for calibration ingest.
            if port != 12591:
                request_data = json.loads(request.data)

            # Calibration ingest parameters.
            else:
                request_data = None
                params_ = MultiDict()
                params_['user'] = user.user_name

            # Add username for general ingestion requests.
            if port == 12589:
                request_data[u'username'] = user.user_name

            #- - - - - - - - - - - - - - - - - - - - - - - - -
            # POST processing except for calibration ingestion.
            #- - - - - - - - - - - - - - - - - - - - - - - - -
            if port != 12591:
                response = requests.post(url, timeout=(timeout, timeout_read), params=params, stream=True,
                                     data=json.dumps(request_data),
                                     headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
                if debug: print '\n debug-- m2m routes: response.status_code: ', response.status_code

                # Process unsuccessful POST information.
                if response.status_code != 201:
                    if response.text:
                        message = json.loads(response.text)
                    else:
                        message = 'No response.text content received from uframe.'
                    return jsonify({'message': message, 'status_code': response.status_code}), response.status_code
                else:
                    headers = dict(response.headers)
                    headers = {k: headers[k] for k in headers if k in transfer_header_fields}
                    return Response(response.iter_content(1024), response.status_code, headers)

            #- - - - - - - - - - - - - - - - - - - - - - - - -
            # POST processing for calibration ingest only.
            #- - - - - - - - - - - - - - - - - - - - - - - - -
            else:
                # Get fully qualified path to temporary store directory from configuration file.
                store_path = get_m2m_tmp_directory()
                tmp_file = store_path + 'test_Cal_Info.xlsx'
                if debug: print '\n debug -- stored file: ', tmp_file

                # Write data received to temporary file.
                target = open(tmp_file, 'wb')
                try:
                    target.write(request.data)
                    target.close()
                except Exception as err:
                    message = str(err)
                    if debug: print '\n debug ****** target.write error: ', message
                    raise Exception(message)

                # Read data from newly updated temporary file.
                target = None
                try:
                    target = open(tmp_file, 'rb')
                except Exception as err:
                    message = str(err)
                    if debug: print '\n debug ****** exception on open: ', message
                    raise Exception(message)

                files = {'file': target}
                response = requests.post(url, files=files, timeout=(timeout, timeout_read), params=params_)
                if debug: print '\n debug-- m2m routes: response.status_code: ', response.status_code
                target.close()

                # Process unsuccessful status_code
                if response.status_code != 202:
                    if response.text:
                        message = json.loads(response.text)
                    else:
                        message = 'Status code %d indicates an error occurred during calibration ingest POST' % response.status_code
                    return jsonify({'message': message, 'status_code': response.status_code}), response.status_code

                # Process successful status_code
                else:
                    if response.text:
                        message = json.loads(response.text)
                        return jsonify({'message': message, 'status_code': response.status_code}), response.status_code
                    else:
                        return jsonify({'message': 'Calibration file accepted.', 'status_code': response.status_code}), response.status_code


        else:
            if debug: print '\n debug -- POST - do not have user...'
            message = 'Authentication failed during POST request.'
            current_app.logger.info(message)
            return jsonify({'message': message, 'status_code': 401}), 401
    except BadM2MException as e:
        current_app.logger.info(e.message)
        return jsonify({'message': e.message, 'status_code': 403}), 403
    except ConnectionError:
        message = 'ConnectionError during POST of data to uframe.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 500}), 500
    except Timeout:
        message = 'Timeout during POST of data to uframe.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 408}), 408
    except Exception as e:
        return jsonify({'message': e.message, 'status_code': 400}), 400


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
            if debug: print '\n debug -- (before) request.data: ', request.data
            request_data = json.loads(request.data)
            if port == 12589:
                request_data[u'username'] = user.user_name
                if debug:
                    print '\n debug -- (updated) request_data: ', request_data
            if debug: print '\n debug -- m2m PUT url: ', url

            # Get uframe timeout values for requests.
            timeout, timeout_read = get_uframe_timeout_info()
            response = requests.put(url, timeout=(timeout, timeout_read), params=params, stream=True,
                                    data=json.dumps(request_data),
                                    headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
            if debug: print '\n debug-- response.status_code: ', response.status_code
            if response.status_code != 200:
                if response.text:
                    message = json.loads(response.text)
                else:
                    message = 'No response.text content received from uframe.'
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
        message = 'ConnectionError during PUT data to uframe.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 500}), 500
    except Timeout:
        message = 'Timeout during PUT data to uframe.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 408}), 408
    except Exception as e:
        return jsonify({'message': e.message, 'status_code': 400}), 400


@api.route('/', methods=['DELETE'], defaults={'path': ''})
@api.route('/<path:path>', methods=['DELETE'])
def m2m_handler_delete(path):
    """ Issue DELETE request to uframe server - only supports annotations at this time. (port 12580)
    """
    debug = False
    if debug: print '\n debug -- Entered m2m DELETE...'
    transfer_header_fields = ['Date', 'Content-Type']
    request_method = 'DELETE'
    try:
        # Determine if help request, if so return help information.
        port, updated_path, help_request = get_port_path_help(path)
        if help_request:
            help_response_data = get_help(port, updated_path, request_method)
            if not help_response_data:
                help_response_data = 'No help information available at this time.'
            return jsonify({'message': help_response_data, 'status_code': 200}), 200

        # Check request data - get annotation to be deleted and review/compare source with current user.
        """
        if not request.data:
            message = 'No request data provided on DELETE.'
            current_app.logger.info(message)
            return jsonify({'message': message, 'status_code': 401}), 401
        """
        # http://uframe-3-test.intra.oceanobservatories.org:12580/anno/466

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

            # Build and issue DELETE request to uframe server.
            url = build_url(path, request_method='DELETE', scope_names=scope_names)
            if debug: print '\n debug -- m2m DELETE url: ', url

            # Get uframe timeout values for requests.
            timeout, timeout_read = get_uframe_timeout_info()

            # Issue GET on url, if successful, compare source to params['user'] and params['email']
            if debug:
                print '\n debug -- scope_names: ', scope_names
                print '\n debug -- params[user]: ', params['user']
                print '\n debug -- params[email]: ', params['email']
            try:
                response = requests.get(url, timeout=(timeout, timeout_read))
            except Exception as err:
                message = str(err)
                if debug: print '\n Exception on GET: ', message
                message = 'Failed to GET annotation by id as required to process DELETE request.'
                raise Exception(message)
            if response.status_code == 200:
                check_data = response.json()
                if debug:
                    print '\n debug -- check_data[source]: ', check_data['source']

                # Verify if override required due to source field value.
                if check_data['source'] != params['user']:
                    if 'annotate_admin' not in scope_names:
                        message = 'The user (%s) does not have permission to delete this item.' % params['user']
                        if debug: print '\n debug: message: ', message
                        return jsonify({'message': message, 'status_code': 409}), 409
            else:
                if debug: print '\n debug -- GET status code: ', response.status_code

            # Issue DELETE on url
            response = requests.delete(url, timeout=(timeout, timeout_read),
                                        headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
            if debug: print '\n debug-- response.status_code: ', response.status_code
            if response.status_code != 200:
                if response.text:
                    message = json.loads(response.text)
                else:
                    message = 'No response.text content received from uframe.'
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
        message = 'ConnectionError during DELETE data request to uframe.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 500}), 500
    except Timeout:
        message = 'Timeout during DELETE data request to uframe.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 408}), 408
    except Exception as e:
        return jsonify({'message': e.message, 'status_code': 400}), 400