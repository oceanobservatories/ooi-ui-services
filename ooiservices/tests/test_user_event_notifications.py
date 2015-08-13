#!/usr/bin/env python
'''
Specific testing for user_event_notifications (class UserEventNotifications) used in Alerts and Alarms.
'''
__author__ = 'Edna Donoughe'

import unittest
import json
from base64 import b64encode
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import (User, UserScope, Organization)
from ooiservices.app.models import (SystemEventDefinition, SystemEvent, UserEventNotification)
import datetime as dt
import requests

from unittest import skipIf
import os

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''

@skipIf(os.getenv('TRAVIS'), 'Skip if testing from Travis CI.')
class UserEventNotificationsTestCase(unittest.TestCase):

    # enable verbose during development and documentation to get a list of sample
    # urls used throughout test cases. Always set to False before check in.
    verbose = False
    debug = False
    root = 'http://localhost:4000'

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
        scope = UserScope.query.filter_by(scope_name='user_admin').first()
        admin.scopes.append(scope)
        scope = UserScope.query.filter_by(scope_name='redmine').first()     # added
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

    def test_create_user_event_notification(self):
        verbose = self.verbose
        debug = self.debug
        root = self.root
        if verbose: print '\n'

        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        data = {'user_id': 1,
                'system_event_definition_id': 1,
                'use_email': True,
                'use_log': True,
                'use_phone': True,
                'use_redmine': True,
                'use_sms': True,
                }
        good_stuff = json.dumps(data)

        # Create event_event_notification
        response = self.client.post(url_for('main.create_user_event_notification'), headers=headers, data=good_stuff)
        notify_data = json.loads(response.data)
        self.assertEquals(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertTrue(response_data is not None)
        self.assertTrue(len(response_data) > 0)
        self.assertTrue('message' in response_data)
        self.assertTrue(len(response_data['message']) > 0)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # # Create an alarm
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        reference_designator = "CE01ISSP-XX099-01-CTDPFJ999"
        test_alarm = self.create_alert_alarm_definition(reference_designator, event_type='alarm', uframe_id=2, severity=1)

        # (Negative) Create event_event_notification using bad user_id
        data = {'user_id': 10,
                'system_event_definition_id': 1,
                'use_email': True,
                'use_log': True,
                'use_phone': True,
                'use_redmine': True,
                'use_sms': True,
                }
        good_stuff = json.dumps(data)
        response = self.client.post(url_for('main.create_user_event_notification'), headers=headers, data=good_stuff)
        notify_data = json.loads(response.data)
        self.assertEquals(response.status_code, 400)
        notify_data = json.loads(response.data)
        self.assertTrue(notify_data is not None)
        self.assertTrue(len(notify_data) > 0)
        notify = UserEventNotification.query.get(1)

        # (Negative) Create event_event_notification using bad user_id (alpha)
        data = {'user_id': 'A',
                'system_event_definition_id': 1,
                'use_email': True,
                'use_log': True,
                'use_phone': True,
                'use_redmine': True,
                'use_sms': True,
                }
        good_stuff = json.dumps(data)
        response = self.client.post(url_for('main.create_user_event_notification'), headers=headers, data=good_stuff)
        notify_data = json.loads(response.data)
        self.assertEquals(response.status_code, 409)
        notify_data = json.loads(response.data)
        self.assertTrue(notify_data is not None)
        self.assertTrue(len(notify_data) > 0)

        # (Negative) Create event_event_notification using bad value for boolean
        data = {'user_id': 1,
                'system_event_definition_id': 1,
                'use_email': 'A',
                'use_log': True,
                'use_phone': True,
                'use_redmine': True,
                'use_sms': True,
                }
        good_stuff = json.dumps(data)
        response = self.client.post(url_for('main.create_user_event_notification'), headers=headers, data=good_stuff)
        self.assertEquals(response.status_code, 400)
        notify_data = json.loads(response.data)
        self.assertTrue(notify_data is not None)
        self.assertTrue(len(notify_data) > 0)
        #notify = UserEventNotification.query.get(1)


        # (Negative) Create event_event_notification
        response = self.client.post(url_for('main.create_user_event_notification'), headers=headers, data=good_stuff)
        notify_data = json.loads(response.data)
        self.assertEquals(response.status_code, 400)
        notify_data = json.loads(response.data)
        self.assertTrue(notify_data is not None)
        self.assertTrue(len(notify_data) > 0)

        # (Positive) Create event_event_notification
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')
        data = {'user_id': 1,
                'system_event_definition_id': 1,
                'use_email': True,
                'use_log': True,
                'use_phone': True,
                'use_redmine': True,
                'use_sms': True,
                }
        good_stuff = json.dumps(data)

        # Create event_event_notification
        response = self.client.post(url_for('main.create_user_event_notification'), headers=headers, data=good_stuff)
        notify_data = json.loads(response.data)
        self.assertEquals(response.status_code, 201)
        notify_data = json.loads(response.data)
        self.assertTrue(notify_data is not None)
        self.assertTrue(len(notify_data) > 0)
        #notify = UserEventNotification.query.get(1)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alarm definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=test_alarm.id), headers=headers)
        self.assertEquals(response.status_code, 200)
        alarm_definition = json.loads(response.data)
        self.assertTrue(alarm_definition is not None)

        # Get user_event_notifications (1)
        response = self.client.get(url_for('main.get_user_event_notifications'), headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data is not None)
        notifications = data['notifications']
        self.assertTrue(notifications is not None)
        self.assertEquals(len(notifications), 2)

        url = url_for('main.get_user_event_notifications')
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('notifications' in data)
        self.assertTrue(len(data['notifications']) > 0)
        self.assertEquals(len(data['notifications']), 2)

        url = url_for('main.get_user_event_notification', id=1)
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        notification = json.loads(response.data)
        self.assertTrue(len(notification) > 0)
        self.assertEquals(len(notification), 8)

        for attribute in UserEventNotification.__table__.columns._data:
            self.assertTrue(attribute in notification)

        if verbose: print '\n'

    def test_update_user_event_notification(self):
        verbose = False #self.verbose
        root = self.root

        if verbose: print '\n'
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Add a second user ('foo', password 'test')
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        test_username = 'foo'
        test_password = 'test'
        test_email = 'foo@test.com'
        Organization.insert_org()
        User.insert_user(username=test_username, password=test_password, email=test_email)
        self.client = self.app.test_client(use_cookies=False)
        UserScope.insert_scopes()
        foo = User.query.filter_by(user_name='foo').first()
        scope = UserScope.query.filter_by(scope_name='user_admin').first()
        foo.scopes.append(scope)
        scope = UserScope.query.filter_by(scope_name='redmine').first()     # added
        foo.scopes.append(scope)
        db.session.add(foo)
        db.session.commit()

        response = self.client.get(url_for('main.get_user',id=1), headers=headers)
        self.assertTrue(response.status_code == 200)

        response = self.client.get(url_for('main.get_user',id=2), headers=headers)
        self.assertTrue(response.status_code == 200)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # # Create alert and an alarm
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ref_def = "CE01ISSP-XX099-01-CTDPFJ999"
        # Create an alarm with user_event_notification - uses definition 1 and user_id 1
        test_alarm = self.create_alert_alarm_definition(ref_def, event_type='alarm', uframe_id=2, severity=1)

        # Create an alarm without user_event_notification - uses definition 1 and user_id 1
        bad_alarm = self.create_alert_alarm_definition_wo_notification(ref_def, event_type='alarm',
                                                                       uframe_filter_id=2, severity=1)

        notification = self.create_user_event_notification(bad_alarm.id, 2)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alarm definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=test_alarm.id), headers=headers)
        self.assertEquals(response.status_code, 200)
        alarm_definition = json.loads(response.data)
        self.assertTrue(alarm_definition is not None)

        response = self.client.get(url_for('main.get_alert_alarm_def', id=bad_alarm.id), headers=headers)
        self.assertEquals(response.status_code, 200)
        bad_alarm_definition = json.loads(response.data)
        self.assertTrue(bad_alarm_definition is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get user_event_notifications (1)
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_user_event_notifications'), headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data is not None)
        notifications = data['notifications']
        self.assertTrue(notifications is not None)
        self.assertEquals(len(notifications), 2)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get user_event_notification by id=1
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.get_user_event_notification', id=1)
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        notification = json.loads(response.data)
        self.assertTrue(len(notification) > 0)
        self.assertEquals(len(notification), 8)

        """
        Error messages for the following tests:

            1. bad_notification:  {}

            2. 'Invalid ID, user_event_notification record not found.'

            3. 'Inconsistent ID, user_event_notification id provided in data does not match id provided.'

            4. 'Inconsistent User ID, user_id provided in data does not match id.'

            5. 'IntegrityError creating user_event_notification.'

            6. (no error)

            7. 'Insufficient data, or bad data format.'
        """

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (1) Get user_event_notification by id=5 (doesn't exist) response: {}
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        url = url_for('main.get_user_event_notification', id=5)
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        bad_notification = json.loads(response.data)
        self.assertTrue(bad_notification is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (2) (Negative) Update event_event_notification;
        # error: 'Invalid ID, user_event_notification record not found.'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        test = {'user_id': 1,
                'system_event_definition_id': test_alarm.id,
                'use_email': False,
                'use_log': False,
                'use_phone': False,
                'use_redmine': False,
                'use_sms': False,
                'id': 50}
        bad_stuff = json.dumps(test)
        response = self.client.put(url_for('main.update_user_event_notification', id=50), headers=headers, data=bad_stuff)
        self.assertEquals(response.status_code, 400)
        notify_data = json.loads(response.data)
        self.assertTrue(notify_data is not None)
        self.assertTrue('message' in notify_data)
        self.assertTrue(notify_data['message'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (3) (Negative) Update event_event_notification
        # error: 'Inconsistent ID, user_event_notification id provided in data does not match id provided.'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        test = {'user_id': 999,
                'system_event_definition_id': 1,
                'use_email': True,
                'use_log': True,
                'use_phone': True,
                'use_redmine': True,
                'use_sms': True,
                'id': 1}
        good_stuff = json.dumps(test)
        response = self.client.put(url_for('main.update_user_event_notification', id=800), headers=headers, data=good_stuff)
        self.assertEquals(response.status_code, 400)
        notify_data = json.loads(response.data)
        self.assertTrue(notify_data is not None)
        self.assertTrue('message' in notify_data)
        self.assertTrue(notify_data['message'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (4) (Negative) Update user_event_notification, with invalid user_id
        # error: 'Inconsistent User ID, user_id provided in data does not match id.'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        test = {'user_id': 1,
                'system_event_definition_id': 2,
                'use_email': True,
                'use_log': True,
                'use_phone': True,
                'use_redmine': True,
                'use_sms': True,
                'id': 2}
        good_stuff = json.dumps(test)
        response = self.client.put(url_for('main.update_user_event_notification', id=2), headers=headers, data=good_stuff)
        self.assertEquals(response.status_code, 400)
        notify_data = json.loads(response.data)
        self.assertTrue(notify_data is not None)
        self.assertTrue('message' in notify_data)
        self.assertTrue(notify_data['message'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (5) # (Negative) Update event_event_notification
        # error: 'IntegrityError creating user_event_notification.'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        test = {'user_id': 2,
                'system_event_definition_id': bad_alarm.id,
                'use_email': False,
                'use_log': 'log',
                'use_phone': False,
                'use_redmine': False,
                'use_sms': False,
                'id': 2}
        bad_stuff = json.dumps(test)
        response = self.client.put(url_for('main.update_user_event_notification', id=2), headers=headers, data=bad_stuff)
        self.assertEquals(response.status_code, 400)
        notify_data = json.loads(response.data)
        self.assertTrue(notify_data is not None)
        self.assertTrue('message' in notify_data)
        self.assertTrue(notify_data['message'] is not None)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (6) (Positive) Update event_event_notification
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        test = {'user_id': 1,
                'system_event_definition_id': 1,
                'use_email': True,
                'use_log': True,
                'use_phone': True,
                'use_redmine': True,
                'use_sms': True,
                'id': 1}
        good_stuff = json.dumps(test)
        response = self.client.put(url_for('main.update_user_event_notification', id=1), headers=headers, data=good_stuff)
        self.assertEquals(response.status_code, 201)
        notify_data = json.loads(response.data)
        self.assertTrue(notify_data is not None)
        self.assertTrue(len(notify_data) > 0)
        notify = UserEventNotification.query.get(1)

        for attribute in UserEventNotification.__table__.columns._data:
            self.assertTrue(attribute in notify_data)
            if attribute != 'user_id' or attribute != 'id':
                self.assertEquals(getattr(notify,attribute), True)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Update event_event_notification - expect failure, invalid user_id
        # error 'Insufficient data, or bad data format.'
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {'user_id': 10}
        good_stuff = json.dumps(data)
        response = self.client.put(url_for('main.update_user_event_notification', id=1), headers=headers, data=good_stuff)
        self.assertEquals(response.status_code, 409)
        notify_data = json.loads(response.data)
        self.assertTrue(notify_data is not None)
        self.assertTrue('message' in notify_data)
        self.assertTrue(notify_data['message'] is not None)

        if verbose: print '\n'

    def test_user_event_notification_list_routes(self):

        verbose = self.verbose
        debug = self.debug
        root = self.root
        if verbose: print '\n'
        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # # Create alert and an alarm
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        reference_designator = "CE01ISSP-XX099-01-CTDPFJ999"
        # Create and alert and an alarm
        test_alarm = self.create_alert_alarm_definition(reference_designator, event_type='alarm', uframe_id=2, severity=1)
        test_alert = self.create_alert_alarm_definition(reference_designator, event_type='alert', uframe_id=-1, severity=1)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # GET alarm definition by SystemEventDefinition id
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        response = self.client.get(url_for('main.get_alert_alarm_def', id=test_alarm.id), headers=headers)
        self.assertEquals(response.status_code, 200)
        alarm_definition = json.loads(response.data)
        if debug: print '\n -- alarm_definition: ', alarm_definition
        self.assertTrue(alarm_definition is not None)

        # Get user_event_notifications (1)
        response = self.client.get(url_for('main.get_user_event_notifications'), headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data is not None)
        notifications = data['notifications']
        self.assertTrue(notifications is not None)
        self.assertEquals(len(notifications), 2)

        url = url_for('main.get_user_event_notifications')
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('notifications' in data)
        self.assertTrue(len(data['notifications']) > 0)
        self.assertEquals(len(data['notifications']), 2)

        url = url_for('main.get_user_event_notification', id=1)
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        notification = json.loads(response.data)
        self.assertTrue(len(notification) > 0)
        self.assertEquals(len(notification), 8)

        for attribute in UserEventNotification.__table__.columns._data:
            self.assertTrue(attribute in notification)

        url = url_for('main.get_user_event_notifications')
        url += '?user_id=1'
        response = self.client.get(url, content_type=content_type, headers=headers)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('notifications' in data)
        self.assertTrue(len(data['notifications']) > 0)
        self.assertEquals(len(data['notifications']), 2)

        for attribute in UserEventNotification.__table__.columns._data:
            self.assertTrue(attribute in notification)

        url = url_for('main.get_user_event_notifications')
        url += '?user_id=5'
        response = self.client.get(url, content_type=content_type, headers=headers)
        data = json.loads(response.data)
        self.assertEquals(response.status_code, 400)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertTrue(len(data['message']) > 0)

        url = url_for('main.get_user_event_notifications')
        url += '?user_id=A'
        response = self.client.get(url, content_type=content_type, headers=headers)
        data = json.loads(response.data)
        self.assertEquals(response.status_code, 409)
        data = json.loads(response.data)
        self.assertTrue('message' in data)
        self.assertTrue(len(data['message']) > 0)

        if verbose: print '\n'

    def test_user_event_notification_has_required_fields(self):

        verbose = self.verbose
        root = self.root
        if verbose: print '\n'

        headers = self.get_api_headers('admin', 'test')

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Create alarm definition
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        ref_def = "CE01ISSP-XX099-01-CTDPFJ999"
        alarm1 = self.create_alert_alarm_definition_wo_notification(ref_def=ref_def, event_type='alarm',
                                                                    uframe_filter_id=2, severity=1)
        alert_alarm_definition_id = alarm1.id

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Create user_event_notification - without required field user_id
        # (error: 'Insufficient data, or bad data format.')
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {
                'system_event_definition_id': 1,
                'use_email': True,
                'use_log': True,
                'use_phone': True,
                'use_redmine': True,
                'use_sms': True,
                }
        good_stuff = json.dumps(data)

        # Create event_event_notification
        response = self.client.post(url_for('main.create_user_event_notification'), headers=headers, data=good_stuff)
        notify_data = json.loads(response.data)
        self.assertEquals(response.status_code, 409)
        notify_data = json.loads(response.data)
        self.assertTrue(notify_data is not None)
        self.assertTrue(len(notify_data) > 0)
        self.assertTrue('message' in notify_data)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # (Negative) Create user_event_notification - required field use_sms is None
        # (error: 'Insufficient data, or bad data format.')
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        data = {'user_id': None,
                'system_event_definition_id': 1,
                'use_email': True,
                'use_log': True,
                'use_phone': True,
                'use_redmine': True,
                'use_sms': None,
                }
        good_stuff = json.dumps(data)

        # Create event_event_notification
        response = self.client.post(url_for('main.create_user_event_notification'), headers=headers, data=good_stuff)
        self.assertEquals(response.status_code, 409)
        notify_data = json.loads(response.data)
        self.assertTrue(notify_data is not None)
        self.assertTrue(len(notify_data) > 0)
        self.assertTrue('message' in notify_data)

        if verbose: print '\n'

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# private test helper methods and tests
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def create_alert_alarm_definition(self, ref_def, event_type, uframe_id, severity):
        # Note, creates a definition in test database only, just used to exercise SystemEventDefinition class
        # but does NOT create alertfilter id in uframe. An alertfilter is created when the /alert_alarm_definition
        # route is called.
        #headers = self.get_api_headers('admin', 'test')
        #valid_event_type = ['alert','alarm']
        alert_alarm_definition = None
        array_name = ref_def[0:0+2]
        platform_name = ref_def[0:0+14]
        instrument_parameter = 'temperature'
        instrument_parameter_pdid = 'PD100'
        operator = 'GREATER'
        high_value = '10.0'
        low_value = '1.0'
        stream = 'ctdpf_j_cspp_instrument'
        escalate_on = 5
        escalate_boundary = 10
        user_id = 1
        use_email = False
        use_redmine = True
        use_phone = False
        use_log = False
        use_sms = True
        create_time = dt.datetime.now()
        if ref_def == 'CP02PMCO-WFP01-02-DOFSTK000':
            alert_alarm_definition = SystemEventDefinition(reference_designator=ref_def)
            alert_alarm_definition.active = True
            alert_alarm_definition.event_type = event_type
            alert_alarm_definition.array_name = array_name
            alert_alarm_definition.platform_name = platform_name
            alert_alarm_definition.instrument_name = ref_def
            alert_alarm_definition.instrument_parameter = instrument_parameter
            alert_alarm_definition.instrument_parameter_pdid = instrument_parameter_pdid
            alert_alarm_definition.operator = operator
            alert_alarm_definition.created_time = create_time
            alert_alarm_definition.uframe_filter_id = uframe_id
            alert_alarm_definition.high_value = high_value
            alert_alarm_definition.low_value = low_value
            alert_alarm_definition.severity = severity
            alert_alarm_definition.stream = stream
            alert_alarm_definition.escalate_on = escalate_on
            alert_alarm_definition.escalate_boundary = escalate_boundary
            if event_type == 'alarm':
                alert_alarm_definition.uframe_filter_id = uframe_id
            try:
                db.session.add(alert_alarm_definition)
                db.session.commit()
            except Exception as err:
                print '\n ***  CP02PMCO-WFP01-02-DOFSTK000 **** message: ', err.message

            try:
                # Create corresponding UserEventNotification when alert or alarm definition is created
                new_id = UserEventNotification.insert_user_event_notification(
                                                     system_event_definition_id=alert_alarm_definition.id,
                                                     user_id=user_id,
                                                     use_email=use_email,
                                                     use_redmine=use_redmine,
                                                     use_phone=use_phone,
                                                     use_log=use_log,
                                                     use_sms=use_sms)
            except Exception as err:
                print '\n ******* Create CP02PMCO-WFP01-02-DOFSTK000 UserEventNotification message: \n', err.message

        elif alert_alarm_definition == 'CP02PMCO-WFP01-03-CTDPFK000':
            alert_alarm_definition = SystemEventDefinition(reference_designator=ref_def)
            alert_alarm_definition.active = True
            alert_alarm_definition.event_type = event_type
            alert_alarm_definition.array_name = array_name
            alert_alarm_definition.platform_name = platform_name
            alert_alarm_definition.instrument_name = ref_def
            alert_alarm_definition.instrument_parameter = instrument_parameter
            alert_alarm_definition.instrument_parameter_pdid = instrument_parameter_pdid
            alert_alarm_definition.operator = operator
            alert_alarm_definition.created_time = create_time
            alert_alarm_definition.uframe_filter_id = uframe_id
            alert_alarm_definition.high_value = high_value
            alert_alarm_definition.low_value = low_value
            alert_alarm_definition.severity = severity
            alert_alarm_definition.stream = stream
            alert_alarm_definition.escalate_on = escalate_on
            alert_alarm_definition.escalate_boundary = escalate_boundary
            if event_type == 'alarm':
                alert_alarm_definition.uframe_filter_id = uframe_id
            try:
                db.session.add(alert_alarm_definition)
                db.session.commit()
            except Exception as err:
                print '\n ******* Create CP02PMCO-WFP01-03-CTDPFK000 alert_alarm_definition message: \n', err.message

            try:
                # Create corresponding UserEventNotification when alert or alarm definition is created
                new_id = UserEventNotification.insert_user_event_notification(
                                                     system_event_definition_id=alert_alarm_definition.id,
                                                     user_id=user_id,
                                                     use_email=use_email,
                                                     use_redmine=use_redmine,
                                                     use_phone=use_phone,
                                                     use_log=use_log,
                                                     use_sms=use_sms)
            except Exception as err:
                print '\n ******* Create CP02PMCO-WFP01-03-CTDPFK000 UserEventNotification message: \n', err.message


        elif alert_alarm_definition == 'CP02PMCO-WFP01-05-PARADK000':
            alert_alarm_definition = SystemEventDefinition(reference_designator=ref_def)
            alert_alarm_definition.active = True
            alert_alarm_definition.event_type = event_type
            alert_alarm_definition.array_name = array_name
            alert_alarm_definition.platform_name = platform_name
            alert_alarm_definition.instrument_name = ref_def
            alert_alarm_definition.instrument_parameter = instrument_parameter
            alert_alarm_definition.instrument_parameter_pdid = instrument_parameter_pdid
            alert_alarm_definition.operator = operator
            alert_alarm_definition.created_time = create_time
            alert_alarm_definition.uframe_filter_id = uframe_id
            alert_alarm_definition.high_value = high_value
            alert_alarm_definition.low_value = low_value
            alert_alarm_definition.severity = severity
            alert_alarm_definition.stream = stream
            alert_alarm_definition.escalate_on = escalate_on
            alert_alarm_definition.escalate_boundary = escalate_boundary
            if event_type == 'alarm':
                alert_alarm_definition.uframe_filter_id = uframe_id
            try:
                db.session.add(alert_alarm_definition)
                db.session.commit()
            except Exception as err:
                print '\n *** CP02PMCO-WFP01-05-PARADK000 **** message: ', err.message

            try:
                # Create corresponding UserEventNotification when alert or alarm definition is created
                new_id = UserEventNotification.insert_user_event_notification(
                                                     system_event_definition_id=alert_alarm_definition.id,
                                                     user_id=user_id,
                                                     use_email=use_email,
                                                     use_redmine=use_redmine,
                                                     use_phone=use_phone,
                                                     use_log=use_log,
                                                     use_sms=use_sms)
            except Exception as err:
                print '\n ******* Create CP02PMCO-WFP01-05-PARADK000 UserEventNotification message: \n', err.message
        else:
            alert_alarm_definition = SystemEventDefinition(reference_designator=ref_def)
            alert_alarm_definition.active = True
            alert_alarm_definition.event_type = event_type
            alert_alarm_definition.array_name = array_name
            alert_alarm_definition.platform_name = platform_name
            alert_alarm_definition.instrument_name = ref_def
            alert_alarm_definition.instrument_parameter = instrument_parameter
            alert_alarm_definition.instrument_parameter_pdid = instrument_parameter_pdid
            alert_alarm_definition.operator = operator
            alert_alarm_definition.created_time = create_time
            alert_alarm_definition.uframe_filter_id = uframe_id
            alert_alarm_definition.high_value = high_value
            alert_alarm_definition.low_value = low_value
            alert_alarm_definition.severity = severity
            alert_alarm_definition.stream = stream
            alert_alarm_definition.escalate_on = escalate_on
            alert_alarm_definition.escalate_boundary = escalate_boundary
            if event_type == 'alarm':
                alert_alarm_definition.uframe_filter_id = uframe_id
            try:
                db.session.add(alert_alarm_definition)
                db.session.commit()
            except Exception as err:
                print '\n *** %s **** message: %s' % (ref_def,err.message)
            try:
                # Create corresponding UserEventNotification when alert or alarm definition is created
                new_id = UserEventNotification.insert_user_event_notification(
                                                     system_event_definition_id=alert_alarm_definition.id,
                                                     user_id=user_id,
                                                     use_email=use_email,
                                                     use_redmine=use_redmine,
                                                     use_phone=use_phone,
                                                     use_log=use_log,
                                                     use_sms=use_sms)
            except Exception as err:
                print '\n ******* Create UserEventNotification message: \n', err.message
        return alert_alarm_definition

    def create_alert_alarm_definition_wo_notification(self, ref_def, event_type, uframe_filter_id, severity):
        # Note, creates a definition in test database only, just used to exercise SystemEventDefinition class
        # but does NOT create alertfilter id in uframe. An alertfilter is created when the /alert_alarm_definition
        # route is called.
        array_name = ref_def[0:0+2]
        platform_name = ref_def[0:0+14]
        instrument_parameter = 'temperature'
        instrument_parameter_pdid = 'PD100'
        operator = 'GREATER'
        high_value = '10.0'
        low_value = '1.0'
        stream = 'ctdpf_j_cspp_instrument'
        escalate_on = 5
        escalate_boundary = 10
        create_time = dt.datetime.now()

        alert_alarm_definition = SystemEventDefinition(reference_designator=ref_def)
        alert_alarm_definition.active = True
        alert_alarm_definition.event_type = event_type
        alert_alarm_definition.array_name = array_name
        alert_alarm_definition.platform_name = platform_name
        alert_alarm_definition.instrument_name = ref_def
        alert_alarm_definition.instrument_parameter = instrument_parameter
        alert_alarm_definition.instrument_parameter_pdid = instrument_parameter_pdid
        alert_alarm_definition.operator = operator
        alert_alarm_definition.created_time = create_time
        alert_alarm_definition.uframe_filter_id = uframe_filter_id
        alert_alarm_definition.high_value = high_value
        alert_alarm_definition.low_value = low_value
        alert_alarm_definition.severity = severity
        alert_alarm_definition.stream = stream
        alert_alarm_definition.escalate_on = escalate_on
        alert_alarm_definition.escalate_boundary = escalate_boundary
        try:
            db.session.add(alert_alarm_definition)
            db.session.commit()
        except Exception as err:
            print '\n *** %s **** message: %s' % (ref_def,err.message)

        return alert_alarm_definition

    def create_user_event_notification(self, definition_id, user_id):

        notification = None
        user_id = user_id
        use_email = False
        use_redmine = True
        use_phone = False
        use_log = False
        use_sms = True
        try:
            # Create corresponding UserEventNotification when alert or alarm definition is created
            new_id = UserEventNotification.insert_user_event_notification(
                                                 system_event_definition_id=definition_id,
                                                 user_id=user_id,
                                                 use_email=use_email,
                                                 use_redmine=use_redmine,
                                                 use_phone=use_phone,
                                                 use_log=use_log,
                                                 use_sms=use_sms)
            notification = UserEventNotification.query.get(new_id)
        except Exception as err:
            print '\n ******* Create CP02PMCO-WFP01-02-DOFSTK000 UserEventNotification message: \n', err.message

        return notification

    def get_uframe_info(self):
        """ Get uframe alertalarm configuration information. """
        uframe_url = self.app.config['UFRAME_ALERTS_URL']
        timeout = self.app.config['UFRAME_TIMEOUT_CONNECT']
        timeout_read = self.app.config['UFRAME_TIMEOUT_READ']
        return uframe_url, timeout, timeout_read

    '''
    reference_designator = 'CE01ISSP-XX099-01-CTDPFJ999'
    def make_fake_uframe_alertfilter_data(self):
        """ Make uframe input data for evaluation/test processing; works in conjunction with manual ingestion process. """
        result = {
              "@class" : "com.raytheon.uf.common.ooi.dataplugin.alert.alertfilter.AlertFilterRecord",
              "enabled" : True,
              "stream" : "ctdpf_j_cspp_instrument",
              "referenceDesignator" : {
                "node" : "XX099",
                "full" : True,
                "subsite" : "CE01ISSP",
                "sensor" : "01-CTDPFJ999"
              },
              "alertRule" : {
                "filter" : "GREATER",
                "valid" : True,
                "highVal" : 31.0,
                "errMessage" : None,
                "lowVal" : 10.0
              },
              "pdId" : "PD440",
              "eventId" : 2,
              "alertMetadata" : {
                "severity" : -2,
                "description" : "Rule 42"
              }
            }

        return result
    '''


