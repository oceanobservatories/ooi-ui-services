#!/usr/bin/env python
'''
Redmine endpoints

'''

from flask import (jsonify, request, Response, current_app)
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
    Create new redmine ticket.
    '''
    # Get request data
    data = request.data
    # Check that there is actually data
    if not data:
        return Response(response='{"error":"Invalid request"}', status=400, mimetype="application/json")

    dataDict = json.loads(data)

    # Define required and recommended ticket fields
    required_fields = ['project_id', 'subject']
    dataDict['project_id'] = 'ocean-observatory'
    recommended_fields = ['due_date', 'description', 'priority_id', 'assigned_to_id',
                          'start_date', 'estimated_hours', 'status_id', 'notes',
                          'tracker_id', 'parent_issue_id', 'done_ratio']

    # Check the required fields
    for field in required_fields:
        if field not in dataDict:
            return Response(response='{"error":"Invalid request: ' + field + ' not defined"}',
                            status=400, mimetype="application/json")
    fields = dict()
    for field in required_fields + recommended_fields:
        if field in dataDict:
            fields[field] = dataDict[field]
    try:
        # Log into Redmine
        redmine = redmine_login()

        # Create new issue
        issue = redmine.issue.new()
        # Get the list of ticker Trackers
        trackers = list(redmine.tracker.all())
        # Find the REDMINE_TRACKER (like 'Support') and get the id
        # This make a difference for field validation and proper tracker assignment
        config_redmine_tracker = current_app.config['REDMINE_TRACKER']
        tracker_id = [tracker.id for tracker in trackers if tracker.name == config_redmine_tracker][0]
        issue.tracker_id = tracker_id
        for key, value in fields.iteritems():
            if value is not None:
                setattr(issue, key, value)

        issue.save()

        return data, 201
    except Exception as e:
        current_app.logger.exception('[create_redmine_ticket] %s ' % e.message)
        return Response(response='{"error":"'+e.message+'"}', status=400, mimetype="application/json")


@api.route('/ticket/', methods=['GET'])
@auth.login_required
@scope_required('redmine')
def get_all_redmine_tickets():
    '''
    List all redmine tickets.
    '''
    use_limit = False
    limit = None
    if 'limit' in request.args:
        limit = int(request.args['limit'])
    if limit is not None:
        use_limit = True

    if 'project' not in request.args:
        return Response(response="{error: Invalid request: project_id not defined}",
                        status=400, mimetype="application/json")

    proj = request.args['project']
    redmine = redmine_login()
    project = redmine.project.get(proj).refresh()
    issues = dict(issues=[])
    inx = 0
    for issue in project.issues:
        details = OrderedDict()
        for field in issue_fields:
            if hasattr(issue, field):
                # Note following line will produce UnicodeEncodeError:
                # 'ascii' codec can't encode characters in position 251-252: ordinal not in range(128)
                details[field] = str(getattr(issue, field)) #
        issues['issues'].append(details)
        inx += 1
        if use_limit:
            if inx > limit:
                break
    return jsonify(issues)


@api.route('/ticket/id', methods=['POST'])
@auth.login_required
@scope_required('redmine')
def update_redmine_ticket():
    '''
    Update a specific redmine ticket.
    '''
    data = request.data
    if not data:
        return Response(response='{"error":"Invalid request"}', status=400, mimetype="application/json")

    # Save the request as a dictionary
    dataDict = json.loads(data)

    # Check the required field (resource_id)
    if 'resource_id' not in dataDict:
        return Response(response='{"error":"Invalid request: resource_id not defined"}',
                        status=400, mimetype="application/json")

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

    # Get the issue, update all fields except the issue resource id
    issue = redmine.issue.get(dataDict['resource_id'])
    for key, value in fields.iteritems():
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
        return Response(response="{error: id not defined}", status=400, mimetype="application/json")

    issue_id = request.args['id']
    issue = redmine.issue.get(issue_id, include='children,journals,watchers')

    details = OrderedDict()
    for field in issue_fields:
        if hasattr(issue, field):
            details[field] = str(getattr(issue, field))
    return jsonify(details)


@api.route('/users', methods=['GET'])
@auth.login_required
def get_redmine_users():
    '''
    Get all the users in a project.
    '''
    redmine = redmine_login()

    if 'project' not in request.args:
        return Response(response="{error: project not defined}", status=400, mimetype="application/json")
    all_users = redmine.user.all(offset=1, limit=100)
    users = dict(users=[])
    for n in xrange(len(all_users)):
      user = str(all_users[n])
      user_id = int(all_users[n]['id'])
      users['users'].append([user,user_id])

    return jsonify(users)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# redmine methods for alert and alarm notifications
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def create_redmine_ticket_for_notification(project_id, subject, description, priority, assigned_id):
    """ Create a redmine ticket for an alert notification.
    """
    ticket_id = None

    # Define required and recommended ticket fields
    required_fields = ['project_id', 'subject']
    recommended_fields = ['due_date', 'description', 'priority_id', 'assigned_to_id',
                          'start_date', 'estimated_hours', 'status_id', 'notes',
                          'tracker_id', 'parent_issue_id', 'done_ratio']
    try:
        data = {
                'project_id': project_id,
                'subject':  subject,
                'description': description,
                'priority_id': priority,
                'assigned_to_id': assigned_id,
                'category_id':  1
                }
        fields = dict()
        for field in required_fields + recommended_fields:
            if field in data:
                fields[field] = data[field]

        # Log into Redmine
        redmine = redmine_login()
        issue = redmine.issue.new()
        # Get the list of ticker Trackers
        trackers = list(redmine.tracker.all())
        # Find the REDMINE_TRACKER (like 'Support') and get the id
        # This make a difference for field validation and proper tracker assignment
        config_redmine_tracker = current_app.config['REDMINE_TRACKER']
        tracker_id = [tracker.id for tracker in trackers if tracker.name == config_redmine_tracker][0]
        issue.tracker_id = tracker_id # support
        for key, value in fields.iteritems():
            setattr(issue, key, value)

        if issue.save():
            ticket_id = issue.id

    except Exception as err:
        current_app.logger.exception('[create_redmine_ticket_for_notification] %s ' % err.message)

    finally:
        return ticket_id

def get_redmine_users_by_project(project_id):
    '''
    if project_id is None:
        return []
    all_projects = redmine.project.all()
    projects = []
    for n in xrange(len(all_projects)):
        project = str(all_projects[n])
        projects.append(project)

    if project_id not in projects:
        return []
    '''
    redmine = redmine_login()
    all_users = redmine.user.all(offset=1, limit=100, project_id=project_id)
    users = dict(users=[])
    for n in xrange(len(all_users)):
      user = str(all_users[n])
      user_id = int(all_users[n]['id'])
      users['users'].append([user,user_id])
    return users

def get_redmine_ticket_for_notification(id):
    ''' Get a specific ticket by id for alert notification. Success return ticket_id; if error, return None.
    '''
    details = None
    try:
        redmine = redmine_login()
        issue = redmine.issue.get(id, include='children,journals,watchers')
        details = {}
        for field in issue_fields:
            if hasattr(issue, field):
                details[field] = str(getattr(issue, field))
    except Exception as err:
        current_app.logger.exception('[get_redmine_ticket_for_notification] %s ' % err.message)
    finally:
        return details

# todo test case
def update_redmine_ticket_for_notification(resource_id, project_id, subject, description, priority, assigned_id):
    ''' Update a specific ticket for alert notification. Success return ticket_id, if error return None.
    '''
    ticket_id = None
    try:
        data = {'resource_id': resource_id,
                'project_id': project_id,
                'subject':  subject,
                'description': description,
                'priority': priority,
                'assigned_to': assigned_id,
                'category_id':  1
                }

        update_fields = ['project', 'subject', 'due_date', 'description', 'priority',
                         'assigned_to', 'start_date', 'estimated_hours', 'status_id', 'notes',
                         'tracker_id', 'parent_issue_id', 'done_ratio']

        # Get all the valid update fields from the request
        fields = dict()
        for field in update_fields:
            if field in data:
                fields[field] = data[field]

        # Log into Redmine
        redmine = redmine_login()

        # Get the issue; update all fields except the issue resource id
        issue = redmine.issue.get(data['resource_id'])
        for key, value in fields.iteritems():
            if 'resource_id' != key:
                setattr(issue, key, value)
        if issue.save():
            ticket_id = issue.id

    except Exception as err:
        current_app.logger.exception('[update_redmine_ticket_for_notification] %s ' % err.message)
    finally:
        return ticket_id
