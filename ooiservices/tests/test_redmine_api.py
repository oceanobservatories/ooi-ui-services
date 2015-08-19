#!/usr/bin/env python
'''
Unit testing for the Redmine API

'''

from ooiservices.app import create_app, db
from ooiservices.app.redmine.routes import (redmine_login, get_redmine_users_by_project,
                                            get_redmine_ticket_for_notification, create_redmine_ticket_for_notification,
                                            update_redmine_ticket_for_notification)
from ooiservices.app.models import User, UserScope, Organization
from flask import current_app
import unittest
from unittest import skipIf
import os
import json
from base64 import b64encode
import datetime as dt

'''
These tests verify the functionality of the Redmine api list.

'''

PROJECT = 'ooi-ui-api-testing'

@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class RedmineTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TESTING_CONFIG')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        test_username = 'admin'
        test_password = 'test'
        Organization.insert_org()

        User.insert_user(username=test_username, password=test_password)

        self.client = self.app.test_client(use_cookies=False)

        UserScope.insert_scopes()
        admin = User.query.filter_by(user_name='admin').first()
        scope = UserScope.query.filter_by(scope_name='redmine').first()
        admin.scopes.append(scope)
        db.session.add(admin)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_read_redmine_issue(self):
        headers = self.get_api_headers('admin', 'test')
        rv = self.client.get('redmine/ticket/id/?id=2', headers=headers)
        self.assertEquals(rv.status_code, 200)
        result = json.loads(rv.data)
        self.assertTrue(result is not None)
        self.assertTrue(len(result) > 0)
        self.assertTrue('id' in result)
        self.assertTrue('project' in result)
        self.assertTrue('subject' in result)
        self.assertTrue('description' in result)
        self.assertTrue('status' in result)
        self.assertTrue('priority' in result)

    def test_read_redmine_issues(self):
        headers = self.get_api_headers('admin', 'test')
        project = current_app.config['REDMINE_PROJECT_ID']
        url = 'redmine/ticket/?project=' + project
        url += '&limit=10'
        #rv = self.client.get('redmine/ticket/?project=' + project, headers=headers)
        rv = self.client.get(url, headers=headers)
        self.assertEquals(rv.status_code, 200)
        issues = json.loads(rv.data)
        self.assertTrue(issues is not None)
        self.assertTrue(len(issues) > 0)
        self.assertTrue('issues' in issues)

        # Select single issue to test
        issue = issues['issues'][0]
        self.assertTrue(issue is not None)
        self.assertTrue(len(issue) > 0)

        # Validate some fields present in issue
        self.assertTrue('id' in issue)
        self.assertTrue('project' in issue)
        self.assertTrue('subject' in issue)
        self.assertTrue('description' in issue)
        self.assertTrue('status' in issue)
        self.assertTrue('priority' in issue)

    def test_read_redmine_users(self):
        headers = self.get_api_headers('admin', 'test')
        rv = self.client.get('redmine/users?project=' + PROJECT, headers=headers)
        self.assertEquals(rv.status_code, 200)

    def test_create_redmine_ticket(self):
        headers = self.get_api_headers('admin', 'test')
        tmp = dt.datetime.now() + dt.timedelta(days=2)
        due_date = dt.datetime.strftime(tmp, "%Y-%m-%d")
        project = 'ocean-observatory'
        rv = self.client.post('redmine/ticket',
                              headers=headers,
                              data=json.dumps({'project_id': project,
                                               'subject': 'Redmine API - Test Issue',
                                               'due_date': due_date,
                                               'description': 'Get this work done ASAP',
                                               'priority_id': 1}))
                                               # 'assigned_to_id': 1}))
        self.assertEquals(rv.status_code, 201)

    def test_update_redmine_ticket(self):
        headers = self.get_api_headers('admin', 'test')
        redmine = redmine_login()
        project = redmine.project.get(PROJECT).refresh()
        rv = self.client.post('redmine/ticket/id',
                              headers=headers,
                              data=json.dumps({'resource_id': 2,
                                               'project_id': project.id,
                                               'subject': 'Redmine API - Testing Update',
                                               'notes': 'This is simply a test'}))
        self.assertEquals(rv.status_code, 201)

    def test_get_all_redmine_tickets(self):
        headers = self.get_api_headers('admin', 'test')
        rv = self.client.get('redmine/ticket/', headers=headers)
        self.assertEquals(rv.status_code, 400)

    def test_create_redmine_ticket_empty(self):
        headers = self.get_api_headers('admin', 'test')
        rv = self.client.post('redmine/ticket', headers=headers, data=None)
        self.assertEquals(rv.status_code, 400)

    def test_create_redmine_ticket_missing_required_field(self):
        headers = self.get_api_headers('admin', 'test')
        tmp = dt.datetime.now() + dt.timedelta(days=2)
        due_date = dt.datetime.strftime(tmp, "%Y-%m-%d")
        # Missing required field 'subject'
        rv = self.client.post('redmine/ticket',
                              headers=headers,
                              data=json.dumps({'due_date': due_date,
                                               'description': 'Get this work done ASAP',
                                               'priority_id': 1}))
        self.assertEquals(rv.status_code, 400)

    def test_update_redmine_ticket_empty(self):
        headers = self.get_api_headers('admin', 'test')
        rv = self.client.post('redmine/ticket/id', headers=headers, data=None)
        self.assertEquals(rv.status_code, 400)

    def test_update_redmine_ticket_missing_required_field(self):
        headers = self.get_api_headers('admin', 'test')
        redmine = redmine_login()
        project = redmine.project.get(PROJECT).refresh()
        rv = self.client.post('redmine/ticket/id',
                              headers=headers,
                              data=json.dumps({'project_id': project.id,
                                               'subject': 'Testing Update',
                                               'notes': 'This is simply a test'}))
        self.assertEquals(rv.status_code, 400)

    def test_read_redmine_issue_error_no_id_arg(self):
        headers = self.get_api_headers('admin', 'test')
        rv = self.client.get('redmine/ticket/id/?foo=2290', headers=headers)
        self.assertEquals(rv.status_code, 400)

    def test_read_redmine_users_no_project(self):
        headers = self.get_api_headers('admin', 'test')
        rv = self.client.get('redmine/users?foo=' + PROJECT, headers=headers)
        self.assertEquals(rv.status_code, 400)

    def test_get_redmine_users_by_project(self):

        '''
        project = 'no_such_project'
        result = get_redmine_users_by_project(project)
        self.assertEquals(result, [])

        result = get_redmine_users_by_project(PROJECT)
        self.assertEquals(result, [])

        result = get_redmine_users_by_project(None)
        self.assertEquals(result, [])

        project = 'C2 Testing'
        result = get_redmine_users_by_project(project)
        self.assertTrue(len(result) != 0)
        '''
        project = 'ocean-observatory'
        result = get_redmine_users_by_project(project)
        self.assertTrue(result != [])
        self.assertTrue(len(result) != 0)

    def test_get_redmine_ticket_for_notification(self):

        # Create a redmine ticket and query
        headers = self.get_api_headers('admin', 'test')
        tmp = dt.datetime.now() + dt.timedelta(days=2)
        due_date = dt.datetime.strftime(tmp, "%Y-%m-%d")
        project = 'ocean-observatory'
        subject = 'Redmine API - Test Issue'
        description = 'Get this work done ASAP'
        priority = 1
        assigned_id = 1
        ticket_id = create_redmine_ticket_for_notification(project, subject, description, priority, assigned_id)
        self.assertTrue(ticket_id is not None)
        self.assertTrue(isinstance(ticket_id, int))
        self.assertTrue(ticket_id > 0)

        result = get_redmine_ticket_for_notification(ticket_id)
        self.assertTrue('id' in result)
        self.assertTrue('project' in result)
        self.assertTrue('subject' in result)
        self.assertTrue('description' in result)
        self.assertTrue('status' in result)
        self.assertTrue('assigned_to' in result)
        self.assertTrue('priority' in result)

        # Prepare for redmine priority, status and assigned_ti
        assigned_to = 'Redmine Admin'
        status = 'New'
        redmine_priority = None
        if priority == 1:
            redmine_priority = 'Low'

        # Validate result values returned from redmine
        self.assertTrue(project != result['project'])
        self.assertEquals(result['subject'], subject)
        self.assertEquals(result['description'], description)
        self.assertEquals(result['status'], status)
        self.assertEquals(result['assigned_to'], assigned_to)
        self.assertEquals(result['priority'], redmine_priority)

        project = 'foo'
        subject = 'Redmine API - Negative Test'
        description = 'This should fail.'
        priority = 1
        assigned_id = None
        result = create_redmine_ticket_for_notification(project, subject, description, priority, assigned_id)
        self.assertTrue(result is None)

        result = get_redmine_ticket_for_notification(-1)
        self.assertTrue(result is None)

        result = get_redmine_ticket_for_notification(ticket_id)
        project = None
        subject = None
        assigned_id = None
        result = update_redmine_ticket_for_notification(ticket_id, project, subject, description, priority, assigned_id)
        self.assertTrue(result is None)