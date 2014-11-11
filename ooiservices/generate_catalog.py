#!/usr/bin/env python

'''
ooiservices.manage

Manage script for specific services related tasks
'''

from flask.ext.script import Manager
from ooiservices import app
from ooiservices.util.erddap_catalog import ERDDAPCatalog, ERDDAPCatalogEntry
import os

manager = Manager(app)

def add_to_catalog(catalog_path, dataset_id, netcdf_file):
    '''
    Adds catalog entry to specificed catalog
    '''
    catalog = ERDDAPCatalog(catalog_path, 'r+')
    base_dir = os.path.dirname(netcdf_file)

    entry = ERDDAPCatalogEntry(dataset_id,base_dir, netcdf_file)
    with entry:
        entry.read_vars()

    catalog.add_entry(entry)

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('catalog_path', help='Path to the datasets.xml file')
    parser.add_argument('dataset_id', help='Unique ID for the dataset')
    parser.add_argument('netcdf_file', help='A sample netcdf file to parse for metadata')
    args = parser.parse_args()

    add_to_catalog(args.catalog_path, args.dataset_id, args.netcdf_file)

