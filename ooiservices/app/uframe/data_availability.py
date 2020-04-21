
"""
Data Availability routes.

Routes:

[GET]  /da/<string:rd>/<string:params>     # Get data availability for reference designator and optional params
"""
__author__ = 'Edna Donoughe'

from flask import jsonify, current_app
from ooiservices.app.main.errors import bad_request
from ooiservices.app.uframe import uframe as api
from ooiservices.app.uframe.uframe_tools import uframe_get_da_by_rd


# Get data availability for reference designator.
@api.route('/available/<string:rd>', methods=['GET'])
def get_da_by_rd(rd):
    """ Get data availability for an instrument reference designator.
    Sample request: http://localhost:4000/uframe/da/CE02SHBP-LJ01D-06-CTDBPN106
    Sample response:
    {u'availability':
                    [
                        {
                            u'data': [
                                    [u'2014-04-17 20:45:00', u'Deployment: 1', u'2014-08-16 22:30:00'],
                                    [u'2014-10-10 17:45:00', u'Deployment: 2', u'2015-04-12 00:30:00'],
                                    [u'2015-06-03 17:15:00', u'Deployment: 3', u'2015-10-07 00:00:00'],
                                    [u'2015-10-08 12:02:00', u'Deployment: 4', u'2016-05-10 15:22:00'],
                                    [u'2016-05-18 15:44:00', u'Deployment: 5', u'2016-10-02 20:15:00'],
                                    [u'2016-09-30 16:45:00', u'Deployment: 6', u'2017-04-17 19:45:00'],
                                    [u'2017-04-19 04:18:00', u'Deployment: 7', u'2017-08-16 15:20:48']],
                            u'categories': {
                                        u'Deployment: 1': {u'color': u'#0073cf'},
                                        u'Deployment: 2': {u'color': u'#cf5c00'},
                                        u'Deployment: 3': {u'color': u'#0073cf'},
                                        u'Deployment: 4': {u'color': u'#cf5c00'},
                                        u'Deployment: 5': {u'color': u'#0073cf'},
                                        u'Deployment: 6': {u'color': u'#cf5c00'},
                                        u'Deployment: 7': {u'color': u'#0073cf'}},
                            u'measure': u'Deployments'
                        },
                        {   u'data': [
                                    [u'2014-04-17 20:45:00', u'Missing', u'2014-08-16 22:30:00'],
                                    [u'2014-10-10 17:45:00', u'Missing', u'2015-04-12 00:30:00'],
                                    [u'2015-06-03 17:15:00', u'Missing', u'2015-10-07 00:00:00'],
                                    [u'2015-10-08 12:02:00', u'Missing', u'2016-05-10 15:22:00'],
                                    [u'2016-05-18 15:44:00', u'Missing', u'2016-09-30 18:30:11'],
                                    [u'2016-09-30 18:30:11', u'Present', u'2016-10-02 20:15:00'],
                                    [u'2016-09-30 16:45:00', u'Missing', u'2016-09-30 18:30:11'],
                                    [u'2016-09-30 18:30:11', u'Present', u'2016-10-13 03:32:56'],
                                    [u'2016-10-13 03:32:56', u'Missing', u'2016-10-16 06:28:02'],
                                    [u'2016-10-16 06:28:02', u'Present', u'2017-01-03 18:30:10'],
                                    [u'2017-01-03 18:30:10', u'Missing', u'2017-01-05 18:28:01'],
                                    [u'2017-01-05 18:28:01', u'Present', u'2017-01-19 09:30:10'],
                                    [u'2017-01-19 09:30:10', u'Missing', u'2017-04-17 19:45:00'],
                                    [u'2017-04-19 04:18:00', u'Missing', u'2016-09-30 18:30:11'],
                                    [u'2017-04-19 04:18:00', u'Present', u'2016-10-13 03:32:56'],
                                    [u'2017-04-19 04:18:00', u'Missing', u'2016-10-16 06:28:02'],
                                    [u'2017-04-19 04:18:00', u'Present', u'2017-01-03 18:30:10'],
                                    [u'2017-04-19 04:18:00', u'Missing', u'2017-01-05 18:28:01'],
                                    [u'2017-04-19 04:18:00', u'Present', u'2017-01-19 09:30:10'],
                                    [u'2017-04-19 04:18:00', u'Missing', u'2017-04-19 06:30:08'],
                                    [u'2017-04-19 06:30:08', u'Present', u'2017-08-15 12:33:55'],
                                    [u'2017-08-15 12:33:55', u'Missing', u'2017-08-16 15:20:48']],
                            u'categories': {
                                    u'Not Expected': {u'color': u'#ffffff'},
                                    u'Present': {u'color': u'#5cb85c'},
                                    u'Missing': {u'color': u'#d9534d'}},
                            u'measure': u'telemetered mopak_o_dcl_accel'
                        }
                    ]
    }
    """
    try:

        from ooiservices.app.uframe.stream_tools import get_stream_name_byname
        debug = False

        if debug: print '\n debug -- Entered get_da_by_rd...'
        # Get data availability for reference designator and optional params.
        da = uframe_get_da_by_rd(rd, None)
        if 'availability' in da:
            if not da['availability']:
                if debug: print '\n debug -- Nothing returned for availability, return...'
                return jsonify(da), 401

        # Post process color selections.
        present_color = u'#0073cf'  # blue, used for Deployments.
        light_grey = u"#D3D3D3"     # used for streams which are missing. dark_grey = u"A9A9A9"
        data = da['availability']
        if data:
            for line in data:

                # Get categories.
                categories = line['categories']

                # Determine type of time line and process colors in categories.
                if 'measure' in line:
                    # If Deployments - set all color to be the same.
                    if line['measure'] == 'Deployments':
                        for k,v in categories.iteritems():
                            categories[k][u"color"] = present_color
                    # Else if streams, set Missing to be a light grey color.
                    else:
                        for k,v in categories.iteritems():
                            if k == 'Missing':
                                categories[k][u"color"] = light_grey

            # 12858 English labels for stream names in time lines.
            if debug: print '\n debug -- post processing stream names...'
            for item in data:
                if 'measure' in item:
                    if item['measure'] == 'Deployments':
                        continue
                    combo_stream_name = item['measure']
                    method, stream = combo_stream_name.rsplit(' ', 1)
                    if debug:
                        print '\n debug -- combo_stream_name: ', combo_stream_name
                        print '\n\t debug -- method: ', method
                        print '\n\t debug -- stream: ', stream
                    display_name = get_stream_name_byname(stream)[0]
                    if not display_name or display_name is None:
                        display_name = stream
                    if debug: print '\n debug -- display_name: ', display_name
                    item['measure'] = method + ' - ' + display_name

        return jsonify(da)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)
