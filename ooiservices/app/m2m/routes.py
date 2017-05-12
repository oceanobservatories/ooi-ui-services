#!/usr/bin/env python

import requests

from flask import Response
from flask import current_app, jsonify
from flask import request
from requests.exceptions import ConnectionError, Timeout
from werkzeug.datastructures import MultiDict
from ooiservices.app.m2m import m2m as api
from ooiservices.app.models import User


class BadM2MException(Exception):
    pass


class InvalidPortException(BadM2MException):
    def __init__(self, port):
        super(InvalidPortException, self).__init__()
        self.message = 'Requested end point (%s) is not exposed through the machine to machine interface. ' \
                       'Please contact the system admin for more information.' % port


class InvalidPathException(BadM2MException):
    def __init__(self, path):
        super(InvalidPathException, self).__init__()
        self.message = 'Requested URL (%s) is not properly formatted for the machine to machine interface. ' \
                       'Please contact the system admin for more information.' % path


class InvalidMethodException(BadM2MException):
    def __init__(self, port, request_method):
        super(InvalidMethodException, self).__init__()
        self.message = 'Requested end point (%s) is not exposed through the machine to machine interface ' \
                       'for request method \'%s\'. ' \
                       'Please contact the system admin for more information.' % (port, request_method)

class InvalidScopeException(BadM2MException):
    def __init__(self, port, request_method):
        super(InvalidScopeException, self).__init__()
        self.message = 'Requested end point (%s) for request method \'%s\' not permitted without proper permissions. ' \
                       'Please contact the system admin for more information.' % (port, request_method)


def build_url(path, request_method='GET', scope_names=None):
    """
    Given an M2M request path, build the corresponding UFrame URL
    Paths must conform to the following specification:
    <UFRAME PORT>/<UFRAME URL>
    :param path: input path
    :return: URL
    """
    try:
        port, path = path.split('/', 1)
        port = int(port)
    except ValueError:
        raise InvalidPathException(path)

    uframe_host = current_app.config['UFRAME_HOST']
    allowed_ports = current_app.config['UFRAME_ALLOWED_M2M_PORTS']
    post_allowed_ports = current_app.config['UFRAME_ALLOWED_M2M_PORTS_POST']
    put_allowed_ports = current_app.config['UFRAME_ALLOWED_M2M_PORTS_PUT']
    if request_method == 'GET':
        if port not in allowed_ports:
            raise InvalidPortException(port)
    elif request_method == 'POST':
        if port not in post_allowed_ports:
            raise InvalidMethodException(port, request_method)
        if port == 12580:
            if 'annotate' not in scope_names:
                raise InvalidScopeException(port, request_method)
    elif request_method == 'PUT':
        if port not in put_allowed_ports:
            raise InvalidMethodException(port, request_method)
        if port == 12580:
            if 'annotate' not in scope_names:
                raise InvalidScopeException(port, request_method)
    else:
        raise InvalidMethodException(port, request_method)

    base_url = 'http://%s:%d' % (uframe_host, port)
    return '/'.join((base_url, path))


@api.route('/', methods=['GET'], defaults={'path': ''})
@api.route('/<path:path>', methods=['GET'])
def m2m_handler(path):
    """
    :param path:
    :return:
    """
    transfer_header_fields = ['Date', 'Content-Type']
    try:
        if request.data:
            data = request.data
        else:
            data = None
        #current_app.logger.info(path)
        user = User.get_user_from_token(request.authorization['username'], request.authorization['password'])
        if user:
            params = MultiDict(request.args)
            params['user'] = user.user_name
            params['email'] = user.email
            url = build_url(path)
            timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
            timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
            if data is None:
                response = requests.get(url, timeout=(timeout, timeout_read), params=params, stream=True)
            else:
                response = requests.get(url, timeout=(timeout, timeout_read), params=params, stream=True, data=data)
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
        message = 'ConnectionError for get uframe contents.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 500}), 500
    except Timeout:
        message = 'Timeout for get uframe contents.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 500}), 500
    except Exception as err:
        return jsonify({'message': err.message, 'status_code': 500}), 500


@api.route('/', methods=['POST'], defaults={'path': ''})
@api.route('/<path:path>', methods=['POST'])
def m2m_handler_post(path):
    """
    """
    transfer_header_fields = ['Date', 'Content-Type']
    try:
        #current_app.logger.info(path)
        if not request.data:
            message = 'No request data provided for POST.'
            current_app.logger.info(message)
            return jsonify({'message': message, 'status_code': 401}), 401
        user = User.get_user_from_token(request.authorization['username'], request.authorization['password'])
        if user:
            scopes = user.scopes
            scope_names = []
            for s in scopes:
                scope_names.append(s.scope_name)
            params = MultiDict(request.args)
            params['user'] = user.user_name
            params['email'] = user.email
            url = build_url(path, request_method='POST', scope_names=scope_names)
            timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
            timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
            response = requests.post(url, timeout=(timeout, timeout_read), params=params, stream=True,
                                     data=request.data,
                                     headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
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
        message = 'ConnectionError for get uframe contents.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 500}), 500
    except Timeout:
        message = 'Timeout for get uframe contents.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 500}), 500
    except Exception as e:
        return jsonify({'message': e.message, 'status_code': 500}), 500


@api.route('/', methods=['PUT'], defaults={'path': ''})
@api.route('/<path:path>', methods=['PUT'])
def m2m_handler_put(path):
    """
    """
    transfer_header_fields = ['Date', 'Content-Type']
    try:
        #current_app.logger.info(path)
        if not request.data:
            message = 'No request data provided on PUT.'
            current_app.logger.info(message)
            return jsonify({'message': message, 'status_code': 401}), 401
        user = User.get_user_from_token(request.authorization['username'], request.authorization['password'])
        if user:
            scopes = user.scopes
            scope_names = []
            for s in scopes:
                scope_names.append(s.scope_name)
            params = MultiDict(request.args)
            params['user'] = user.user_name
            params['email'] = user.email
            url = build_url(path, request_method='PUT', scope_names=scope_names)
            timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
            timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
            response = requests.put(url, timeout=(timeout, timeout_read), params=params, stream=True,
                                    data=request.data,
                                    headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
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
        message = 'ConnectionError for get uframe contents.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 500}), 500
    except Timeout:
        message = 'Timeout for get uframe contents.'
        current_app.logger.info(message)
        return jsonify({'message': message, 'status_code': 500}), 500
    except Exception as e:
        return jsonify({'message': e.message, 'status_code': 500}), 500
