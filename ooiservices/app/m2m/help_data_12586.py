#!/usr/bin/env python


def get_help_data_12586():
    """
    Vocabulary help.
    Data store of information to be presented when a help request is made for port 12586.
    Returns a list of dictionaries associated with various requests supported on that port.
    Sample response:
    [
        {
          "@class" : ".VocabRecord",
          "model" : "",
          "manufacturer" : "",
          "vocabId" : 1,
          "refdes" : "CE01ISSM",
          "instrument" : "",
          "tocL1" : "Coastal Endurance",
          "tocL2" : "Oregon Inshore Surface Mooring",
          "tocL3" : "",
          "mindepth" : 0.0,
          "maxdepth" : 25.0
        },
        {
          "@class" : ".VocabRecord",
          "model" : "",
          "manufacturer" : "",
          "vocabId" : 2,
          "refdes" : "CE01ISSM-MFC31",
          "instrument" : "",
          "tocL1" : "Coastal Endurance",
          "tocL2" : "Oregon Inshore Surface Mooring",
          "tocL3" : "Seafloor Multi-Function Node (MFN)",
          "mindepth" : 25.0,
          "maxdepth" : 25.0
        },
        . . .
    ]

    """
    help_data = [
            {
                'root': 'vocab',
                'endpoint': 'vocab',
                'method': 'GET',
                'permission_required': False,
                'description': 'Returns a list of dictionaries for OOI vocabulary. ' +
                               'An abbreviated response is provided below.',
                'data_required': False,
                'data_format': None,
                'sample_request': 'vocab',
                'sample_response':
                    [
                        {
                          "@class" : ".VocabRecord",
                          "model" : "",
                          "manufacturer" : "",
                          "vocabId" : 1,
                          "refdes" : "CE01ISSM",
                          "instrument" : "",
                          "tocL1" : "Coastal Endurance",
                          "tocL2" : "Oregon Inshore Surface Mooring",
                          "tocL3" : "",
                          "mindepth" : 0.0,
                          "maxdepth" : 25.0
                        },
                        {
                          "@class" : ".VocabRecord",
                          "model" : "",
                          "manufacturer" : "",
                          "vocabId" : 2,
                          "refdes" : "CE01ISSM-MFC31",
                          "instrument" : "",
                          "tocL1" : "Coastal Endurance",
                          "tocL2" : "Oregon Inshore Surface Mooring",
                          "tocL3" : "Seafloor Multi-Function Node (MFN)",
                          "mindepth" : 25.0,
                          "maxdepth" : 25.0
                        },

                    ]
            },
            {
                'root': 'vocab',
                'endpoint': 'vocab/inv',
                'method': 'GET',
                'permission_required': False,
                'description': 'Returns a list of all subsite entries in the vocabulary. ' +
                               'An abbreviated response is provided below.',
                'data_required': False,
                'data_format': None,
                'sample_request': 'vocab/inv',
                'sample_response':
                    ["CE01ISSM", "CE01ISSP", "CE02SHBP", "CE02SHSM", "CE02SHSP", "CE04OSBP"]
            },
            {
                'root': 'vocab',
                'endpoint': 'vocab/inv/{subsite}',
                'method': 'GET',
                'permission_required': True,
                'description': 'Returns a list of all nodes for the given subsite. ' +
                               'An abbreviated response is provided below.',
                'data_required': False,
                'data_format':
                            [
                                { 'name': 'subsite',
                                  'type': 'str',
                                  'description': 'The subsite entry whose nodes are to be returned.',
                                  'valid_values': None,
                                  'default': None
                                }
                            ],
                'sample_request': 'vocab/inv/CE01ISSM',
                'sample_response': ["MFC31", "MFD35", "MFD37", "RID16", "SBC11", "SBD17"]
            },
            {
                'root': 'vocab',
                'endpoint': 'vocab/inv/{subsite}/{node}',
                'method': 'GET',
                'permission_required': False,
                'description': 'Returns a list of all sensors for the given subsite and node. ' +
                               'An abbreviated response is provided below.',
                'data_required': True,
                'data_format':
                            [
                                { 'name': 'subsite',
                                  'type': 'str',
                                  'description': 'The subsite whose sensors are to be returned.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'node',
                                  'type': 'str',
                                  'description': 'The node whose sensors are to be returned.',
                                  'valid_values': None,
                                  'default': None
                                }
                            ],
                'sample_request': 'vocab/inv/CE01ISSM/MFC31',
                'sample_response': ["00-CPMENG000"]
            },
            {
                'root': 'vocab',
                'endpoint': 'vocab/inv/{subsite}/{node}/{sensor}',
                'method': 'GET',
                'permission_required': False,
                'description': 'Returns the single vocab record for a given subsite. node, and sensor' +
                               'An abbreviated response is provided below.',
                'data_required': True,
                'data_format':
                            [
                                { 'name': 'subsite',
                                  'type': 'str',
                                  'description': 'The subsite used to get the vocabulary record.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'node',
                                  'type': 'str',
                                  'description': 'The node used to get the vocabulary record.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'sensor',
                                  'type': 'str',
                                  'description': 'The sensor used to get the vocabulary record.',
                                  'valid_values': None,
                                  'default': None
                                }
                            ],
                'sample_request': 'vocab/inv/CE01ISSM/MFC31/00-CPMENG000',
                'sample_response': [{
                                      "@class" : ".VocabRecord",
                                      "model" : "Communications and Power Manager",
                                      "manufacturer" : "WHOI",
                                      "vocabId" : 3,
                                      "refdes" : "CE01ISSM-MFC31-00-CPMENG000",
                                      "instrument" : "Platform Controller",
                                      "tocL1" : "Coastal Endurance",
                                      "tocL2" : "Oregon Inshore Surface Mooring",
                                      "tocL3" : "Seafloor Multi-Function Node (MFN)",
                                      "mindepth" : 25.0,
                                      "maxdepth" : 25.0
                                    }]
            }
        ]
    return help_data
