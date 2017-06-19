#!/usr/bin/env python


def get_help_data_12587_status():
    """
    Asset Management help - Category 'status'
    Data store of information to be presented when a help request is made for port 12587.
    Returns a list of dictionaries associated with various requests supported on that port.
    """
    help_data = [
                    {
                        'root': 'status/query',
                        'endpoint': 'status/query',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get a list of all array status records.',
                        'data_required': False,
                        'data_format': None,
                        'samples': [{
                                    'sample_request': 'status/query',
                                    'sample_response': [
                                                            {
                                                              "referenceDesignator" : "RS",
                                                              "status" : {
                                                                "legend" : {
                                                                  "notTracked" : 0,
                                                                  "removedFromService" : 0,
                                                                  "degraded" : 2,
                                                                  "failed" : 1,
                                                                  "operational" : 8
                                                                },
                                                                "count" : 11
                                                              }
                                                            },
                                                            {
                                                              "referenceDesignator" : "CE",
                                                              "status" : {
                                                                "legend" : {
                                                                  "notTracked" : 0,
                                                                  "removedFromService" : 0,
                                                                  "degraded" : 1,
                                                                  "failed" : 0,
                                                                  "operational" : 2
                                                                },
                                                                "count" : 3
                                                              }
                                                            }]
                                    }]
                    },
                    {
                        'root': 'status/query',
                        'endpoint': 'status/query/{array}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get status information given an array identifier.',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'array',
                                  'type': 'str',
                                  'description': 'Array (two character) identifier. (i.e. \'RS\')',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
                        'samples': [{
                                    'sample_request': 'status/query/RS',
                                    'sample_response': [
                                                        {
                                                          "reason" : None,
                                                          "deployment" : 3,
                                                          "referenceDesignator" : "RS01SBPS",
                                                          "status" : "operational"
                                                        },
                                                        {
                                                          "reason" : None,
                                                          "deployment" : 3,
                                                          "referenceDesignator" : "RS01SBPS-PC01A",
                                                          "status" : "operational"
                                                        },
                                                        {
                                                          "reason" : None,
                                                          "deployment" : 3,
                                                          "referenceDesignator" : "RS01SLBS",
                                                          "status" : "degraded"
                                                        },
                                                        {
                                                          "reason" : None,
                                                          "deployment" : 3,
                                                          "referenceDesignator" : "RS01SLBS-LJ01A",
                                                          "status" : "degraded"
                                                        },
                                                        {
                                                          "reason" : None,
                                                          "deployment" : 2,
                                                          "referenceDesignator" : "RS01SUM1",
                                                          "status" : "operational"
                                                        }]
                                    }]
                    },
                    {
                        'root': 'status/query',
                        'endpoint': 'status/query/{subsite}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get status information given its full subsite identifier (subsite). ',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'subsite',
                                  'type': 'str',
                                  'description': 'The subsite identifier. (i.e. \'RS01SBPS\')',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
                        'samples': [{
                                    'sample_request': 'status/query/RS01SBPS',
                                    'sample_response': [
                                                        {
                                                          "reason" : None,
                                                          "deployment" : 3,
                                                          "referenceDesignator" : "RS01SBPS",
                                                          "status" : "operational"
                                                        },
                                                        {
                                                          "reason" : None,
                                                          "deployment" : 3,
                                                          "referenceDesignator" : "RS01SBPS-PC01A",
                                                          "status" : "operational"
                                                        }]
                                    }]
                    },
                    {
                        'root': 'status/query',
                        'endpoint': 'status/query/{subsite}/{node}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get status information by subsite and node identifiers provided.',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'subsite',
                                  'type': 'str',
                                  'description': 'The subsite identifier. (i.e. \'RS01SBPS\')',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'node',
                                  'type': 'str',
                                  'description': 'The node identifier. (i.e. \'PC01A\')',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
                        'samples': [{
                                    'sample_request': 'status/query/RS01SBPS/PC01A',
                                    'sample_response': [
                                                        {
                                                          "reason" : None,
                                                          "deployment" : 3,
                                                          "referenceDesignator" : "RS01SBPS-PC01A",
                                                          "status" : "operational"
                                                        },
                                                        {
                                                          "reason" : "Stream statuses: operational: 2, notTracked: 5",
                                                          "deployment" : 3,
                                                          "referenceDesignator" : "RS01SBPS-PC01A-05-ADCPTD102",
                                                          "status" : "operational"
                                                        },
                                                        {
                                                          "reason" : "Stream statuses: operational: 1, notTracked: 5",
                                                          "deployment" : 3,
                                                          "referenceDesignator" : "RS01SBPS-PC01A-4A-CTDPFA103",
                                                          "status" : "operational"
                                                        },
                                                        {
                                                          "reason" : "Stream statuses: operational: 1, notTracked: 2",
                                                          "deployment" : 3,
                                                          "referenceDesignator" : "RS01SBPS-PC01A-4B-PHSENA102",
                                                          "status" : "operational"
                                                        },
                                                        {
                                                          "reason" : "Stream statuses: operational: 1, notTracked: 1",
                                                          "deployment" : 3,
                                                          "referenceDesignator" : "RS01SBPS-PC01A-4C-FLORDD103",
                                                          "status" : "operational"
                                                        }]
                        }]
                    },
                    {
                        'root': 'status/query',
                        'endpoint': 'status/query/{subsite}/{node}/{sensor}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get status information by subsite, node and sensor identifiers provided.',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'subsite',
                                  'type': 'str',
                                  'description': 'The subsite identifier. (i.e. \'RS01SBPS\')',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'node',
                                  'type': 'str',
                                  'description': 'The node identifier. (i.e. \'PC01A\')',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'sensor',
                                  'type': 'str',
                                  'description': 'The sensor identifier. (i.e. \'4B-PHSENA102\')',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
                        'samples': [{
                                    'sample_request': 'status/query/RS01SBPS/PC01A/4B-PHSENA102',
                                    'sample_response': [
                                                        {
                                                          "reason" : "Stream statuses: operational: 1, notTracked: 2",
                                                          "deployment" : 3,
                                                          "referenceDesignator" : "RS01SBPS-PC01A-4B-PHSENA102",
                                                          "status" : "operational"
                                                        }]
                                    }]
                    }

        ]

    return help_data
