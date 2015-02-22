#!/usr/bin/env python
'''
Specific testing of routes.

'''
__author__ = 'Edna Donoughe'

import unittest
import json
from base64 import b64encode
from flask import url_for
from ooiservices.app import create_app, db
from ooiservices.app.models import InstrumentDeployment, PlatformDeployment, Instrumentname, Organization
from ooiservices.app.models import User, UserScope
import datetime as dt

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

    '''
    {
      "depth": 500.0,
      "display_name": "CTDMO",
      "end_date": null,
      "geo_location": null,
      "id": 683,
      "platform_deployment_id": 198,
      "reference_designator": "GS03FLMB-RIS02-11-CTDMOG",
      "start_date": null
    }
    '''
    def _check_instrument_deployment_fields_provided(self, response_data):

        #verify all data fields for InstrumentDeployment object are [returned] in response_data

        result = False
        try:
            self.assertTrue(len(response_data) > 0)
            self.assertTrue(type(response_data) == type(''))
            self.assertTrue('id' in response_data)
            self.assertTrue('depth'   in response_data)
            self.assertTrue('geo_location'   in response_data)
            self.assertTrue('display_name'   in response_data)
            self.assertTrue('end_date'   in response_data)
            self.assertTrue('start_date' in response_data)
            self.assertTrue('platform_deployment_id' in response_data)
            self.assertTrue('reference_designator'   in response_data)

            result = True
        except Exception, err:
            print '\n *** _check_instrument_deployment_fields_provided: error: %s' % err

        return result

    '''
    import datetime as dt
    scenario_timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    '''

    #Test routes
    #Test [GET] /platform_deployments - 'main.get_platform_deployments'
    def test_route_get_instrument_deployments(self):

        content_type = 'application/json'

        # Create a sample data set:
        # Summary: 2 platform deployments, three instrument deployments
        # Contents:
        #     1. platform deployment:       CE04OSSM-SBD11
        #         instrument deployment(1): CE04OSSM-SBD11-01-MOPAK0000
        #
        #     2. platform deployment:       GS05MOAS-PG002
        #         instrument deployment(1): GS05MOAS-PG002-02-FLORDM000
        #         instrument deployment(2): GS05MOAS-PG002-04-PARADM000
        #

        # platform_deployment(s) - CE04OSSM-SBD11, GS05MOAS-PG002
        # platform deployment 1
        CE04OSSM_SBD11_rd = 'CE04OSSM-SBD11'
        CE04OSSM_SBD11    = PlatformDeployment(reference_designator=CE04OSSM_SBD11_rd)
        db.session.add(CE04OSSM_SBD11)
        db.session.commit()
        CE04OSSM_SBD11_id = CE04OSSM_SBD11.id

        # platform deployment 2
        GS05MOAS_PG002_rd = 'GS05MOAS-PG002'
        GS05MOAS_PG002    = PlatformDeployment(reference_designator=GS05MOAS_PG002_rd)
        db.session.add(GS05MOAS_PG002)
        db.session.commit()
        GS05MOAS_PG002_id = GS05MOAS_PG002.id

        # Create multiple instrument deployments for multiple platforms
        # instrument deployment 1 (platform deployment 1)
        number_of_instruments = 3
        MOPAK0000_rd = 'CE04OSSM-SBD11-01-MOPAK0000'
        MOPAK0000 = InstrumentDeployment(reference_designator=MOPAK0000_rd)
        # todo get remaining data for this instrument
        db.session.add(MOPAK0000)
        db.session.commit()
        MOPAK0000_id = MOPAK0000.id

        # instrument deployment 2 (platform deployment 2 - first instrument)
        FLORDM000_rd = 'GS05MOAS-PG002-02-FLORDM000'
        FLORDM000 = InstrumentDeployment(reference_designator=FLORDM000_rd)
        FLORDM000.depth = 1000.0
        FLORDM000.display_name = '2-Wavelength Fluorometer'
        FLORDM000.end_date = dt.datetime.now()
        FLORDM000.geo_location = 'POINT(-70 40)'
        FLORDM000.platform_deployment_id = GS05MOAS_PG002_id        # actual 754
        FLORDM000.reference_designator = FLORDM000_rd
        FLORDM000.start_date = dt.datetime.now()
        db.session.add(FLORDM000)
        db.session.commit()
        FLORDM000_id = FLORDM000.id

        # instrument deployment 3 (platform deployment 2 - second instrument)
        PARADM000_rd = 'GS05MOAS-PG002-04-PARADM000'
        PARADM000 = InstrumentDeployment(reference_designator=PARADM000_rd)
        PARADM000.depth = 1000.0
        PARADM000.display_name = 'Photosynthetically Available Radiation'
        PARADM000.end_date = dt.datetime.now()
        PARADM000.geo_location = 'POINT(-70 40)'
        PARADM000.platform_deployment_id = GS05MOAS_PG002_id         # actual 774
        PARADM000.reference_designator = PARADM000_rd
        PARADM000.start_date = dt.datetime.now()
        db.session.add(PARADM000)
        db.session.commit()
        PARADM000_id = PARADM000.id

        # Get all instrument deployments; verify 3 instruments returned
        response = self.client.get(url_for('main.get_instrument_deployments'), content_type=content_type)
        self.assertTrue(response.status_code == 200)
        all_data = json.loads(response.data)

        # Verify three instruments
        self.assertIn('instrument_deployments', all_data)
        list_all_data = all_data['instrument_deployments']
        len_list_all_data = len(list_all_data)
        self.assertTrue(len_list_all_data > 0)
        self.assertEquals(len_list_all_data, number_of_instruments)

        # todo Verify each instrument is associated with correct platform deployment id

        # Get instrument MOPAK0000
        response = self.client.get(url_for('main.get_instrument_deployment', id=MOPAK0000_id), content_type=content_type)
        self.assertTrue(response.status_code == 200)
        MOPAK0000_data = json.loads(response.data[:])
        # todo Verify (a) all required fields provided, (b)content as expected and (c) geo_location not null

        # Get instrument FLORDM000
        response = self.client.get(url_for('main.get_instrument_deployment', id=FLORDM000_id), content_type=content_type)
        self.assertTrue(response.status_code == 200)
        FLORDM000_data = json.loads(response.data[:])
        # todo Verify (a) all required fields provided, (b)content as expected and (c) geo_location not null

        # Get instrument PARADM000
        response = self.client.get(url_for('main.get_instrument_deployment', id=PARADM000_id), content_type=content_type)
        self.assertTrue(response.status_code == 200)
        PARADM000_data = json.loads(response.data[:])
        # todo Verify (a) all required fields provided, (b)content as expected and (c) geo_location not null

        response = self.client.get('/instrument_deployment?platform_deployment_id=%s' % GS05MOAS_PG002_id)
        self.assertTrue(response.status_code == 200)
        response_data = response.data

        self.assertTrue(self._check_instrument_deployment_fields_provided(response_data))

        if 'instrument_deployments' in response_data:
            ins_data = json.loads(response_data)
            list_instrument_deployment = ins_data['instrument_deployments']

        self.assertEquals(list_instrument_deployment[0], FLORDM000_data)
        self.assertEquals(response.status_code, 200)

        #TODO add search parameter test (TBD)
        #response = self.client.get('/platform_deployments?search="CE04OSSM-SBD11-01-MOPAK0000"')
        #self.assertTrue(response.status_code == 404)

    #Test [GET] /platform_deployments - 'main.get_platform_deployments'
    def test_route_get_instrument_deployment_with_unknown_platform_deployment_id(self):

        content_type = 'application/json'

        # platform deployment GS05MOAS_PG002
        GS05MOAS_PG002_rd = 'GS05MOAS-PG002'
        GS05MOAS_PG002    = PlatformDeployment(reference_designator=GS05MOAS_PG002_rd)
        db.session.add(GS05MOAS_PG002)
        db.session.commit()
        GS05MOAS_PG002_id = GS05MOAS_PG002.id

        # instrument deployment FLORDM000
        FLORDM000_rd = 'GS05MOAS-PG002-02-FLORDM000'
        FLORDM000 = InstrumentDeployment(reference_designator=FLORDM000_rd)
        FLORDM000.depth = 1000.0
        FLORDM000.display_name = '2-Wavelength Fluorometer'
        FLORDM000.end_date = dt.datetime.now()
        FLORDM000.geo_location = 'POINT(-70 40)'
        FLORDM000.platform_deployment_id = GS05MOAS_PG002_id        # actual 754
        FLORDM000.reference_designator = FLORDM000_rd
        FLORDM000.start_date = dt.datetime.now()
        db.session.add(FLORDM000)
        db.session.commit()
        FLORDM000_id = FLORDM000.id

        # Get all instrument deployments
        response = self.client.get(url_for('main.get_instrument_deployments'), content_type=content_type)
        all_data = json.loads(response.data)
        self.assertIn('instrument_deployments', all_data)
        list_all_data = all_data['instrument_deployments']
        len_list_all_data = len(list_all_data)
        self.assertTrue(len_list_all_data > 0)
        self.assertTrue(response.status_code == 200)

        # for platform_deployment_id which doesn't exist; expect failure (receive 200)
        #TODO returns empty list of instrument_deployments and status_code 200; correct?
        response = self.client.get('/instrument_deployment?platform_deployment_id=9999')

        # Verify result return has instrument_deployments and list is empty
        response_data = json.loads(response.data[:])
        self.assertIn('instrument_deployments', response_data)
        list_instrument_deployments = response_data['instrument_deployments']
        len_list_instrument_deployments = len(list_instrument_deployments)
        self.assertEquals(0, len(list_instrument_deployments))

        self.assertEquals(response.status_code, 200)
        self.assertTrue(all_data != response_data)

    # Test [DELETE] '/instrument_deployment/<int:id>' - 'main.delete_instrument_deployment'
    def test_delete_instrument_deployment(self):

        headers = self.get_api_headers('admin', 'test')
        content_type = 'application/json'

        # Create platform deployment for foreign key constraints when creating
        # instrument_deployment (note: using actual platform_deployment id 203)
        GS05MOAS_PG002_rd = 'GS05MOAS-PG002'
        GS05MOAS_PG002 = PlatformDeployment(reference_designator=GS05MOAS_PG002_rd)
        db.session.add(GS05MOAS_PG002)
        db.session.commit()
        GS05MOAS_PG002_id = GS05MOAS_PG002.id
        number_of_platform_deployments = 1

        # Create instrument(s) for preiously created platform deployment; required for
        # foreign keys - otherwise foreign key violation received.
        number_of_instruments = 2
        #TODO General: Review, test and catch foreign key violations
        FLORDM000_rd = 'GS05MOAS-PG002-02-FLORDM000'
        FLORDM000 = InstrumentDeployment(reference_designator=FLORDM000_rd)
        FLORDM000.depth = 1000.0
        FLORDM000.display_name = '2-Wavelength Fluorometer'
        FLORDM000.end_date = dt.datetime.now()
        FLORDM000.geo_location = 'POINT(-70 40)'
        FLORDM000.platform_deployment_id = GS05MOAS_PG002_id                # actual 754
        FLORDM000.reference_designator = FLORDM000_rd
        FLORDM000.start_date = dt.datetime.now()
        db.session.add(FLORDM000)
        db.session.commit()
        FLORDM000_id = FLORDM000.id

        PARADM000_rd = 'GS05MOAS-PG002-04-PARADM000'
        PARADM000 = InstrumentDeployment(reference_designator=PARADM000_rd)
        PARADM000.depth = 1000.0
        PARADM000.display_name = 'Photosynthetically Available Radiation'
        PARADM000.end_date = dt.datetime.now()
        PARADM000.geo_location = 'POINT(-70 40)'
        PARADM000.platform_deployment_id = GS05MOAS_PG002_id                # actual 774
        PARADM000.reference_designator = PARADM000_rd
        PARADM000.start_date = dt.datetime.now()
        db.session.add(PARADM000)
        db.session.commit()
        PARADM000_id = PARADM000.id


        instrument_name_FLORD = Instrumentname()
        instrument_name_FLORD.instrument_class = 'FLORD'
        instrument_name_FLORD.display_name = '2-Wavelength Fluorometer'
        instrument_name_FLORD.id = 18
        db.session.add(instrument_name_FLORD)
        db.session.commit()

        instrument_name_PARAD = Instrumentname()
        instrument_name_PARAD.instrument_class = 'PARAD'
        instrument_name_PARAD.display_name = 'Photosynthetically Available Radiation'
        instrument_name_PARAD.id = 34
        db.session.add(instrument_name_PARAD)
        db.session.commit()

        #TODO
        # Scenario:
        # Verify exists: (1) one platform_deployment; (2) two instrument deployments and the
        # todo (3) two instrument deployments are properly formed in platform deployment
        # delete first instrument deployment, verify success
        # verify platform deployment has only one instrument deployment (checks model foreign key usage)
        # delete remaining instrument deployment
        # check platform_deployment exists and has no instrument deployments

        # Get all platform deployments; verify platform deployment count
        response = self.client.get(url_for('main.get_platform_deployments'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

        # Verify number of platform deployments
        all_pd_data = json.loads(response.data)
        self.assertIn('platform_deployments', all_pd_data)
        list_all_pd_data = all_pd_data['platform_deployments']
        len_list_all_pd_data = len(list_all_pd_data)
        self.assertTrue(len_list_all_pd_data > 0)
        self.assertEquals(len_list_all_pd_data, number_of_platform_deployments)

        # Verify number of instruments for platform deployment GS05MOAS_PG002
        response = self.client.get('/instrument_deployment?platform_deployment_id=%d' % GS05MOAS_PG002_id)
        self.assertTrue(response.status_code == 200)

        # Verify result has instrument_deployments and number of instrument_deployments is correct
        response_data = json.loads(response.data[:])
        self.assertIn('instrument_deployments', response_data)
        list_instrument_deployments = response_data['instrument_deployments']
        len_list_instrument_deployments = len(list_instrument_deployments)
        self.assertEquals(number_of_instruments, len_list_instrument_deployments)

        # TODO Verify instrument_deployments are properly formed and valid for this platform deployment (GS05MOAS_PG002)
        # Check number of instrument deployments and verify display_name not None
        # Verify for each instrument return by platform id (GS05MOAS_PG002_id), the display name
        # is equal to display name returned from Instrumentname based on instrument class
        check_instrument_deployment_display_names = 0
        for instrument_deployment in list_instrument_deployments:
            self.assertIn('display_name', instrument_deployment)
            self.assertIn('id', instrument_deployment)
            self.assertTrue(instrument_deployment['id'] != None)
            self.assertTrue(instrument_deployment['id'] > 0)

            display_name = instrument_deployment['display_name']
            instrument_class = instrument_deployment['reference_designator'][18:23]
            foo = Instrumentname.query.filter(Instrumentname.instrument_class == instrument_class).first()
            _display_name = foo.display_name
            self.assertTrue(_display_name != None)
            self.assertEquals(display_name, _display_name)
            check_instrument_deployment_display_names += 1

        self.assertEquals(check_instrument_deployment_display_names, number_of_instruments)

        # Get all instrument deployments; verify instrument deployment count
        response = self.client.get(url_for('main.get_instrument_deployments'), content_type=content_type)
        self.assertTrue(response.status_code == 200)

        all_data = json.loads(response.data)
        self.assertIn('instrument_deployments', all_data)
        list_all_data = all_data['instrument_deployments']
        len_list_all_data = len(list_all_data)
        self.assertTrue(len_list_all_data > 0)
        self.assertEquals(len_list_all_data, number_of_instruments)

        # Delete instrument deployment FLORDM000
        response = self.client.delete(url_for('main.delete_instrument_deployment', id=FLORDM000_id), headers=headers)
        self.assertEquals(response.status_code, 200)

        # Now verify list of instruments for platform deployments reflects deleted instrument deployment
        response = self.client.get('/instrument_deployment?platform_deployment_id=%d' % GS05MOAS_PG002_id)
        self.assertTrue(response.status_code == 200)

        # Verify number of instruments for platform deployment GS05MOAS_PG002 is one less than number_of_instruments
        response_data = json.loads(response.data[:])
        self.assertIn('instrument_deployments', response_data)
        curr_list_instrument_deployments = response_data['instrument_deployments']
        #len_curr_list_instrument_deployments = len(curr_list_instrument_deployments)
        self.assertEquals((number_of_instruments - 1), len(curr_list_instrument_deployments))

        # Delete instrument deployment PARADM000
        response = self.client.delete(url_for('main.delete_instrument_deployment', id=PARADM000_id), headers=headers)
        self.assertEquals(response.status_code, 200)

        # Now verify list of instruments for platform deployments reflects deleted instrument deployment
        response = self.client.get('/instrument_deployment?platform_deployment_id=%d' % GS05MOAS_PG002_id)
        self.assertTrue(response.status_code == 200)

        # Verify no instruments for platform deployment GS05MOAS_PG002
        expected_empty_response_data = {"instrument_deployments": []}
        response_data = json.loads(response.data[:])
        self.assertIn('instrument_deployments', response_data)
        curr_list_instrument_deployments = response_data['instrument_deployments']
        len_curr_list_instrument_deployments = len(curr_list_instrument_deployments)
        self.assertEquals((number_of_instruments - 2), len_curr_list_instrument_deployments)
        self.assertEquals(response_data, expected_empty_response_data)

    def _get_instrument_display_name(self, instrument_json):
        self.assertTrue(instrument_json, None)
        self.assertIn('display_name', instrument_json)
        self.assertTrue(instrument_json['display_name'] != None)
        return instrument_json['display_name']

    # Test [GET] '/instrument_deployment/<int:id>' - 'main.get_instrument_deployment'
    def test_get_unknown_instrument_deployment(self):
        '''
        delete non existent instrument deployment, expect failure code
        '''
        headers = self.get_api_headers('admin', 'test')
        response = self.client.get(url_for('main.get_instrument_deployment', id=9999), headers=headers)
        self.assertEquals(response.status_code, 404)

    # Test [DELETE] '/instrument_deployment/<int:id>' - 'main.delete_instrument_deployment'
    def test_delete_unknown_instrument_deployment(self):
        '''
        delete non existent instrument deployment, expect failure code
        '''
        headers = self.get_api_headers('admin', 'test')
        response = self.client.delete(url_for('main.delete_instrument_deployment', id=9999), headers=headers)
        self.assertEquals(response.status_code, 404)

    # TODO: Requires proper validation in models.InstrumentDeployment from_json method
    # Test [POST] /instrument_deployment - 'main.post_instrument_deployment'
    # def test_post_instrument_deployment(self):
    #     '''
    #     create new instrument deployment
    #     '''
    #     headers = self.get_api_headers('admin', 'test')
    #     content_type = 'application/json'
    #
    #     # Create platform deployment for foreign key constraints when creating
    #     # instrument_deployment (note: using platform_deployment with actual id=203)
    #     GS05MOAS_PG002_rd = 'GS05MOAS-PG002'
    #     GS05MOAS_PG002 = PlatformDeployment(reference_designator=GS05MOAS_PG002_rd)
    #     db.session.add(GS05MOAS_PG002)
    #     db.session.commit()
    #     GS05MOAS_PG002_id = GS05MOAS_PG002.id
    #     number_of_platform_deployments = 1
    #
    #     # Create instrument(s) for preiously created platform deployment; required for
    #     # foreign keys - otherwise foreign key violation received.
    #     number_of_instruments = 1
    #     FLORDM000_rd = 'GS05MOAS-PG002-02-FLORDM000'
    #     FLORDM000 = InstrumentDeployment(reference_designator=FLORDM000_rd)
    #     FLORDM000.depth = 1000.0
    #     FLORDM000.display_name = '2-Wavelength Fluorometer'
    #     FLORDM000.end_date = dt.datetime.now()
    #     FLORDM000.geo_location = 'POINT(-70 40)'
    #     FLORDM000.platform_deployment_id = GS05MOAS_PG002_id                # actual 754
    #     FLORDM000.reference_designator = FLORDM000_rd
    #     FLORDM000.start_date = dt.datetime.now()
    #     db.session.add(FLORDM000)
    #     db.session.commit()
    #     FLORDM000_id = FLORDM000.id
    #
    #     # Create data to post
    #     # {'coordinates': [-70,45],'type': 'Point'},
    #     # 'POINT(-70 40)',
    #     FLORDM000_data = {'display_name': '2-Wavelength Fluorometer',
    #                      'platform_deployment_id': GS05MOAS_PG002_id,
    #                      'end_date': '2015-02-16',
    #                      'start_date': '2015-02-15',
    #                      'reference_designator': 'GS05MOAS-PG002-02-FLORDM000',
    #                      'depth': 500.0,
    #                      'geo_location': None,
    #                      'id': (FLORDM000_id+1)}
    #
    #     data = json.dumps(FLORDM000_data)
    #     response = self.client.post(url_for('main.post_instrument_deployment'), headers=headers, data=data)
    #     self.assertEquals(response.status_code, 201)
    #
    #     # Get new instrument FLORDM000 and compare get results with initial data
    #     response = self.client.get(url_for('main.get_instrument_deployment', id=(FLORDM000_id+1)), content_type=content_type)
    #     self.assertTrue(response.status_code == 200)
    #     get_FLORDM000_data = json.loads(response.data[:])
    #     self.assertEquals(get_FLORDM000_data, FLORDM000_data)
    #
    #     # Create bad data
    #     bad_data =  {'make': 'mercedes',
    #                  'model': 'SL450',
    #                  'engine_style': '2015-02-16'
    #                 }
    #     # Send bad data to POST, generate ValueError
    #     data = json.dumps(bad_data)
    #     response = self.client.post(url_for('main.post_instrument_deployment'), headers=headers, data=data)
    #     self.assertEquals(response.status_code, 400)

    # Test [PUT] /instrument_deployment/<int:id> - 'main.put_instrument_deployment'
    def test_put_instrument_deployment(self):
        '''
        update instrument deployment
        '''
        headers = self.get_api_headers('admin', 'test')
        content_type = 'application/json'

        # Create platform deployment for foreign key constraints when creating
        # instrument_deployment (note: using platform_deployment with actual id=203)
        GS05MOAS_PG002_rd = 'GS05MOAS-PG002'
        GS05MOAS_PG002 = PlatformDeployment(reference_designator=GS05MOAS_PG002_rd)
        db.session.add(GS05MOAS_PG002)
        db.session.commit()
        GS05MOAS_PG002_id = GS05MOAS_PG002.id
        number_of_platform_deployments = 1

        # Create instrument(s) for previously created platform deployment; required for
        # foreign keys - otherwise foreign key violation received.
        number_of_instruments = 1
        FLORDM000_rd = 'GS05MOAS-PG002-02-FLORDM000'
        FLORDM000 = InstrumentDeployment(reference_designator=FLORDM000_rd)
        FLORDM000.depth = 1000.0
        FLORDM000.display_name = '2-Wavelength Fluorometer'
        FLORDM000.end_date = dt.datetime.now()
        FLORDM000.geo_location = 'POINT(-70 40)'
        FLORDM000.platform_deployment_id = GS05MOAS_PG002_id                # actual 754
        FLORDM000.reference_designator = FLORDM000_rd
        FLORDM000.start_date = dt.datetime.now()
        db.session.add(FLORDM000)
        db.session.commit()
        FLORDM000_id = FLORDM000.id

        # Create data to post
        original_FLORDM000_data = {'display_name': '2-Wavelength Fluorometer',
                         'platform_deployment_id': GS05MOAS_PG002_id,
                         'end_date': '2015-02-15',
                         'start_date': '2015-02-15',
                         'reference_designator': 'GS05MOAS-PG002-02-FLORDM000',
                         'depth': 1000.0,
                         'geo_location': {'coordinates': [-70,45],'type': 'Point'},
                         'id': FLORDM000_id}

        modified_FLORDM000_data = {'display_name': '2-Wavelength Fluorometer',
                         'platform_deployment_id': GS05MOAS_PG002_id,
                         'end_date': '2015-02-16',
                         'start_date': '2015-02-15',
                         'reference_designator': 'GS05MOAS-PG002-02-FLORDM000',
                         'depth': 500.0,
                         'geo_location': None,
                         'id': FLORDM000_id}

        data = json.dumps(modified_FLORDM000_data)
        response = self.client.put(url_for('main.put_instrument_deployment', id=FLORDM000_id), headers=headers, data=data)
        self.assertEquals(response.status_code, 200)

        # Get updated instrument FLORDM000; compare to data modifications requested
        response = self.client.get(url_for('main.get_instrument_deployment', id=FLORDM000_id), content_type=content_type)
        self.assertTrue(response.status_code == 200)
        FLORDM000_data = json.loads(response.data[:])
        self.assertEquals(FLORDM000_data, modified_FLORDM000_data)

        # Send unknown id for PUT, expect failure
        data = json.dumps(modified_FLORDM000_data)
        response = self.client.put(url_for('main.put_instrument_deployment', id=999), headers=headers, data=data)
        self.assertEquals(response.status_code, 404)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Test data reference - do not delete
    '''
        curl -X GET http://localhost:4000/instrument_deployment?platform_deployment_id=203
        {
          "instrument_deployments": [
            {
              "depth": 1000.0,
              "display_name": "2-Wavelength Fluorometer",
              "end_date": null,
              "geo_location": null,
              "id": 754,
              "platform_deployment_id": 203,
              "reference_designator": "GS05MOAS-PG002-02-FLORDM000",
              "start_date": null
            },
            {
              "depth": 1000.0,
              "display_name": "Photosynthetically Available Radiation",
              "end_date": null,
              "geo_location": null,
              "id": 774,
              "platform_deployment_id": 203,
              "reference_designator": "GS05MOAS-PG002-04-PARADM000",
              "start_date": null
            },
            {
              "depth": 1000.0,
              "display_name": "Absorption Spectrophotometer",
              "end_date": null,
              "geo_location": null,
              "id": 686,
              "platform_deployment_id": 203,
              "reference_designator": "GS05MOAS-PG002-03-OPTAAM000",
              "start_date": null
            },
            {
              "depth": 1000.0,
              "display_name": "CTD Glider",
              "end_date": null,
              "geo_location": null,
              "id": 758,
              "platform_deployment_id": 203,
              "reference_designator": "GS05MOAS-PG002-01-CTDGVM000",
              "start_date": null
            }
          ]
        }
        '''



