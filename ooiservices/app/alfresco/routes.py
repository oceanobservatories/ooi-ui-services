#!/usr/bin/env python
'''

'''
__author__ = 'M@Campbell'

from flask import url_for, request, current_app, jsonify, make_response
import os
import json
from cmislib.model import CmisClient

from ooiservices.app.main.authentication import auth
from ooiservices.app.alfresco import alfresco as api
# utilities from alfresco bp
from ooiservices.app.alfresco.utils import make_alfresco_conn, \
    make_alfresco_ticket, make_alfresco_query, make_alfresco_download_link


@api.route('/', methods=['GET'])
@auth.login_required
def get_alfresco_connection():
    '''
    Inspect the current connection to the cmis client (alfresco)
    '''
    # make the alfresco connection and store the repo obj

    try:
        repo = make_alfresco_conn()
    except Exception as e:
        error_response = {'error': 'Alfresco configuration not set or incorrect',
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
        ticket = make_alfresco_ticket()
    except Exception as e:
        error_response = {'error': 'Alfresco configuration invalid,' + \
            ' cannot create ticket.', 'status_code': 500}
        response = make_response(jsonify(error_response), 500)
        return response, response.status_code

    # massage the response a little . . .
    ticket_num = json.loads(ticket._content)
    ticket = ticket_num['data']['ticket']

    return ticket

@api.route('/documents/<string:query>', methods=['GET'])
@auth.login_required
def get_doc(query):
    '''
    This is a general search query for now, it may take a while to
    get a response!
    '''
    # since we'll need the ticket to access any of these
    # documents, lets send it over with the payload . . .
    ticket = get_alfresco_ticket()

    results = make_alfresco_query(query)

    result_list = []
    for result in results:
        result_dict = {}
        result_dict['name'] = result.name
        result_dict['id'] = result.id
        result_dict['url'] = make_alfresco_download_link(result.id, ticket)
        result_list.append(result_dict)

    return jsonify({'results': result_list})
