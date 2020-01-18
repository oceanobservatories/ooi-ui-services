#!/usr/bin/env python


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

