#!/usr/bin/env python
'''

'''
__author__ = 'M@Campbell'

from flask import jsonify, make_response, request, current_app
import json
import cmislib

from ooiservices.app.main.authentication import auth
from ooiservices.app.alfresco import alfresco as api
# utilities from alfresco bp
from ooiservices.app.alfresco.utils import AlfrescoCMIS as ACMIS
from ooiservices.app.main.errors import internal_server_error


@api.route('/', methods=['GET'])
@auth.login_required
def get_alfresco_connection():
    """ Inspect the current connection to the cmis client (alfresco)
    """
    try:
        # Make the alfresco connection and store the repo obj
        alf = ACMIS()
        repo = alf.make_alfresco_conn()
    except Exception as e:
        current_app.logger.info(e)
        message = 'Alfresco configuration not set or incorrect'
        return internal_server_error(message)

    # return the information in the repo object
    info = repo.info
    info_dict = {}
    for k, v in info.items():
        info_dict[k] = v

    return jsonify(info_dict)


@api.route('/', methods=['POST'])
@auth.login_required
def get_alfresco_ticket():
    """ POSTing to alfresco root will return the ticket generated from the services.
    """
    try:
        ticket = _get_alfresco_ticket()
        return ticket
    except Exception as err:
        message = str(err)
        return internal_server_error(message)


def _get_alfresco_ticket():
    """ Return the ticket generated from the alfresco services.
    """
    try:
        try:
            alf = ACMIS()
            ticket = alf.make_alfresco_ticket()
        except Exception as e:
            current_app.logger.info(e)
            message = 'Alfresco configuration invalid, cannot create ticket.'
            raise Exception(message)

        if not ticket:
            message = 'Alfresco ticket invalid, cannot create ticket.'
            raise Exception(message)

        # massage the response a little . . .
        ticket_num = None
        if ticket:
            ticket_num = json.loads(ticket._content)
        if ticket_num:
            if 'data' not in ticket_num:
                message = 'Data not provided in ticket: %s' % jsonify(ticket_num)
                raise Exception(message)
            ticket = ticket_num['data']['ticket']

        return ticket
    except Exception as err:
        message = str(err)
        raise Exception(message)


@api.route('/documents', methods=['GET'])
#@auth.login_required
def get_doc():
    """ Get cruise or asset document or general search. General search may take time to respond.
    """
    query = request.args.get('search', '')
    cruise_name = request.args.get('cruise', '')
    array = request.args.get('array', '')
    # Get the ticket to access any of these documents, and return in payload. (Calling function, not route!)
    ticket = _get_alfresco_ticket()
    cruise = None
    results = []
    try:
        alf = ACMIS()
        # Process cruise_name (cruises display)
        if cruise_name:
            results, cruise = alf.get_cruise_documents(cruise_name)

        # Process array (assets page)
        elif array:
            results, cruise = alf.make_alfresco_cruise_query(array, cruise_name)

        # Process search parameter for query. (Asset page? Reference designator?)
        elif query:
            results = alf.make_alfresco_query(query)

    except cmislib.exceptions.ObjectNotFoundException as e:
        current_app.logger.info(e)
        error_response = {'error': 'Document not found, cannot create download link.', 'status_code': 404}
        response = make_response(jsonify(error_response), 404)
        return response, response.status_code
    except Exception as e:
        current_app.logger.info(e)
        error_response = {'error': 'Alfresco configuration invalid, cannot create download link.', 'status_code': 500}
        response = make_response(jsonify(error_response), 500)
        return response, response.status_code

    result_list = []
    # Add the cruise information
    if cruise is not None:
        result_dict = {}
        result_dict['name'] = cruise.name
        result_dict['id'] = cruise.id
        result_dict['type'] = cruise.type
        result_dict['url'] = alf.make_alfresco_page_link(cruise.id, ticket)
        result_list.append(result_dict)

    # Add the results
    for result in results:
        result_dict = {}
        result_dict['name'] = result.name
        result_dict['id'] = result.id
        result_dict['type'] = result.type
        if result_dict['type'] == "cruise" or result_dict['type'] == "asset":
            result_dict['url'] = alf.make_alfresco_download_link(result.id, ticket)
        result_list.append(result_dict)

    return jsonify({'results': result_list})
