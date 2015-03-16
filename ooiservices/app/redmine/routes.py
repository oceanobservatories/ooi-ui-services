#!/usr/bin/env python
'''
Redmine endpoints

'''

from flask import jsonify, request, Response, current_app
from ooiservices.app.redmine import redmine as api
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required
from collections import OrderedDict
from redmine import Redmine
import json


# List the fields of interest in a redmine issue
issue_fields = ['id', 'assigned_to', 'author', 'created_on', 'description', 'done_ratio',
                'due_date', 'estimated_hours', 'priority', 'project', 'relations', 'children', 'journal',
                'start_date', 'status', 'subject', 'time_entries', 'tracker', 'updated_on', 'watchers']


def redmine_login():
    key = current_app.config['REDMINE_KEY']
    redmine = Redmine(current_app.config['REDMINE_URL'],
                      key=key, requests={'verify': False})
    return redmine


@api.route('/ticket', methods=['POST'])
@auth.login_required
@scope_required('redmine')
def create_redmine_ticket():
    '''
    Create new ticket
    '''

    # Get request data
    data = request.data
    # Check that there is actually data
    if not data:
        return Response(response='{"error":"Invalid request"}',
                        status=400,
                        mimetype="application/json")

    dataDict = json.loads(data)

    # Define required and recommended ticket fields
    required_fields = ['project_id', 'subject']
    recommended_fields = ['due_date', 'description', 'priority_id', 'assigned_to_id',
                          'start_date', 'estimated_hours', 'status_id', 'notes',
                          'tracker_id', 'parent_issue_id', 'done_ratio']

    # Check the required fields
    for field in required_fields:
        if field not in dataDict:
            return Response(response='{"error":"Invalid request: ' + field + ' not defined"}',
                            status=400,
                            mimetype="application/json")
    fields = dict()
    for field in required_fields + recommended_fields:
        if field in dataDict:
            fields[field] = dataDict[field]

    # Log into Redmine
    redmine = redmine_login()

    # Create new issue
    issue = redmine.issue.new()
    issue.tracker_id = 3 # support
    for key, value in fields.iteritems():
        setattr(issue, key, value)
    issue.save()

    return data, 201


@api.route('/ticket/', methods=['GET'])
@auth.login_required
@scope_required('redmine')
def get_all_redmine_tickets():
    '''
    List all redmine tickets
    ''' 
    redmine = redmine_login()
    if 'project' not in request.args:
        return Response(response="{error: Invalid request: project_id not defined}",
                        status=400,
                        mimetype="application/json")

    proj = request.args['project']

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
@auth.login_required
@scope_required('redmine')
def update_redmine_ticket():
    '''
    Update a specific ticket
    '''
    data = request.data

    if not data:
        return Response(response='{"error":"Invalid request"}',
                        status=400,
                        mimetype="application/json")

    # Save the request as a dictionary
    dataDict = json.loads(data)

    # Check the required field (resource_id)
    if 'resource_id' not in dataDict:
        return Response(response='{"error":"Invalid request: resource_id not defined"}',
                        status=400,
                        mimetype="application/json")

    update_fields = ['project_id', 'subject', 'due_date', 'description', 'priority_id',
                     'assigned_to_id', 'start_date', 'estimated_hours', 'status_id', 'notes',
                     'tracker_id', 'parent_issue_id', 'done_ratio']
    # Get all the update fields from the request
    fields = dict()
    for field in update_fields:
        if field in dataDict:
            fields[field] = dataDict[field]

    # Log into Redmine
    redmine = redmine_login()

    # Get the issue
    issue = redmine.issue.get(dataDict['resource_id'])
    for key, value in fields.iteritems():
        # Update all fields except the issue resource id
        if 'resource_id' != key:
            setattr(issue, key, value)
    issue.save()

    return data, 201


@api.route('/ticket/id/', methods=['GET'])
@auth.login_required
@scope_required('redmine')
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


@api.route('/users', methods=['GET'])
@auth.login_required
#@scope_required('redmine') #We don't care if they are 'redmine' scoped to populate the page!
def get_redmine_users():
    '''
    Get all the users in a project
    '''
    redmine = redmine_login()
    if 'project' not in request.args:
        return Response(response="{error: project not defined}",
                        status=400,
                        mimetype="application/json")

    all_users = redmine.user.all(offset=1, limit=100)
    users = dict(users=[],user_id=[])
    
    for n in xrange(len(all_users)):
      user = str(all_users[n])
      user_id = int(all_users[n]['id'])

      users['users'].append([user,user_id])

       

    return jsonify(users)
