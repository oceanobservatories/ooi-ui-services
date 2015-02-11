#!/usr/bin/env python
'''
Redmine endpoints

'''

from flask import jsonify, request, Response, current_app
from ooiservices.app.redmine import redmine as api
from ooiservices.app.main.authentication import auth
from collections import OrderedDict
from redmine import Redmine
import json


# List the fields of interest in a redmine issue
issue_fields = ['id', 'assigned_to', 'author', 'created_on', 'description', 'done_ratio',
                'due_date', 'estimated_hours', 'priority', 'project', 'relations', 'children', 'journal',
                'start_date', 'status', 'subject', 'time_entries', 'tracker', 'updated_on', 'watchers']


def redmine_login():
    key = current_app.config['REDMINE_KEY']
    redmine = Redmine('https://uframe-cm.ooi.rutgers.edu',
                      key=key)
    return redmine


@api.route('/ticket', methods=['POST'])
# @auth.login_required
def create_redmine_ticket():
    '''
    Create new ticket
    '''
    data = request.data

    if not data:
        return Response(response='{"error":"Invalid request"}',
                        status=400,
                        mimetype="application/json")

    dataDict = json.loads(data)
    if 'project' not in dataDict:
        return Response(response='{"error":"Invalid request"}',
                        status=400,
                        mimetype="application/json")

    redmine = redmine_login()
    redmine.issue.create(project_id=dataDict['project'],
                         subject=dataDict['subject'])
    # return request.args.get('project', '')
    return data, 201


@api.route('/ticket/', methods=['GET'])
# @auth.login_required
def get_all_redmine_tickets():
    '''
    List all redmine tickets
    '''

    redmine = redmine_login()
    if 'project' not in request.args:
        return Response(response="{error: project not defined}",
                        status=400,
                        mimetype="application/json")

    proj = request.args['project']

    # project = redmine.project.get('ooinet-user-interface-development').refresh()
    project = redmine.project.get(proj).refresh()

    issues = dict(issues=[])
    for issue in project.issues:
        details = OrderedDict()
        for field in issue_fields:
            if hasattr(issue, field):
                details[field] = str(getattr(issue, field))
        issues['issues'].append(details)
    return jsonify(issues)


@api.route('/ticket/id', methods=['POST'])
# @auth.login_required
def update_redmine_ticket():
    '''
    Update a specific ticket
    '''
    data = request.data

    if not data:
        return Response(response='{"error":"Invalid request"}',
                        status=400,
                        mimetype="application/json")

    dataDict = json.loads(data)
    if 'resource_id' not in dataDict:
        return Response(response='{"error":"Invalid request"}',
                        status=400,
                        mimetype="application/json")

    redmine = redmine_login()
    redmine.issue.update(resource_id=dataDict['resource_id'],
                         project_id=dataDict['project_id'],
                         subject=dataDict['subject'],
                         notes=dataDict['notes'])
    return data, 201


@api.route('/ticket/id/', methods=['GET'])
# @auth.login_required
def get_redmine_ticket():
    '''
    Get a specific ticket by id
    '''
    redmine = redmine_login()
    if 'id' not in request.args:
        return Response(response="{error: id not defined}",
                        status=400,
                        mimetype="application/json")

    issue_id = request.args['id']
    issue = redmine.issue.get(issue_id, include='children,journals,watchers')

    details = OrderedDict()
    for field in issue_fields:
        if hasattr(issue, field):
            details[field] = str(getattr(issue, field))

    return jsonify(details)


@api.route('/users/', methods=['GET'])
# @auth.login_required
def get_redmine_users():
    '''
    Get all the users in a project
    '''
    redmine = redmine_login()
    if 'project' not in request.args:
        return Response(response="{error: project not defined}",
                        status=400,
                        mimetype="application/json")

    proj = request.args['project']
    project = redmine.project.get(proj).refresh()

    users = dict(users=[])
    for user in project.memberships:
        users['users'].append(user['user']['name'])

    return jsonify(users)
