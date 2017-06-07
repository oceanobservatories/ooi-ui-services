#!/usr/bin/env python

from flask import (current_app, jsonify, request)
from ooiservices.app.m2m import m2m as api
from ooiservices.app.m2m.help_tools import (get_help, json_get_help_file)
from ooiservices.app.m2m.common import valid_port_keywords


@api.route('/help', methods=['GET'], defaults={'path': ''})
@api.route('/help/<path:path>', methods=['GET'])
def m2m_handler_help(path):
    """
    Request m2m help. (Also accessible from UI as service route.)
    Returns help as dictionary containing elements 'message' and 'status_code'.
    If json argument provided, the message content is returned as json dictionary, otherwise the
    message content is returned as a pre-processed and formatted string with embedded '\n' values.
    Samples:
        http://localhost:5000/api/m2m/help                      # returns dict 'message' as string
        Server example: http://localhost:4000/m2m/help          # returns dict 'message' as string

        http://localhost:5000/api/m2m/help/<port>
            where port is a valid m2m port
            Example: http://host/api/m2m/help/12576
            Server examples (string versus json):
            -- http://localhost:4000/m2m/help/12576             # returns dict 'message' as string
            {
              "message": "\n==========\nM2M GET Request (Syntax): http://ui-server-address/api/m2m/12576/sensor/inv...',
              "status_code": 200
            }

            -- http://localhost:4000/m2m/help/12576?json=True   # returns dict 'message' as json
                {
                  "message": [
                    {
                      "data_format": null,
                      "data_required": false,
                      "description": "Returns a list of available subsites from the sensor inventory.",
                      "endpoint": "sensor/inv",
                      "method": "GET",
                      "permission_required": false,
                      "root": "sensor/inv",
                      "sample_request": "sensor/inv",
                      "sample_response": [
                        "CE01ISSM",
                        "CE01ISSP",
                        "CE02SHBP",
                        "CP01CNSM",
                        "CP02PMCI",
                        "CP02PMCO",
                        "GA01SUMO",
                        "GI01SUMO",
                        "GP02HYPM",
                        "GP03FLMA",
                        "GS01SUMO",
                        "RS01SBPS",
                        "RS03CCAL",
                        "RS03ECAL",
                        "SSRSPACC"
                      ]
                    },

        Proposed help by port and keyword.
        http://localhost:5000/api/m2m/help/<port>/<keyword>
            where port is a valid m2m port and keyword is a support endpoint identifier for the port.
            Example: http://host/api/m2m/help/12580/annotation
            Example: http://host/api/m2m/help/12580/anno

        Help by keyword, where keywords are predefined list or collection of unique root values.
        http://localhost:5000/api/m2m/help/<keyword>
            where keyword is a valid m2m help keyword
            Sample m2m urls:
                http://host/api/m2m/help'             # General help
                http://host/api/m2m/help/12575'       # Help for port 12575 - Preload (streams, parameters)
                http://host/api/m2m/help/12576'       # Help for port 12576 - Sensor Inventory
                http://host/api/m2m/help/12577'       # Help for port 12577 - Alerts and Alarms
                http://host/api/m2m/help/12587'       # General Asset management help.
                http://host/api/m2m/help/12587/asset' # uframe REST queries for asset objects
                http://host/api/m2m/help/12587/event' # uframe REST queries for event(s)

    Three types of help requests:
        Get help (general m2m help summary). Returns string
        Get help by port. (all help for the port). Returns string (default) or dictionary (?json=True)
        Get help by port and keyword. (proposed)
    """
    json_help = False
    string_valid_ports = []
    try:
        valid_ports = current_app.config['UFRAME_ALLOWED_M2M_PORTS']
        for port in valid_ports:
            string_valid_ports.append(str(port))

        if 'json' in request.args:
            json_help = request.args.get('json', False)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # General m2m help requested (from file).
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not path:
            help_response_data = json_get_help_file(None)
            if not help_response_data:
                help_response_data = 'No help information available at this time.'
            return jsonify({'message': help_response_data, 'status_code': 200}), 200

            '''
            elif path not in string_valid_ports:
                help_response_data = 'Unknown port presented in help request (\'%s\').' % path
                return jsonify({'message': help_response_data, 'status_code': 403}), 403
            '''
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Help requested by valid port (Returns all help for port)
        # Sample: http://localhost:5000/api/m2m/help/12580
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        elif path in string_valid_ports:
            if path == '12587':
                help_response_data = json_get_help_file(path)
            else:
                help_response_data = get_help(int(path), path, request_method=None,
                                          json_result=json_help)
            if not help_response_data:
                help_response_data = 'No help information available at this time.'
            return jsonify({'message': help_response_data, 'status_code': 200}), 200

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Help requested by keyword and port
        # Sample: http://localhost:5000/api/m2m/help/12575
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        else:
            # If no separator, unknown/malformed request.
            if '/' not in path:
                help_response_data = 'Unknown keyword presented in help request (\'%s\').' % path
                return jsonify({'message': help_response_data, 'status_code': 403}), 403

            # Get port and keyword
            port, keyword = path.split('/', 1)
            if port in string_valid_ports:
                if port in string_valid_ports and keyword in valid_port_keywords[int(port)]:
                    help_response_data = get_help(int(port), path, request_method=None,
                                                  json_result=json_help, keyword=keyword)
                    if not help_response_data:
                        help_response_data = 'No help information available at this time.'
                    return jsonify({'message': help_response_data, 'status_code': 200}), 200
            else:
                help_response_data = 'Unknown port presented in help request (\'%s\').' % path
                return jsonify({'message': help_response_data, 'status_code': 403}), 403

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # At this point a valid port and an invalid keyword provided, error.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        help_response_data = 'Invalid keyword presented in help request (\'%s\').' % path
        return jsonify({'message': help_response_data, 'status_code': 403}), 403

    except Exception as err:
        return jsonify({'message': err.message, 'status_code': 500}), 500
