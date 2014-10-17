#!/usr/bin/env python
'''
tests.model.test_adaptor

The base class for the Services Test Case
'''

from ooiservices.model.adaptor import FileAdaptor
from tests.services_test_case import ServicesTestCase

import os
import shutil

class TestAdaptor(ServicesTestCase):
    '''
    Unit tests for the file adaptor
    '''

    def setUp(self):
        '''
        a place to put the docs
        '''
        ServicesTestCase.setUp(self)

        self.docs_dir = os.path.join(self.output_dir, 'docs')

        if not os.path.exists(self.docs_dir):
            os.makedirs(self.docs_dir)


    def test_basic_io(self):
        '''
        Tests the basic input output of the file adaptor
        '''
        adaptor = FileAdaptor(self.docs_dir)
        doc = {
            "name" : "Platform Example",
            "owner" : "owner_id",
            "lat" : 40,
            "lon" : -70
        }
        doc_id = adaptor.create(doc)
        assert os.path.exists(os.path.join(self.docs_dir, doc_id + '.json'))

        doc = adaptor.read(doc_id)
        assert 'id' in doc and doc_id == doc['id']

        doc['owner'] = 'WHOI'
        adaptor.update(doc)

        doc = None
        doc = adaptor.read(doc_id)
        assert doc['owner'] == 'WHOI'

        assert adaptor.delete(doc_id)
        assert not os.path.exists(os.path.join(self.docs_dir, doc_id + '.json'))

