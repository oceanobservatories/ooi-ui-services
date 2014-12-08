#!/usr/bin/env python

'''
ooiservices.manage

Manage script for specific services related tasks
'''

from flask.ext.script import Manager
from ooiservices import app
from ooiservices.util.erddap_catalog import ERDDAPCatalog, ERDDAPCatalogEntry
from ooiservices.config import DataSource
from ooiservices.model.instrument_deployment import InstrumentDeploymentModel
from ooiservices.model.platform_deployment import PlatformDeploymentModel
import sqlite3
import os
import re

manager = Manager(app)


class DatasetCrawler:

    def __init__(self, catalog_path, wipe_catalog=False):
        self.catalog_path = catalog_path
        if wipe_catalog and os.path.exists(self.catalog_path):
            os.remove(self.catalog_path)

        self.instrument_deployments = InstrumentDeploymentModel()
        self.platform_deployments = PlatformDeploymentModel()


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
            if re.match(r'[0-9]{2}[-_][A-Z0-9]{9}', directory):
                self.crawl_instrument_directory(os.path.join(platform_directory, directory))

    def crawl_instrument_directory(self, instrument_directory):
        '''
        Generates the catalog by looking at the netcdf file
        '''
        if not os.path.exists(instrument_directory):
            raise IOError("Instrument directory path %s does not exist" % instrument_directory)

        for directory in os.listdir(instrument_directory):
            if os.path.isdir(os.path.join(instrument_directory, directory)):
                self.crawl_stream_directory(os.path.join(instrument_directory, directory))
    
    def crawl_stream_directory(self, stream_directory):
        '''
        Generates the catalog by looking at the netcdf file
        '''
        if not os.path.exists(stream_directory):
            raise IOError("Stream directory path %s does not exist" % stream_directory)

        for directory in os.listdir(stream_directory):
            if os.path.isdir(os.path.join(stream_directory, directory)):
                self.crawl_file_directory(os.path.join(stream_directory, directory))

    def crawl_file_directory(self, file_directory):
        '''

        '''
        if not os.path.exists(file_directory):
            raise IOError("File directory path %s does not exist" % file_directory)


        for netcdf_file in os.listdir(file_directory):

            if netcdf_file.endswith('.nc'):
                self.add_to_catalog(os.path.join(file_directory, netcdf_file))
                break

    def get_dataset_title(self, reference_designator):
        '''
        Returns the approved vocabulary title given a reference designator
        '''
        docs = self.instrument_deployments.read({'reference_designator' : reference_designator})
        if not docs:
            return None

        platform_title = self.get_platorm_title(reference_designator[:14])
        display_name = docs[0]['display_name']
        if platform_title:
            display_name = platform_title + ' ' + display_name
        return display_name

    def get_platorm_title(self, platform_designator):
        '''
        Returns the proper display name given a platform reference designator
        '''
        docs = self.platform_deployments.read({'reference_designator' : platform_designator})
        if not docs:
            return None
        display_name = docs[0]['display_name']
        return display_name

    def add_to_catalog(self, netcdf_file):
        '''
        Adds catalog entry to specificed catalog
        '''
        catalog = ERDDAPCatalog(self.catalog_path, 'r+')
        base_dir = os.path.dirname(netcdf_file)

        path_tree = netcdf_file.split('/')
        processed_prefix = path_tree[-2]
        stream_name = path_tree[-3]
        instrument = path_tree[-4]
        platform = path_tree[-5]


        ref_des = '_'.join([platform, instrument])

        dataset_id = '_'.join([ref_des, stream_name, processed_prefix])
        dataset_id = re.sub(r'-', '_', dataset_id)
        dataset_title = self.get_dataset_title(re.sub(r'_', '-', ref_des)) or ref_des
        dataset_title = dataset_title + ' ' + stream_name

        entry = ERDDAPCatalogEntry(dataset_id, dataset_title, base_dir, netcdf_file)
        with entry:
            entry.read_vars()

        catalog.add_entry(entry)
        app.logger.info("Created dataset entry for %s", dataset_id)

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('catalog_path', help='Path to the datasets.xml file')
    parser.add_argument('datasets_root', help='Datasets root')
    parser.add_argument('-w', '--wipe', action='store_true', help='Remove the existing datasets.xml')
    args = parser.parse_args()

    from ooiservices import app
    with app.app_context():
        dc = DatasetCrawler(args.catalog_path, args.wipe)
        dc.crawl_datasets(args.datasets_root)

