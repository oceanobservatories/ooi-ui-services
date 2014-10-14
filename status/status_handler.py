#!/usr/bin/env python

"""
@package status.status_handler
@file status/status_handler.py
@author James D. Case
@brief WSGI service supporting data requests to UFRAME and responses back to the OOI UI Flask App
"""


from gevent.pywsgi import WSGIServer
from os.path import exists
import psycopg2
import simplejson as json
from simplejson.compat import StringIO
import yaml

KEY_SERVICE = "service"

ALIVE = "alive"

CHECK_CONNECTIONS = "checkconnections"

FETCH_STATUS = "fetchstatus"

STATUS_FILTER_PLATFORM = "sfplatform"
STATUS_FILTER_INSTRUMENT = "sfinstrument"


class StatusHandler(object):
    """
    WSGI service that fetches the status of OOI assets from Raytheon UFRAME
    Allows for switching between LIVE and DEMO mode in the settings file
    """

    def __init__(self):
        """

        :return:
        """
        # Open the settings.yml or settings_local.yml file
        settings = None
        try:
            if exists("settings_local.yml"):
                stream = open("settings_local.yml")
                settings = yaml.load(stream)
            elif exists("settings.yml"):
                stream = open("settings.yml")
                settings = yaml.load(stream)
            else:
                raise IOError('No settings.yml or settings_local.yml file exists!')
        except IOError, err:
            print err.message

        self.wsgi_url = settings['status_handler']['wsgi_server']['url']
        self.wsgi_port = settings['status_handler']['wsgi_server']['port']

        self.postgresql_url = settings['status_handler']['postgresql_server']['url']
        self.postgresql_port = settings['status_handler']['postgresql_server']['port']
        self.postgresql_username = settings['status_handler']['postgresql_server']['username']
        self.postgresql_password = settings['status_handler']['postgresql_server']['password']
        self.postgresql_database = settings['status_handler']['postgresql_server']['database']

        self.uframe_url = settings['status_handler']['uframe_server']['url']
        self.uframe_port = settings['status_handler']['uframe_server']['port']
        self.uframe_username = settings['status_handler']['uframe_server']['username']
        self.uframe_password = settings['status_handler']['uframe_server']['password']

        self.service_mode = settings['status_handler']['service_mode']

        self.platform_required_attributes = settings['status_handler']['platform']['required_attributes']

        self.startup()

    def startup(self):
        """
        Start status handler WSGI service...
        """
        try:
            WSGIServer((self.wsgi_url, self.wsgi_port), self.application).serve_forever()
        except IOError, err:
            print "The WSGI server at IP address " + self.wsgi_url + " failed to start on port " + self.wsgi_port + " Error message: " + err.message

    def application(self, env, start_response):
        request = env['PATH_INFO']
        request = request[1:]
        output = ''
        print request
        req = request.split("&")
        param_dict = {}
        if len(req) > 1:
            for param in req:
                params = param.split("=")
                param_dict[params[0]] = params[1]
        else:
            if "=" in request:
                params = request.split("=")
                param_dict[params[0]] = params[1]
            else:
                start_response('200 OK', [('Content-type', 'text/html')])
                return ['<b>' + request + '</br>' + output + '</b>']

        if KEY_SERVICE in param_dict:
            # Simply check if the service is responding (alive)
            # Returns: html
            if param_dict[KEY_SERVICE] == ALIVE:
                start_response('200 OK', [('Content-type', 'text/json')])
                return self.format_json(input_str={'Service Response': 'Alive'})
            # Check the postgresql connections
            # Returns: html
            elif param_dict[KEY_SERVICE] == CHECK_CONNECTIONS:
                #TODO: Add UFRAME connection check
                postgresql_connected = self.check_postgresql_connection()
                if postgresql_connected:
                    start_response('200 OK', [('Content-type', 'text/json')])
                    return self.format_json(input_str={'Database': {'Connection': 'Alive'}})
                else:
                    start_response('400 Bad Request', [('Content-type', 'text/json')])
                    return self.format_json(input_str={'Database': {'Connection': 'Error'}})
            # Fetch the status of OOI assets
            # Returns: JSON
            elif param_dict[KEY_SERVICE] == FETCH_STATUS:
                # Generate a dict of submitted valid filter parameters
                status_filter = self.generate_parameter_filter(param_dict)

                # Get the status based on the filter parameters
                status_output = self.get_status(service_mode=self.service_mode, parameter_filter=status_filter)

                # Check for returned Errors
                if status_output == IOError:
                    start_response('400 Bad Request', [('Content-type', 'text/json')])
                    return self.format_json(input_str={'ERROR': 'service_mode setting is incorrect! Try demo or live instead.'})
                else:
                    # Send the JSON response
                    start_response('200 OK', [('Content-type', 'text/json')])
                    return status_output
            # Specified service is not valid
            # Returns: html
            else:
                start_response('400 Bad Request', [('Content-type', 'text/json')])
                return self.format_json(input_str='ERROR: Specified service parameter is incorrect' + 'Request: ' + request + 'Response: ' + output)

        start_response('200 OK', [('Content-type', 'text/html')])
        return self.format_json(input_str='{Request: ' + request + '}{Response: ' + output + '}')

    def format_json(self, input_str=None):
        """
        Formats an input and returns JSON
        :param input_str:
        :return:
        """
        io = StringIO()
        io.write('{Status:')
        json.dump(self.generate_json_header(), io)
        json.dump(input_str, io)
        io.write('}')
        return io.getvalue()

    def generate_json_header(self):
        """
        This method should build the status response metadata into the header
        :return:
        """
        return {'Status Header': 'Some good metadata here'}

    def get_postgres_connection(self):
        """

        :return:
        """
        try:
            conn = psycopg2.connect(
                database=self.postgresql_database,
                user=self.postgresql_username,
                password=self.postgresql_password,
                host=self.postgresql_url,
                port=self.postgresql_port)
            return conn
        except psycopg2.DatabaseError, err:
            print err
            return err

    def check_postgresql_connection(self):
        """

        :return:
        """
        conn = self.get_postgres_connection()
        print type(conn)
        if type(conn) == psycopg2.OperationalError:
            return None
        else:
            return conn.status

    def generate_parameter_filter(self, param_dict):
        """

        :param param_dict:
        :return:
        """
        # TODO: Auto-generate valid keys from authoritative source
        # TODO: Validate input
        parameter_filter = {}

        if param_dict.has_key(STATUS_FILTER_PLATFORM):
            parameter_filter[STATUS_FILTER_PLATFORM] = param_dict[STATUS_FILTER_PLATFORM]

        if param_dict.has_key(STATUS_FILTER_INSTRUMENT):
            parameter_filter[STATUS_FILTER_INSTRUMENT] = param_dict[STATUS_FILTER_INSTRUMENT]

        return parameter_filter

    def get_status(self, service_mode, parameter_filter=None):
        """

        :param service_mode:
        :param parameter_filter:
        :return: JSON
        """
        if service_mode == 'demo':
            status_dict = {'Status Mode': 'Demo'}
            if parameter_filter is not None:
                status_dict.update(parameter_filter)
            return self.format_json(status_dict)
        elif service_mode == 'live':
            from simplejson.compat import StringIO
            io = StringIO()
            json.dump(['Status response: Live mode: UFRAME Unimplemented'], io)
            return io.getvalue()
        else:
            return IOError
