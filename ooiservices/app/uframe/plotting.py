#!/usr/bin/env python
'''
    ooiservices/app/main/plotting.py
    Support for generating svg plots
    '''
from flask import request
from netCDF4 import num2date
from ooiservices.app.uframe.plot_tools import OOIPlots
from ooiservices.app.uframe.stream_tools import get_parameter_name_by_parameter_stream
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import numpy as np
import prettyplotlib as ppl
from flask import current_app
from datetime import datetime

__author__ = 'Andy Bird'

# Define the matplotlib style sheet and some colors from that style
plt.style.use('bmh')
colors = plt.rcParams['axes.color_cycle']

# Instantiate the OOIPlots class
ooi_plots = OOIPlots()


def generate_plot(data, plot_options):
    debug = False
    # Define some fonts
    title_font = {
        'fontname': 'Calibri',
        'size': '14',
        'color': 'black',
        'weight': 'bold'
    }

    axis_font = {
        'fontname': 'Calibri',
        'size': '12',
        'weight': 'bold'
    }

    tick_font = {
        'axis': 'both',
        'labelsize': 8,
        'width': 1,
        'color': 'k'
    }

    # Get all the plot options
    plot_format = plot_options['plot_format']
    plot_layout = plot_options['plot_layout']
    plot_profile_id = plot_options['profileid']
    events = plot_options['events']
    width_in = plot_options['width_in']
    use_scatter = plot_options['use_scatter']
    plot_qaqc = plot_options['use_qaqc']
    reference_designator = plot_options['rd']
    if debug:
        print '\n debug -- use_scatter: ', use_scatter
        print '\n debug -- plot_qaqc: ', plot_qaqc
        print '\n debug -- rd: ', reference_designator

    # Generate the plot figure and axes
    is_timeseries = False
    if isinstance(data, dict):
        width = data['width']
        height = data['height']

        if "time" == data['x_field'][0]:
            data['x']['time'] = num2date(data['x']['time'], units='seconds since 1900-01-01 00:00:00', calendar='gregorian')
            is_timeseries = True
    else:
        width = data[0]['width']
        height = data[0]['height']
        for idx, dataset in enumerate(data):
            if "time" == dataset['x_field'][0]:
                data[idx]['x']['time'] = num2date(data[idx]['x']['time'], units='seconds since 1900-01-01 00:00:00', calendar='gregorian')

    fig, ax = ppl.subplots(1, 1, figsize=(width, height))

    # Calculate the hypotenuse to determine appropriate font sizes
    hypot = np.sqrt(width**2 + height**2) - 4
    tick_font['labelsize'] = int(hypot)
    axis_font['size'] = int(hypot) + 3
    title_font['size'] = int(hypot) + 5

    # Check the plot type and generate the plot!
    if plot_layout == "timeseries":
        """
        Plot time series data
        """
        if debug: print '\n-- Plotting Time Series'

        # Define some plot parameters
        kwargs = dict(linewidth=1.5,
                      alpha=0.7,
                      linestyle='None',
                      marker=".",
                      markersize=10,
                      markeredgecolor='k')

        # First check if we have a multiple stream data
        if isinstance(data, list):
            if debug: print '\n-- Plotting Multiple Streams'
            ooi_plots.plot_multiple_streams(fig, ax, data, colors,
                                            title_font=title_font,
                                            axis_font=axis_font,
                                            tick_font=tick_font,
                                            width_in = width_in,
                                            plot_qaqc=plot_qaqc,
                                            **kwargs)

        # Check for a single time series plot
        elif len(data['x_field']) == 1 and len(data['y_field']) == 1:
            if debug: print '\n debug -- Check for a single time series plot...'
            xlabel = data['x_field'][0]
            ylabel = data['y_field'][0]
            x = data['x'][xlabel]
            y = data['y'][ylabel]

            # QAQC logic
            if debug:
                if plot_qaqc > 0:
                    if debug: print '\n debug -- Processing qaqc...', plot_qaqc
            if plot_qaqc >= 10:
                # Plot all of the qaqc flags results
                qaqc_data = data['qaqc'][ylabel]

            elif plot_qaqc >= 1:
                # This is a case where the user wants to plot just one of the 9 QAQC tests
                ind = np.where(data['qaqc'][ylabel] != plot_qaqc)
                data['qaqc'][ylabel][ind] = 0
                qaqc_data = data['qaqc'][ylabel]
            else:
                qaqc_data = []

            ooi_plots.plot_time_series(fig, is_timeseries, ax, x, y,
                                       title=data['title'],
                                       xlabel=xlabel,
                                       ylabel=ylabel + " (" + data['y_units'][0] + ")",
                                       title_font=title_font,
                                       axis_font=axis_font,
                                       tick_font=tick_font,
                                       scatter=use_scatter,
                                       events=events,
                                       qaqc=qaqc_data,
                                       **kwargs)

        # Must be a multiple y axes plot, single stream
        else:
            xdata = {}
            xdata['time'] = data['x']['time']
            ydata = data['y']
            units = data['y_units']
            for ind, key in enumerate(ydata):
                xdata[key] = data['x']['time']
                # QAQC logic
                if plot_qaqc >= 10:
                    # Plot all of the qaqc flags results
                    pass
                elif plot_qaqc >= 1:
                    # This is a case where the user wants to plot just one of the 9 QAQC tests
                    ind = np.where(data['qaqc'][key] != plot_qaqc)
                    data['qaqc'][key][ind] = 0
                else:
                    data['qaqc'][key] = []

            ooi_plots.plot_multiple_yaxes(fig, ax,
                                          xdata,
                                          ydata,
                                          colors,
                                          title=data['title'],
                                          units=units,
                                          axis_font=axis_font,
                                          title_font=title_font,
                                          tick_font=tick_font,
                                          scatter = use_scatter,
                                          width_in = width_in,
                                          qaqc=data['qaqc'],
                                          **kwargs)

    elif plot_layout == "depthprofile":
        """
        Plot depth profiles (overlay)
        """
        if debug: print '\n-- Plotting Depth Profile'

        # Define some plot parameters
        kwargs = dict(linewidth=1.5, alpha=0.7)
        xlabel = data['x_field'] + " (" + request.args.get('x_units') + ")"
        ylabel = data['y_field'] + " (" + request.args.get('y_units') + ")"

        if plot_profile_id is None:

            for profile_id in range(0, np.shape(data['x'])[0]):
                # Remove the bad data
                qaqc_data = data['qaqc'][data['x_field']]

                ooi_plots.plot_profile(fig,
                                       ax,
                                       data['x'][profile_id],
                                       data['y'][profile_id],
                                       xlabel=xlabel,
                                       ylabel=ylabel,
                                       axis_font=axis_font,
                                       tick_font=tick_font,
                                       scatter=use_scatter,
                                       **kwargs)
        else:
            if int(plot_profile_id) < int(np.shape(data['x'])[0]):
                # get the profile selected
                ooi_plots.plot_profile(fig,
                                       ax,
                                       data['x'][int(plot_profile_id)],
                                       data['y'][int(plot_profile_id)],
                                       xlabel=xlabel,
                                       ylabel=ylabel,
                                       axis_font=axis_font,
                                       tick_font=tick_font,
                                       scatter=use_scatter,
                                       **kwargs)
            else:
                # return something
                ooi_plots.plot_profile(fig,
                                       ax,
                                       data['x'][0],
                                       data['y'][0],
                                       xlabel=xlabel,
                                       ylabel=ylabel,
                                       axis_font=axis_font,
                                       tick_font=tick_font,
                                       scatter=use_scatter,
                                       **kwargs)
        plt.gca().invert_yaxis()

    elif plot_layout == 'ts_diagram':
        """
        Plot a Temperature-Salinity diagram
        """
        if debug: print '\n-- Plotting T-S Diagram'

        # Define some plot parameters
        kwargs = dict(color='r', marker='o')

        # This should be used with 'real' data only (NO COUNTS!!)
        x = data['y'][data['y_field'][0]]
        y = data['y'][data['y_field'][1]]
        xlabel = data['y_field'][0] + " (" + data['y_units'][0] + ")"
        ylabel = data['y_field'][1] + " (" + data['y_units'][1] + ")"

        # # Mask the bad data
        # qaqc_x = data['qaqc'][data['y_field'][0]] < 1
        # qaqc_y = data['qaqc'][data['y_field'][1]] < 1
        # mask = qaqc_x & qaqc_y

        # x = x[mask]
        # y = x[mask]

        # if len(x) <= 0:
        #     raise(Exception('No good data avaliable!'))

        ooi_plots.plot_ts_diagram(ax, x, y,
                                  title=data['title'],
                                  xlabel=xlabel,
                                  ylabel=ylabel,
                                  title_font=title_font,
                                  axis_font=axis_font,
                                  tick_font=tick_font,
                                  **kwargs)

    elif plot_layout == 'quiver':
        """
        Plot magnitude and direction as a time series on a quiver plot
        """
        if debug: print '\n-- Plotting Quiver'

        # color='#0000FF',
        # edgecolors='#000000',
        kwargs = dict(units='y',
                      scale_units='y',
                      scale=1,
                      headlength=1.0,
                      headaxislength=1.0,
                      width=0.002,
                      alpha=0.5)

        time = mdates.date2num(data['x']['time'])
        start = plot_options['st_date']
        end = plot_options['ed_date']

        start_dt = mdates.date2num(datetime.strptime(start.split('.')[0], '%Y-%m-%dT%H:%M:%S'))
        end_dt = mdates.date2num(datetime.strptime(end.split('.')[0], '%Y-%m-%dT%H:%M:%S'))

        u = np.array(data['y'][data['y_field'][0]])
        v = np.array(data['y'][data['y_field'][1]])
        ylabel = "Velocity" + " (" + data['y_units'][0] + ")"

        # # Mask the bad data
        # qaqc_u = data['qaqc'][data['y_field'][0]] < 1
        # qaqc_v = data['qaqc'][data['y_field'][1]] < 1
        # mask = qaqc_u & qaqc_v
        # u = u[mask]
        # v = v[mask]
        # time = time[mask]
        # if len(u) <= 0:
        #     raise(Exception('No good data available.'))

        ooi_plots.plot_1d_quiver(fig, ax, time, u, v,
                                 title=data['title'],
                                 ylabel=ylabel,
                                 tick_font=tick_font,
                                 title_font=title_font,
                                 axis_font=axis_font,
                                 start=start_dt,
                                 end=end_dt,
                                 key_units=data['y_units'][0],
                                 **kwargs)

    elif plot_layout == 'stacked':
        """
        Plot colored stacked time series

        data.keys(): ['x_field', 'height', 'qaqc', 'y_units', 'y_field', 'dt_units', 'stream_name',
                      'title', 'data_length', 'width', 'x_units', 'y', 'x']

        sample: http://server:5000/data_access/#GI01SUMO-RII11-02-ADCPSN010/telemetered_adcps-jln-stc-instrument
        """
        _debug = False
        if _debug:
            print '\n-- Plotting  Stacked'
            print '\n-- Plotting  Stacked - reference designator: ', reference_designator
        #- - - - - - - - - - - - - - - - - - -
        # Get labels using preload information (default to system parameter name and units)
        #- - - - - - - - - - - - - - - - - - -
        if 'stream_name' in data:
            if data['stream_name'] is None or not data['stream_name']:
                label = data['y_field'][0] + " (" + data['y_units'][0] + ")"
            else:
                label = get_parameter_name_by_parameter_stream(data['y_field'][0], data['stream_name'])
            if label is None:
                label = data['y_field'][0] + " (" + data['y_units'][0] + ")"
        else:
            # If no stream_name, default to system parameter name and units
            label = data['y_field'][0] + " (" + data['y_units'][0] + ")"
        if _debug:
            print '\n debug -- Plotting Stacked Title: ', data['title']
            print '\n debug -- Plotting Stacked (Label) data[y_field][0]: ', data['y_field'][0]
            print '\n debug -- Plotting Stacked (Label) len(data[y_field]): ', len(data['y_field'])
            print '\n debug -- Plotting Stacked data[stream_name]: ', data['stream_name']

        #- - - - - - - - - - - - - - - - - - -
        # Get time component
        #- - - - - - - - - - - - - - - - - - -
        if _debug:  print '\n debug -- Plotting  Stacked: Get time...'
        time = mdates.date2num(data['x']['time'])
        plot_parameter = data['y_field'][0]
        plot_units = data['y_units'][0]
        if _debug:
            print '\n debug -- plot_parameter: ', plot_parameter
            print '\n debug -- plot_units: ', plot_units

        if isinstance(data['y'][plot_parameter][0], list):
            if _debug:
                print '\n debug -- Plotting  Stacked: Get z...'
                print '\n debug -- Plotting Stacked: Parameter \'%s\' available in data[y].' % plot_parameter
                print '\n debug -- Plotting Stacked: Parameter type \'%s\': %s ' % \
                                        (plot_parameter, str(type(data['y'][plot_parameter])))
                print '\n debug -- Plotting Stacked: Number of data items: %d' % len(data['y'][plot_parameter])
                #print '\n debug -- Plotting Stacked: [0]: ', data['y'][plot_parameter][0]
                #print '\n debug -- Plotting Stacked: [1]: ', data['y'][plot_parameter][1]
                print '\n debug -- Plotting Stacked: len(data[y][plot_parameter]): ', len(data['y'][plot_parameter])

            # Original
            z = np.array(data['y'][data['y_field'][0]])
            if '-SPKIR' in reference_designator:
                if _debug:
                    print '\n debug -- Dealing with SPKIR.....', reference_designator
                    print '\n debug -- SPIKR - type(z): ', str(type(z))
                    print '\n debug -- SPKIR - np.arange(len(z[0]))[::-1]: ', np.arange(len(z[0]))[::-1]
                ooi_plots.plot_stacked_time_series_spkir(fig, ax, time, np.arange(len(z[0]))[::-1], z.transpose(),
                                           title=data['title'],
                                           ylabel='Bin #',
                                           cbar_title=label,
                                           title_font=title_font,
                                           axis_font=axis_font,
                                           tick_font=tick_font)
            elif '-ZPLSC' in reference_designator:
                depth_parameter = data['y_field'][1]
                if _debug:
                    print '\n debug ---------------------------------------------------------------'
                    print '\n debug -- Dealing with ZPLSC.....', reference_designator
                    print '\n debug -- ZPLSC - type(z): ', str(type(z))
                    print '\n debug -- ZPLSC - np.arange(len(z[0]))[::-1]: ', np.arange(len(z[0]))[::-1]
                    print '\n debug -- ZPLSC - np.arange(len(z[0])): ', np.arange(len(z[0]))

                    #depth_parameter = data['y_field'][1]
                    print '\n debug -- Plotting Stacked: depth_parameter: ', depth_parameter
                    print '\n debug -- Plotting Stacked: len(data[y][depth_parameter]): ', len(data['y'][depth_parameter])

                #stacked_depth_ranges = np.array(data['y'][data['y_field'][1]])
                if _debug:  print '\n debug -- Plotting Stacked: (BEFORE) depth_parameter [0]: ', data['y'][depth_parameter][0][0:20]
                stacked_depth_ranges = np.array(data['y'][depth_parameter][:])
                if _debug:  print '\n debug -- Plotting Stacked: (AFTER) depth_parameter [0]: ', data['y'][depth_parameter][0][0:20]
                reverse = np.arange(len(stacked_depth_ranges[0]))[::-1]
                normal = np.arange(len(stacked_depth_ranges[0]))
                if _debug:
                    print '\n debug -- Dealing with stacked_depth_ranges.....'
                    print '\n debug -- Plotting Stacked: depth_parameter [0]: ', data['y'][depth_parameter][0][0:20]
                    print '\n debug -- Plotting Stacked: stacked_depth_ranges [0]: ', stacked_depth_ranges[0][0:20]
                    print '\n debug -- ZPLSC - type(stacked_depth_ranges): ', str(type(stacked_depth_ranges))
                    print '\n debug -- ZPLSC - np.arange(len(stacked_depth_ranges[0]))[::-1]: ', reverse
                    print '\n debug -- ZPLSC - np.arange(len(stacked_depth_ranges[0])): ', normal

                ooi_plots.plot_stacked_time_series_zplsc(fig, ax, time, np.arange(len(z[0]))[::-1], z.transpose(),
                                                               stacked_depth_ranges,
                                                               title=data['title'],
                                                               ylabel='',
                                                               cbar_title=label,
                                                               title_font=title_font,
                                                               axis_font=axis_font,
                                                               tick_font=tick_font)
            else:
                if _debug: print '\n debug -- NOT dealing with SPKIR......(ADCP)...'
                ooi_plots.plot_stacked_time_series(fig, ax, time, np.arange(len(z[0]))[::-1], z.transpose(),
                                           title=data['title'],
                                           ylabel='Bin #',
                                           cbar_title=label,
                                           title_font=title_font,
                                           axis_font=axis_font,
                                           tick_font=tick_font,
                                           plot_units=plot_units)

        else:
            if _debug:
                print '\n debug -- Plotting  Stacked: str(type(data[y][plot_parameter])): ', \
                                                                      str(type(data['y'][plot_parameter]))
            message = 'Unable to provide binned pseudo color plot for %s at this time.' % reference_designator
            raise Exception(message)

    elif plot_layout == '3d_scatter':
        """
        Plot 3d scatter plot
        Note: review the use of following: ax.xaxis.get_major_locator()._nbins = 5
        """
        if debug: print '\n-- Plotting 3D Scatter'

        stream_name = None
        if 'stream_name' in data:
            stream_name = data['stream_name']
        #number_of_data_points_requested = 1000
        #if 'number_of_data_points' in data:
        #    number_of_data_points_requested = data['number_of_data_points']

        time = data['x']['time']
        xlabel = data['y_field'][0]
        ylabel = data['y_field'][1]
        zlabel = data['y_field'][2]

        # Get labels for system parameter names; use system parameter names if error.
        x_display_label = get_parameter_label(stream_name, xlabel)
        y_display_label = get_parameter_label(stream_name, ylabel)
        z_display_label = get_parameter_label(stream_name, zlabel)
        if x_display_label is None:
            x_display_label = xlabel + " (" + data['y_units'][0] + ")"
        if y_display_label is None:
            y_display_label = ylabel + " (" + data['y_units'][1] + ")"
        if z_display_label is None:
            z_display_label = zlabel + " (" + data['y_units'][2] + ")"

        x = np.array(data['y'][xlabel])
        y = np.array(data['y'][ylabel])
        z = np.array(data['y'][zlabel])
        number_points = len(x)

        # Check for time units
        if 'time' in xlabel.lower():
            x = num2date(data['y'][xlabel], units='seconds since 1900-01-01 00:00:00', calendar='gregorian')
            x = mdates.date2num(x)

        """
        # Mask the bad data
        if debug: print '\n debug -- 3d scatter: turned on qa mask...'
        qaqc_x = data['qaqc'][xlabel] < 1
        qaqc_y = data['qaqc'][ylabel] < 1
        qaqc_z = data['qaqc'][zlabel] < 1
        mask = qaqc_x & qaqc_y & qaqc_z
        x = x[mask]
        y = x[mask]
        if debug: print '\n debug -- 3d scatter: after turned on qa mask...'
        """

        # if len(x) <= 0:
        #     raise(Exception('No good data available!'))

        ooi_plots.plot_3d_scatter(fig, ax, x, y, z,
                                  title=data['title'],
                                  xlabel=x_display_label,
                                  ylabel=y_display_label,
                                  zlabel=z_display_label,
                                  title_font=title_font,
                                  tick_font=tick_font,
                                  axis_font=axis_font,
                                  number_points=number_points)

    elif plot_layout == 'rose':
        """
        Plot rose
        """
        if debug: print '\n-- Plotting Rose'

        # Need to create new fig and axes here
        plt.close(fig)

        xlabel = data['y_field'][0]
        ylabel = data['y_field'][1]
        magnitude = np.array(data['y'][xlabel])
        direction = np.array(data['y'][ylabel])

        # Mask the bad data
        # qaqc_mag = data['qaqc'][xlabel] < 1
        # qaqc_dir = data['qaqc'][ylabel] < 1
        # mask = qaqc_mag & qaqc_dir
        # magnitude = magnitude[mask]
        # direction = direction[mask]
        # if len(magnitude) <= 0:
        #     raise(Exception('No good data avaliable!'))

        # Add carriage return after plot title.
        title = data['title'] + '\n'

        # Get legend title.
        default_legend_title = data['y_field'][0] + ' (' + data['y_units'][0] + ')'
        if 'stream_name' in data:
            legend_title = get_parameter_label(data['stream_name'], data['y_field'][0])
            if legend_title is None:
                legend_title = default_legend_title
        else:
            # If no stream_name, default to system parameter name and units
            legend_title = default_legend_title

        size = height if height <= width else width
        size = 6 if size < 6 else size
        hypot = np.sqrt(size**2 + size**2) + 1
        fig = ooi_plots.plot_rose(magnitude, direction,
                                  figsize=size,
                                  bins=5,
                                  title=title,
                                  title_font=title_font,
                                  legend_title=legend_title,
                                  fontsize=int(hypot) + 2)

    #=============================================================
    # Wrap up and return buf from fig created.
    buf = io.BytesIO()

    # plt.tick_params(axis='both', which='major', labelsize=10)
    if plot_format not in ['svg', 'png']:
        plot_format = 'svg'

    plt.savefig(buf, format=plot_format)
    buf.seek(0)
    plt.close(fig)
    return buf


# For a stream and system parameter, get the uframe stream engine values (english)
def get_parameter_label(stream_name, parameter):
    label = None
    try:
        if stream_name and stream_name is not None and parameter and parameter is not None:
            label = get_parameter_name_by_parameter_stream(parameter, stream_name)
        return label
    except Exception as err:
        message = str(err)
        raise Exception(message)