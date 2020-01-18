#!/usr/bin/env python


def get_help_data_12575():
    """
    Sensor Inventory help.
    Data store of information to be presented when a help request is made for port 12576.
    Returns a list of dictionaries associated with various requests supported on that port.
    """
    help_data = [
                    {
                        'root': 'parameter',
                        'endpoint': 'parameter/{id}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Retrieve information for a Preload Parameter given its identifier.',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'id',
                                  'type': 'int',
                                  'description': 'The Parameter identifier.',
                                  'valid_values': None,
                                  'default': None
                                }],
                        'samples': [{
                                    'sample_request': 'parameter/100',
                                    'sample_response': {
                                          "name" : "ass_sig_wave_period",
                                          "display_name" : "Auto-Spectrum Statistics - Significant Wave Period",
                                          "standard_name" : None,
                                          "description" : None,
                                          "id" : 100,
                                          "data_product_identifier" : None,
                                          "precision" : 4,
                                          "fill_value" : {
                                            "value" : "-9999999"
                                          },
                                          "unit" : {
                                            "value" : "s"
                                          },
                                          "data_level" : None,
                                          "code_set" : None,
                                          "value_encoding" : {
                                            "value" : "float32"
                                          },
                                          "parameter_type" : {
                                            "value" : "quantity"
                                          },
                                          "parameter_function" : None,
                                          "data_product_type" : None,
                                          "dimensions" : [ ],
                                          "parameter_function_map" : None
                                        }
                                    }]
                    },
                    {
                        'root': 'stream',
                        'endpoint': 'stream/{id}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Retrieve information for a Preload Stream given its identifier. ' +
                                       'The sample has an abbreviated set of parameters displayed.',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'id',
                                  'type': 'int',
                                  'description': 'The Stream identifier.',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
                        'samples': [{
                                    'sample_request': 'stream/506',
                                    'sample_response': {
                                              "name" : "cg_cpm_eng_cpm",
                                              "id" : 506,
                                              "time_parameter" : 7,
                                              "binsize_minutes" : 20160,
                                              "stream_type" : {
                                                "value" : "Engineering"
                                              },
                                              "stream_content" : {
                                                "value" : "CPM Controller Status Data"
                                              },
                                              "description" : None,
                                              "parameters" : [ {
                                                                "name" : "time",
                                                                "display_name" : "Time, UTC",
                                                                "standard_name" : "time",
                                                                "description" : "Time, UTC",
                                                                "id" : 7,
                                                                "data_product_identifier" : None,
                                                                "precision" : 0,
                                                                "fill_value" : {
                                                                  "value" : "-9999999"
                                                                },
                                                                "unit" : {
                                                                  "value" : "seconds since 1900-01-01"
                                                                },
                                                                "data_level" : None,
                                                                "code_set" : None,
                                                                "value_encoding" : {
                                                                  "value" : "float64"
                                                                },
                                                                "parameter_type" : {
                                                                  "value" : "quantity"
                                                                },
                                                                "parameter_function" : None,
                                                                "data_product_type" : None,
                                                                "dimensions" : [ ],
                                                                "parameter_function_map" : None
                                                              }],
                                              "dependencies" : [ ]
                                            }
                                    }]
                    },
                    {
                        'root': 'stream',
                        'endpoint': 'stream/byname/{name}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Retrieve information for a Preload Stream given its name. ' +
                                       'The sample has an abbreviated set of parameters displayed.',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'name',
                                  'type': 'str',
                                  'description': 'Preload Stream name.',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
                        'samples': [{
                                'sample_request': 'stream/byname/cg_cpm_eng_cpm',
                                'sample_response': {
                                                      "name" : "cg_cpm_eng_cpm",
                                                      "id" : 506,
                                                      "time_parameter" : 7,
                                                      "binsize_minutes" : 20160,
                                                      "stream_type" : {
                                                        "value" : "Engineering"
                                                      },
                                                      "stream_content" : {
                                                        "value" : "CPM Controller Status Data"
                                                      },
                                                      "description" : None,
                                                      "parameters" : [ {
                                                                        "name" : "time",
                                                                        "display_name" : "Time, UTC",
                                                                        "standard_name" : "time",
                                                                        "description" : "Time, UTC",
                                                                        "id" : 7,
                                                                        "data_product_identifier" : None,
                                                                        "precision" : 0,
                                                                        "fill_value" : {
                                                                          "value" : "-9999999"
                                                                        },
                                                                        "unit" : {
                                                                          "value" : "seconds since 1900-01-01"
                                                                        },
                                                                        "data_level" : None,
                                                                        "code_set" : None,
                                                                        "value_encoding" : {
                                                                          "value" : "float64"
                                                                        },
                                                                        "parameter_type" : {
                                                                          "value" : "quantity"
                                                                        },
                                                                        "parameter_function" : None,
                                                                        "data_product_type" : None,
                                                                        "dimensions" : [ ],
                                                                        "parameter_function_map" : None
                                                                      }],
                                                      "dependencies" : [ ]
                                                    }
                                    }]
                    }

                ]
    return help_data
