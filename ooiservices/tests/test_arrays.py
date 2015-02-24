#!/usr/bin/env python
'''
Specific testing of arrays.

'''
__author__ = 'Edna Donoughe'

import unittest
import json
from base64 import b64encode
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import Array, User, UserScope, Organization

'''
These tests are additional to the normal testing performed by coverage; each of
these tests are to validate model logic outside of db management.

'''
class UserTestCase(unittest.TestCase):
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
    def _check_array_fields_provided(self, response_data):
        '''
        verify all data fields for Array object are [returned] in response_data
        '''
        result = False
        try:
            self.assertTrue(len(response_data) > 0)
            self.assertTrue(type(response_data) == type(''))
            self.assertTrue('id' in response_data)
            self.assertTrue('array_code'   in response_data)
            self.assertTrue('array_name'   in response_data)
            self.assertTrue('description'  in response_data)
            self.assertTrue('display_name' in response_data)
            self.assertTrue('geo_location' in response_data)
            result = True
        except Exception, err:
            print '\n *** _check_array_fields_provided: error: %s' % err

        return result

    def test_array(self):
        '''
        general test for array api route for lists
        '''
        content_type = 'application/json'

        #Create a sample data set.
        array_code = Array(array_code='CE')
        db.session.add(array_code)
        db.session.commit()

        response = self.client.get(url_for('main.get_arrays'), content_type=content_type )
        self.assertTrue(response.status_code == 200)

        response = self.client.get(url_for('main.get_array',id='CE'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

    #Test user API routes
    #Test [GET] /arrays/<string:id> - 'main.get_array'
    #Test [GET] /array              - 'main.get_arrays'
    def test_arrays_route(self):

        content_type = 'application/json'

        # Create test data - two arrays
        array_CE = Array(array_code='CE')
        array_CE.array_name  = 'Endurance'
        array_CE.description = 'Coastal node array description...'
        array_CE.display_name= 'Coastal Endurance'
        array_CE.geo_location= 'POINT(-70 40)'
        db.session.add(array_CE)
        db.session.commit()

        array_NU = Array(array_code='RS')
        array_NU.array_name  = 'Regional Scale'
        array_NU.description = 'Coastal node array off Washington and Oregon coasts...'
        array_NU.display_name= 'Coastal Regional Scale'
        array_NU.geo_location= 'POINT(-70 45)'
        db.session.add(array_NU)
        db.session.commit()

        response = self.client.get(url_for('main.get_array',id='RS'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

        # verify resulting fields for array are returned
        response_data = response.data
        self.assertTrue(self._check_array_fields_provided(response_data))

        #TODO Verify two arrays are returned
        response = self.client.get(url_for('main.get_arrays'), content_type=content_type)
        self.assertTrue(response.status_code == 200)


    # Test [PUT] /arrays/<int:id> - 'main.update_array'
    def test_update_array(self):

        content_type =  'application/json'
        headers = self.get_api_headers('admin', 'test')

        # Create array data
        array_CE = Array(array_code='CE')
        array_CE.array_name  = 'Endurance'
        array_CE.description = 'description...'
        array_CE.display_name= 'Coastal Endurance'
        array_CE.geo_location= 'POINT(-70 40)'
        db.session.add(array_CE)
        db.session.commit()

        data = json.dumps({'description':'description update'})
        response = self.client.put(url_for('main.update_array', id=1), headers=headers, data=data)
        self.assertTrue(response.status_code == 200)

        # fetch array and compare contents returned with expected contents
        response = self.client.get(url_for('main.get_array',id='CE'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

        # verify resulting fields for array are returned
        response_data = response.data
        self.assertTrue(self._check_array_fields_provided(response_data))

        # create dictionary from string;
        dict_data = json.loads(response_data)

        expected_data = {'array_code': 'CE', 'display_name':'Coastal Endurance',
                         'description': 'description update','array_name': 'Endurance', 'id': 1,
                         'geo_location': {u'type': u'Point', u'coordinates': [-70, 40]}, }
        self.assertTrue(dict_data == expected_data)

    # Test [PUT] /arrays/<int:id> - 'main.update_array'
    def test_update_array_with_error(self):

        headers = self.get_api_headers('admin', 'test')

        # Create array with geo_locations == None
        array_CE = Array(array_code='CE')
        array_CE.array_name  = 'Endurance'
        array_CE.description = 'description...'
        array_CE.display_name= 'Coastal Endurance'
        array_CE.geo_location= None
        db.session.add(array_CE)
        db.session.commit()

        data = json.dumps({'description':'update'})
        response = self.client.put(url_for('main.update_array', id=1), headers=headers, data=data)
        self.assertTrue(response.status_code == 409)

    # Test [PUT] /arrays/<int:id> - 'main.update_array'
    def test_update_array_with_empty_values(self):
        '''
        Create array with empty values: array_code, display_name
        Add test for empty geo_location
        '''
        headers = self.get_api_headers('admin', 'test')

        # Create array with array_code empty, expect failure
        array_ac = Array(array_code='')
        array_ac.array_name  = 'Endurance'
        array_ac.description = 'description...'
        array_ac.display_name= 'Coastal Endurance'
        array_ac.geo_location= 'POINT(-70 40)'
        db.session.add(array_ac)
        db.session.commit()

        data = json.dumps({'description':'update'})
        response = self.client.put(url_for('main.update_array', id=1), headers=headers, data=data)
        self.assertTrue(response.status_code == 409)

        # Create array with display_name empty, expect failure
        array_dn = Array(array_code='DN')
        array_dn.array_name  = 'name'
        array_dn.description = 'description...'
        array_dn.display_name= ''
        array_dn.geo_location= 'POINT(-70 40)'
        db.session.add(array_dn)
        db.session.commit()

        data = json.dumps({'description':'update'})
        response = self.client.put(url_for('main.update_array', id=1), headers=headers, data=data)
        self.assertTrue(response.status_code == 409)

        # Create valid array object, update with geo_location empty, expect failure
        array_gl = Array(array_code='GL')
        array_gl.array_name  = 'name'
        array_gl.description = 'description...'
        array_gl.display_name= 'display name'
        array_gl.geo_location= 'POINT(-70 40)'
        db.session.add(array_gl)
        db.session.commit()

        data = json.dumps({'geo_location':''})
        response = self.client.put(url_for('main.update_array', id=1), headers=headers, data=data)
        self.assertTrue(response.status_code == 409)

    # Test [POST] /arrays/ - 'main.create_array'
    def test_create_array(self):

        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')

        # Create array data
        data = {}
        data['array_code']   = 'RS'
        data['array_name']   = 'Regional Scale Node'
        data['display_name'] = 'Coastal Regional Scale Node'
        data['description']  = 'Coastal array located off Washington and Oregon coasts.'
        data["geo_location"] = 'POINT(-70 40)'

        data = json.dumps(data)
        response = self.client.post(url_for('main.create_array'), headers=headers,data=data)
        self.assertEquals(response.status_code, 201)

        response = self.client.get(url_for('main.get_array',id='RS'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

    # Test [POST] /arrays/ - 'main.create_array'
    def test_create_duplicate_array_code(self):

        content_type = 'application/json'
        headers = self.get_api_headers('admin', 'test')

        # Create array
        data = {}
        data['array_code']   = 'RS'
        data['array_name']   = 'Regional Scale Node'
        data['display_name'] = 'Coastal Regional Scale Node'
        data['description']  = 'Coastal array located off Washington and Oregon coasts.'
        data['geo_location'] = 'POINT(-70 40)'

        data = json.dumps(data)
        response = self.client.post(url_for('main.create_array'), headers=headers,data=data)
        self.assertEquals(response.status_code, 201)

        response = self.client.get(url_for('main.get_array',id='RS'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

        response = self.client.post(url_for('main.create_array'), headers=headers,data=data)
        self.assertEquals(response.status_code, 201)

        response = self.client.get(url_for('main.get_array',id='RS'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

    # Test [POST] /arrays/ - 'main.create_array'
    def test_create_array_with_missing_data(self):

        headers = self.get_api_headers('admin', 'test')

        # Create array with missing data array_code; expect failure
        data = {}
        data['array_name'] = 'Regional Scale Node'
        data['display_name'] = 'Coastal Regional Scale Node'
        data['geolocation']= {'coordinates': [-70,45],'type': 'Point'}
        data['description']= 'Coastal array located off Washington and Oregon coasts.'

        response = self.client.post(url_for('main.create_array'), headers=headers, data=json.dumps(data))
        self.assertEquals(response.status_code, 409)

    # Test [POST] /arrays/ - 'main.create_array'
    def test_create_array_with_empty_data(self):

        headers = self.get_api_headers('admin', 'test')

        # Create array with empty array_code; expect failure
        bad_data = {}
        bad_data['array_code']   = None
        bad_data['array_name']   = 'Regional Scale Node'
        bad_data['display_name'] = 'Coastal Regional Scale Node'
        bad_data['geolocation']  = {'coordinates': [-70,45],'type': 'Point'}
        bad_data['description']  = 'Coastal array located off Washington and Oregon coasts.'

        data = json.dumps(bad_data)
        response = self.client.post(url_for('main.create_array'), headers=headers,data=data)
        self.assertEquals(response.status_code, 409)

    # Test [DELETE] '/arrays/<int:id>' - 'main.delete_array'
    def test_delete_array(self):

        headers = self.get_api_headers('admin', 'test')

        # Create array
        array_CE = Array(array_code='CE')
        array_CE.array_name  = 'Endurance'
        array_CE.description = 'description...'
        array_CE.display_name= 'Coastal Endurance'
        array_CE.geo_location= 'POINT(-70 45)'
        db.session.add(array_CE)
        db.session.commit()

        response = self.client.delete(url_for('main.delete_array', id=1), headers=headers)
        self.assertEquals(response.status_code, 200)

    # Test [DELETE] '/arrays/<int:id>' - 'main.delete_array'
    def test_delete_unknown_array(self):

        headers = self.get_api_headers('admin', 'test')
        # Create array, attempt to retrieve non-existent array using invalid id
        array_CE = Array(array_code='CE')
        array_CE.array_name  = 'Endurance'
        array_CE.description = 'description...'
        array_CE.display_name= 'Coastal Endurance'
        array_CE.geo_location= 'POINT(-70 45)'
        db.session.add(array_CE)
        db.session.commit()

        response = self.client.delete(url_for('main.delete_array', id=5), headers=headers)
        self.assertEquals(response.status_code, 409)

