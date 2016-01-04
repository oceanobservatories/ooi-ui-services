#!/usr/bin/env python
'''

'''
__author__ = 'M@Campbell'

from flask import jsonify, make_response, request
import json
import cmislib

from ooiservices.app.main.authentication import auth
from ooiservices.app.alfresco import alfresco as api
# utilities from alfresco bp
from ooiservices.app.alfresco.utils import AlfrescoCMIS as ACMIS

@api.route('/', methods=['GET'])
@auth.login_required
def get_alfresco_connection():
    '''
    Inspect the current connection to the cmis client (alfresco)
    '''
    # make the alfresco connection and store the repo obj

    try:
        alf = ACMIS()
        repo = alf.make_alfresco_conn()
    except Exception as e:
        print e
        error_response = \
            {'error': 'Alfresco configuration not set or incorrect',
            'status_code': 500}
        response = make_response(jsonify(error_response), 500)
        return response, response.status_code

    # return the information in the repo object
    info = repo.info
    info_dict = {}
    for k, v in info.items():
        info_dict[k] = v

    return jsonify(info_dict)


@api.route('/', methods=['POST'])
@auth.login_required
def get_alfresco_ticket():
    '''
    POSTing to alfresco root will return the ticket generated from
    the services.
    '''
    try:
        alf = ACMIS()
        ticket = alf.make_alfresco_ticket()
    except Exception as e:
        print e
        error_response = {'error': 'Alfresco configuration invalid,' +
            ' cannot create ticket.', 'status_code': 500}
        response = make_response(jsonify(error_response), 500)
        return response, response.status_code

    # massage the response a little . . .
    ticket_num = json.loads(ticket._content)
    ticket = ticket_num['data']['ticket']

    return ticket


@api.route('/documents', methods=['GET'])
@auth.login_required
def get_doc():
    '''
    This is a general search query for now, it may take a while to
    get a response!
    '''
    query = request.args['search']
    cruise = request.args['cruise']
    array = request.args['array']
    # since we'll need the ticket to access any of these
    # documents, lets send it over with the payload . . .
    ticket = get_alfresco_ticket()
    try:
        alf = ACMIS()

        results,cruise = alf.make_alfresco_cruise_query(array,cruise)

        #results = alf.make_alfresco_query(query)
    except cmislib.exceptions.ObjectNotFoundException as e:
        print e
        error_response = {'error': 'Document not found,' +
            ' cannot create download link.', 'status_code': 404}
        response = make_response(jsonify(error_response), 404)
        return response, response.status_code
    except Exception as e:
        print e
        error_response = {'error': 'Alfresco configuration invalid,' +
            ' cannot create download link.', 'status_code': 500}
        response = make_response(jsonify(error_response), 500)
        return response, response.status_code

    result_list = []
    #add the cruise information
    if cruise is not None:
        result_dict = {}
        result_dict['name'] = cruise.name
        result_dict['id'] = cruise.id
        result_dict['type'] = cruise.type
        result_dict['url'] = alf.make_alfresco_page_link(cruise.id, ticket)
        result_list.append(result_dict)

    #add the results
    for result in results:
        result_dict = {}
        result_dict['name'] = result.name
        result_dict['id'] = result.id
        result_dict['type'] = result.type
        if result_dict['type'] == "cruise" or result_dict['type'] == "asset":
            result_dict['url'] = alf.make_alfresco_download_link(result.id, ticket)
        result_list.append(result_dict)

    return jsonify({'results': result_list})
