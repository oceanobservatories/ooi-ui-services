#!/usr/bin/env python

import requests

from flask import current_app
from flask import request
from requests.exceptions import ConnectionError, Timeout

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


def build_url(path):
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

    if port not in allowed_ports:
        raise InvalidPortException(port)

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
        current_app.logger.info(path)
        if User.api_verify_token(request.authorization['username'], request.authorization['password']):
            url = build_url(path)
            timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
            timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
            response = requests.get(url, timeout=(timeout, timeout_read), params=request.args)
            headers = dict(response.headers)
            headers = {k: headers[k] for k in headers if k in transfer_header_fields}
            return response.text, response.status_code, headers
        else:
            message = 'Authentication failed.'
            current_app.logger.info(message)
            return message, 401
    except BadM2MException as e:
        current_app.logger.info(e.message)
        return e.message, 403
    except ConnectionError:
        message = 'ConnectionError for get uframe contents.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for get uframe contents.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception:
        raise
