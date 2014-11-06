#!/usr/bin/env python
'''
tests.util.test_erddap_catalog

Tests to validate the ERDDAP Catalog generation is correct and desired
'''

from tests.services_test_case import ServicesTestCase
from ooiservices.util.erddap_catalog import ERDDAPCatalog, ERDDAPCatalogEntry
import os
import time

class TestERDDAPCatalog(ServicesTestCase):

    def test_erddap_catalog(self):
        catalog_path = os.path.join(self.output_dir, 'catalog.xml')
        catalog = ERDDAPCatalog(catalog_path, 'w')

        entry = ERDDAPCatalogEntry('dataset_id', self.output_dir, 'tests/samples/optaa_dj_dcl_instrument_recovered__24344093-28e1-4e10-af0f-0bbffb278c71.nc')
        with entry:
            entry.read_vars()

        catalog.add_entry(entry)

        with open(catalog.catalog_path, 'r') as f:
            result = f.read()

        with open('tests/util/expected.xml') as f:
            expected = f.read()

        result += '\n' # ugh newlines

        assert result == expected

