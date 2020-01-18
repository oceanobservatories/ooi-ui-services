#!/usr/bin/env python


def get_help_data_12578():
    """
    Quality Control (QC) help.
    Data store of information to be presented when a help request is made for port 12578.
    Returns a list of dictionaries associated with various requests supported on that port.
    """
    help_data = [
                    {
                        'root': 'qcparameters',
                        'endpoint': 'qcparameters',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get a list of all QC parameters.',
                        'data_required': False,
                        'data_format': None,
                        'samples': [{
                                    'sample_request': 'qcparameters',
                                    'sample_response': [
                                            {
                                              "@class" : ".QCParameterRecord",
                                              "value" : "-3",
                                              "valueType" : "FLOAT",
                                              "qcParameterPK" : {
                                                "parameter" : "dat_min",
                                                "refDes" : {
                                                  "vocab" : {
                                                    "refdes" : "CE01ISSM-MFD35-01-VEL3DD000",
                                                    "instrument" : "3-D Single Point Velocity Meter",
                                                    "tocL1" : "Coastal Endurance",
                                                    "tocL2" : "Oregon Inshore Surface Mooring",
                                                    "tocL3" : "Seafloor Multi-Function Node (MFN)"
                                                  },
                                                  "node" : "MFD35",
                                                  "full" : True,
                                                  "sensor" : "01-VEL3DD000",
                                                  "subsite" : "CE01ISSM"
                                                },
                                                "streamParameter" : "vel3d_c_eastward_turbulent_velocity",
                                                "qcId" : "dataqc_globalrangetest_minmax"
                                              },
                                              "qcpId" : 1
                                            }]
                                    }]
                    },
                    {
                        'root': 'qcparameters',
                        'endpoint': 'qcparameters/{id}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get details of QC parameter with id provided.',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'id',
                                  'type': 'int',
                                  'description': 'The parameter identifier.',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
                        'samples': [{
                                    'sample_request': 'qcparameters/1',
                                    'sample_response': {
                                              "@class" : ".QCParameterRecord",
                                              "value" : "-3",
                                              "valueType" : "FLOAT",
                                              "qcParameterPK" : {
                                                "parameter" : "dat_min",
                                                "refDes" : {
                                                  "vocab" : {
                                                    "refdes" : "CE01ISSM-MFD35-01-VEL3DD000",
                                                    "instrument" : "3-D Single Point Velocity Meter",
                                                    "tocL1" : "Coastal Endurance",
                                                    "tocL2" : "Oregon Inshore Surface Mooring",
                                                    "tocL3" : "Seafloor Multi-Function Node (MFN)"
                                                  },
                                                  "node" : "MFD35",
                                                  "full" : True,
                                                  "sensor" : "01-VEL3DD000",
                                                  "subsite" : "CE01ISSM"
                                                },
                                                "streamParameter" : "vel3d_c_eastward_turbulent_velocity",
                                                "qcId" : "dataqc_globalrangetest_minmax"
                                              },
                                              "qcpId" : 1
                                            }
                                    }]
                    },
                    {
                        'root': 'qcparameters',
                        'endpoint': 'qcparameters/schema',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get the schema for a QC parameter.',
                        'data_required': False,
                        'data_format': None,
                        'samples': [{
                                    'sample_request': 'qcparameters/schema',
                                    'sample_response': [
                                            {
                                              "type" : "object",
                                              "properties" : {
                                                "value" : {
                                                  "type" : "string"
                                                },
                                                "valueType" : {
                                                  "type" : "string",
                                                  "enum" : [ "INT", "FLOAT", "STRING", "VECTOR", "LIST" ]
                                                },
                                                "qcParameterPK" : {
                                                  "type" : "object",
                                                  "properties" : {
                                                    "parameter" : {
                                                      "type" : "string"
                                                    },
                                                    "refDes" : {
                                                      "type" : "object",
                                                      "properties" : {
                                                        "vocab" : {
                                                          "type" : "object",
                                                          "properties" : {
                                                            "refdes" : {
                                                              "type" : "string"
                                                            },
                                                            "instrument" : {
                                                              "type" : "string"
                                                            },
                                                            "tocL1" : {
                                                              "type" : "string"
                                                            },
                                                            "tocL2" : {
                                                              "type" : "string"
                                                            },
                                                            "tocL3" : {
                                                              "type" : "string"
                                                            }
                                                          }
                                                        },
                                                        "node" : {
                                                          "type" : "string"
                                                        },
                                                        "full" : {
                                                          "type" : "boolean",
                                                          "required" : True
                                                        },
                                                        "sensor" : {
                                                          "type" : "string"
                                                        },
                                                        "subsite" : {
                                                          "type" : "string"
                                                        }
                                                      }
                                                    },
                                                    "streamParameter" : {
                                                      "type" : "string"
                                                    },
                                                    "qcId" : {
                                                      "type" : "string"
                                                    }
                                                  }
                                                },
                                                "qcpId" : {
                                                  "type" : "integer"
                                                },
                                                "@class" : {
                                                  "enum" : [ ".QCParameterRecord" ],
                                                  "required" : True
                                                }
                                              }
                                            }]
                                    }]
                    }
                ]
    return help_data
