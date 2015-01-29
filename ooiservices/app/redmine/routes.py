#!/usr/bin/env python
'''
Redmine endpoints

'''

from flask import jsonify, request  # , current_app, url_for
from ooiservices.app.redmine import redmine as api
from ooiservices.app import db
from ooiservices.app.main.authentication import auth
from collections import OrderedDict
from redmine import Redmine


def redmine_login():
    redmine = Redmine('https://uframe-cm.ooi.rutgers.edu',
                      key='<your_key>')
    return redmine


@api.route('/ticket', methods=['POST'])
@auth.login_required
def create_redmine_ticket():
    '''
    Create new ticket
    '''
    redmine = redmine_login()
    print request.args()
    # issue = redmine.issue.create(project_id='vacation', subject='Vacation')


@api.route('/ticket', methods=['GET'])
def get_all_redmine_tickets():
    '''
    List all redmine tickets
    '''
    redmine = redmine_login()

    # project = redmine.project.get('ooinet-user-interface-development').refresh()
    project = redmine.project.get('bob-test').refresh()

    # List the fields of interest in a redmine issue
    issue_fields = ['id', 'assigned_to', 'author', 'created_on', 'description', 'done_ratio',
                    'due_date', 'estimated_hours', 'priority', 'project', 'relations',
                    'start_date', 'status', 'subject', 'time_entries', 'tracker', 'updated_on']

    issues = dict(issues=[])
    for issue in project.issues:
        details = OrderedDict()
        for field in issue_fields:
            if hasattr(issue, field):
                details[field] = str(getattr(issue, field))
        # try:
        #     jsonify(details)
        # except:
        #     continue
        issues['issues'].append(details)
    return jsonify(issues)


@api.route('/ticket/id', methods=['PUT'])
@auth.login_required
def update_redmine_ticket():
    '''
    Update a specific ticket
    '''
    pass


@api.route('/ticket/id', methods=['GET'])
@auth.login_required
def get_redmine_ticket():
    '''
    Get a specific ticket by id
    '''
    pass