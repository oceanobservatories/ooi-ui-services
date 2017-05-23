#!/usr/bin/env python

from flask import (current_app, jsonify, request)
from ooiservices.app.m2m import m2m as api
from ooiservices.app.m2m.help_tools import (get_help, json_get_help_file)


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
            Example: http://localhost:5000/api/m2m/help/12576
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
            Example: http://localhost:5000/api/m2m/help/12580/annotation
            Example: http://localhost:5000/api/m2m/help/12580/anno

        Proposed help by keyword, where keywords are predefined list or collection of unique root values.
        http://localhost:5000/api/m2m/help/<keyword>
            where keyword is a valid m2m help keyword
            Example: http://localhost:5000/api/m2m/help/sensor/inv

    Requires:
        Get help (general m2m help summary). Returns string
        Get help by port. (all help for the port). Returns string or dictionary (?jon=True)

        Get help by keyword. (proposed)
        Get help by port and keyword. (proposed)
    """
    debug = True
    json_help = False
    transfer_header_fields = ['Date', 'Content-Type']
    request_method = 'GET'
    valid_keywords = ['asset', 'streams', 'annotation', 'anno', 'sensor', 'sensor/inv']
    string_valid_ports = []
    try:
        if debug: print '\n debug -- m2m GET HELP entered...'
        valid_ports = current_app.config['UFRAME_ALLOWED_M2M_PORTS']
        for port in valid_ports:
            string_valid_ports.append(str(port))

        if 'json' in request.args:
            if debug: print '\n debug -- Request arguments...'
            json_help = request.args.get('json', False)
        else:
            if debug: print '\n debug -- No request arguments...'
        if debug: print '\n debug -- json_help: ', json_help

        # General m2m help requested.
        if not path:
            if debug: print '\n debug -- General M2M help requested.'
            help_response_data = json_get_help_file(None)
            if debug: print '\n debug -- help_response_data: ', help_response_data
            if not help_response_data:
                help_response_data = 'No help information available at this time.'
            return jsonify({'message': help_response_data, 'status_code': 200}), 200

        # Help requested by valid port (Returns all help for port)
        # 'http://localhost:5000/api/m2m/help/12580'
        elif path in string_valid_ports:
            if debug: print '\n debug -- General help requested for port: %s' % path
            help_response_data = get_help(int(path), path, request_method=None, json_result=json_help)
            if not help_response_data:
                help_response_data = 'No help information available at this time.'
            return jsonify({'message': help_response_data, 'status_code': 200}), 200

        # Help requested by keyword (Proposed)
        elif path in valid_keywords:
            if debug: print '\n debug -- General help requested for keyword: %s' % path

        # Help requested by keyword and port (Proposed)
        else:
            if debug: print '\n debug -- General help requested for unknown keyword: %s' % path

            # If no separator, unknown/malformed request.
            if '/' not in path:
                help_response_data = 'Unknown keyword presented in help request (\'%s\').' % path
                return jsonify({'message': help_response_data, 'status_code': 403}), 403

            # Get port and keyword
            port, keyword = path.split('/', 1)
            if port in string_valid_ports:
                if debug:
                    print '\n debug -- Valid port: ', port
                    print '\n debug -- Get keywords for port(%s)... ' % port
            if keyword in valid_keywords:
                if debug: print '\n debug -- Valid keyword: ', keyword
            if port in string_valid_ports and keyword in valid_keywords:
                if debug: print '\n debug -- Valid port (%s) and keyword: %s' % (port, keyword)

        return jsonify({'message': 'help entered, path: '+ path, 'status_code': 200}), 200
        
        '''
        # Determine if help request, if so return help information.
        port, updated_path, help_request = get_port_path_help(path)
        if help_request:
            if debug: print '\n debug -- Help was requested for (%s) %s...' % (request_method, path)
            help_response_data = get_help(port, updated_path, request_method)
            if debug: print '\n debug -- help_response_data: ', help_response_data
            if not help_response_data:
                help_response_data = 'No help information available at this time.'
            return jsonify({'message': help_response_data, 'status_code': 200}), 200

        if request.data:
            data = request.data
            if debug: print '\n debug -- m2m GET data provided...'
        else:
            data = None
        #current_app.logger.info(path)
        user = User.get_user_from_token(request.authorization['username'], request.authorization['password'])
        if user:
            if debug: print '\n debug -- m2m GET - have user...'
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
            if debug: print '\n debug -- m2m GET - After request has been made...status_code: ', response.status_code
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
    '''
    except Exception as err:
        return jsonify({'message': err.message, 'status_code': 500}), 500
