#!/usr/bin/env python

'''
ooiservices.manage

Manage script for specific services related tasks
'''

from flask.ext.script import Manager
from ooiservices import app
from ooiservices.util.erddap_catalog import ERDDAPCatalog, ERDDAPCatalogEntry
import os
import re

manager = Manager(app)


class DatasetCrawler:

    def __init__(self, catalog_path, wipe_catalog=False):
        self.catalog_path = catalog_path
        if wipe_catalog and os.path.exists(self.catalog_path):
            os.remove(self.catalog_path)

    def crawl_datasets(self, dataset_root_path):
        '''
        Iterates over the directory sturcture and pulls out the necessary datasets
        and metadata.
        '''
        if not os.path.exists(dataset_root_path):
            raise IOError("Dataset root path %s does not exist" % dataset_root_path)

        for directory in os.listdir(dataset_root_path):
            if re.match(r'[A-Z0-9]{8}[-_][A-Z0-9]{5}', directory):
                # this is a valid platform
                self.crawl_platform_directory(os.path.join(dataset_root_path, directory))

    def crawl_platform_directory(self, platform_directory):
        '''
        Crawls the platform directory structure
        '''
        if not os.path.exists(platform_directory):
            raise IOError("Platform directory path %s does not exist" % platform_directory)

        for directory in os.listdir(platform_directory):
            if re.match(r'[A-Z0-9]{9}', directory):
                self.generate_catalog(os.path.join(platform_directory, directory))

    def generate_catalog(self, instrument_directory):
        '''
        Generates the catalog by looking at the netcdf file
        '''
        if not os.path.exists(instrument_directory):
            raise IOError("Platform directory path %s does not exist" % instrument_directory)

        for file_path in os.listdir(instrument_directory):
            if file_path.endswith('.nc'):
                self.add_to_catalog(os.path.join(instrument_directory, file_path))
                # We want to break early so we only look at one file
                # ERDDAP takes care of the rest

                break

    def add_to_catalog(self, netcdf_file):
        '''
        Adds catalog entry to specificed catalog
        '''
        catalog = ERDDAPCatalog(self.catalog_path, 'r+')
        base_dir = os.path.dirname(netcdf_file)

        path_tree = netcdf_file.split('/')
        instrument = path_tree[-2]
        platform = path_tree[-3]


        ref_des = '_'.join([platform, instrument])
        stream_name = path_tree[-1].split('__')[0]

        dataset_id = '_'.join([ref_des, stream_name])
        dataset_id = re.sub(r'-', '_', dataset_id)

        entry = ERDDAPCatalogEntry(dataset_id, base_dir, netcdf_file)
        with entry:
            entry.read_vars()

        catalog.add_entry(entry)
        app.logger.info("Created dataset entry for %s", dataset_id)

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('catalog_path', help='Path to the datasets.xml file')
    parser.add_argument('netcdf_file', help='A sample netcdf file to parse for metadata')
    args = parser.parse_args()

    add_to_catalog(args.catalog_path, args.netcdf_file)

