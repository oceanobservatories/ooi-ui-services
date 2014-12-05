#!/usr/bin/env python
'''
ooiservices.util.erddap_catalog

Utilities to generate an ERDDAP datasets.xml entry from a NetCDF file
'''

from netCDF4 import Dataset
from jinja2 import Environment, FileSystemLoader

import pkg_resources
import os
import lxml.etree as etree
import numpy as np

class ERDDAPCatalog:
    '''
    ERDDAP Catalog Generation

    Example:
      catalog = ERDDAPCatalog(catalog_path, 'w')
      entry = ERDDAPCatalogEntry('dataset_id', self.output_dir, netcdf_file)
    '''

    def __init__(self, catalog_path, mode='r'):
        self.catalog_path = catalog_path
        self.mode = mode

        # Get the path to the templates folder relative to this package 
        template_path = pkg_resources.resource_filename(__name__, 'templates')
        self.jenv = Environment(loader=FileSystemLoader(template_path), trim_blocks=True, lstrip_blocks=True)

    def add_entry(self, erddap_catalog_entry):
        '''
        Adds a new dataset entry to the catalog
        '''
        self.check_new_catalog()

        # Parse the existing catalog
        with open(self.catalog_path, 'r') as f:
            tree = etree.parse(f)
            root = tree.getroot()


        # Read the new entry in
        entry_xml = erddap_catalog_entry.render_template()
        entry = etree.fromstring(entry_xml)
        root.append(entry)
        xml_buffer = etree.tostring(tree, xml_declaration=True, encoding='utf-8')

        if self.mode in ('r+', 'a', 'w'):
            with open(self.catalog_path, 'w') as f:
                f.write(xml_buffer)
        else:
            raise IOError('File not open for writing')

    def check_new_catalog(self):
        '''
        Creates the baseline template for the datasets.xml catalog if the mode
        is 'w' or if the file doesn't exist
        '''
        if self.mode == 'w':  
            self.create_catalog()
        elif self.mode in ['r+', 'a']:
            # if the file doesn't exist create it
            if not os.path.exists(self.catalog_path):
                self.create_catalog()

    def create_catalog(self):
        '''
        Writes the basline catalog to the file
        '''
        # Truncate the file and create the baseline catalog
        template = self.jenv.get_template('datasets.xml.j2')
        buf = template.render()
        with open(self.catalog_path, 'w') as f:
            f.write(buf)



class ERDDAPCatalogEntry:
    dataset_id  = '' # Unique ID for this dataset on ERDDAP
    dataset_dir = '' # Directory where the netcdf file(s) are located
    data_vars   = {} # name, type value pairs

    def __init__(self, dataset_id, dataset_title, dataset_dir, netcdf_file):
        '''
        Initializes the catalog entry to the specified attributes and opens the
        netcdf file
        '''
        self.dataset_id = dataset_id
        self.dataset_dir = dataset_dir
        self.dataset_title = dataset_title
        # Load the netcdf file
        self.nc = Dataset(netcdf_file, 'r')
        self.data_vars = {}
        # Get the path to the templates folder relative to this package 
        template_path = pkg_resources.resource_filename(__name__, 'templates')
        self.jenv = Environment(loader=FileSystemLoader(template_path), trim_blocks=True, lstrip_blocks=True)

    def map_type(self, dtype):
        '''
        Returns the ERDDAP data type for a given dtype
        '''
        dtype_map = {
            np.dtype('float64') : 'double',
            np.dtype('float32') : 'float',
            np.dtype('int64')   : 'long',
            np.dtype('int32')   : 'int',
            np.dtype('int16')   : 'short',
            np.dtype('int8')    : 'byte',
            np.dtype('uint64')  : 'unsignedLong',
            np.dtype('uint32')  : 'unsignedInt',
            np.dtype('uint16')  : 'unsignedShort',
            np.dtype('uint8')   : 'unsignedByte',
            np.dtype('bool')    : 'boolean',
            np.dtype('S')       : 'String'
        }
        if dtype.char == 'S':
            return 'String'

        return dtype_map[dtype]

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        '''
        Closes the file descriptors
        '''
        self.nc.close()

    def read_vars(self):
        '''
        Reads the variables from the dataset and populates self.data_vars

        This is necessary to produce the proper template
        '''
        for nc_var in self.nc.variables:
            data_type = self.map_type(self.nc.variables[nc_var].dtype)
            self.data_vars[nc_var] = data_type
    
    def render_template(self):
        '''
        Returns the XML for the dataset entry in ERDDAP's datasets.xml
        '''
        template = self.jenv.get_template('dataset_entry.xml.j2')
        return template.render(dataset_title=self.dataset_title,
                               dataset_id=self.dataset_id, 
                               dataset_dir=self.dataset_dir, 
                               data_vars=self.data_vars)


