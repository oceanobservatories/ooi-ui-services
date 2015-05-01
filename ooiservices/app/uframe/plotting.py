#!/usr/bin/env python
'''
ooiservices/app/main/plotting.py

Support for generating svg plots
'''

from netCDF4 import num2date
from ooiservices.app.uframe.plot_tools import OOIPlots
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import numpy as np
import prettyplotlib as ppl
from flask import current_app

__author__ = 'Andy Bird'

# Define the matplotlib style sheet and some colors from that style
plt.style.use('bmh')
colors = plt.rcParams['axes.color_cycle']

# Instantiate the OOIPlots class
ooi_plots = OOIPlots()


def generate_plot(data, plot_format, plot_layout, use_line, use_scatter, plot_profile_id=None, width_in= 8.3):

    # Generate the plot figure and axes
    width = data['width']
    height = data['height']
    fig, ax = ppl.subplots(1, 1, figsize=(width, height))

    # Define the fonts
    title_font = {'fontname': 'Calibri',
                  'size': '16',
                  'color': 'black',
                  'weight': 'bold'}

    axis_font = {'fontname': 'Calibri',
                 'size': '14',
                 'weight': 'bold'}

    tick_font = {'axis': 'both',
                 'labelsize': 10,
                 'width': 1,
                 'color': 'k'}

    # Calculate the hypotenuse to determine appropriate font sizes
    hypot = np.sqrt(width**2 + height**2)
    tick_font['labelsize'] = int(hypot)
    axis_font['size'] = int(hypot) + 4

    # plot_layout = 'quiver'
    is_timeseries = False
    if "time" == data['x_field'][0]:
        data['x']['time'] = num2date(data['x']['time'], units='seconds since 1900-01-01 00:00:00', calendar='gregorian')
        is_timeseries = True

    if plot_layout == "timeseries":
        '''
        Plot time series data
        '''

        current_app.logger.debug('Plotting Time Series')

        # Define some plot parameters
        kwargs = dict(linewidth=1.5, alpha=0.7)

        if len(data['x_field']) == 1 and len(data['y_field']) == 1:
            xlabel = data['x_field'][0]
            ylabel = data['y_field'][0]
            xdata = data['x'][xlabel]
            ydata = data['y'][ylabel]

            ooi_plots.plot_time_series(fig, is_timeseries, ax, xdata, ydata,
                                       title=data['title'],
                                       xlabel=xlabel,
                                       ylabel=ylabel,
                                       title_font=title_font,
                                       axis_font=axis_font,
                                       tick_font=tick_font,
                                       line = use_line,
                                       scatter = use_scatter,
                                       **kwargs)
        else:
            xdata = data['x']['time']
            ydata = data['y']

            ooi_plots. plot_multiple_yaxes(fig, ax,
                                           xdata,
                                           ydata,
                                           colors,
                                           title=data['title'],
                                           axis_font=axis_font,
                                           title_font=title_font,
                                           tick_font=tick_font,
                                           scatter = use_scatter,
                                           width_in = width_in,
                                           **kwargs)

    elif plot_layout == "depthprofile":
        '''
        Plot depth profiles (overlay)
        '''

        current_app.logger.debug('Plotting Depth Profile')
        # Define some plot parameters
        kwargs = dict(linewidth=1.5, alpha=0.7)

        if plot_profile_id is None:

            for profile_id in range(0, np.shape(data['x'])[0]):
                # print data['time'][profile_id]
                ooi_plots.plot_profile(fig,
                                       ax,
                                       data['x'][profile_id],
                                       data['y'][profile_id],
                                       xlabel=data['x_field'],
                                       ylabel=data['y_field'],
                                       axis_font=axis_font,
                                       tick_font=tick_font,
                                       line=use_line,
                                       scatter=use_scatter,
                                       **kwargs)
        else:
            if int(plot_profile_id) < int(np.shape(data['x'])[0]):
                # get the profile selected
                ooi_plots.plot_profile(fig,
                                       ax,
                                       data['x'][int(plot_profile_id)],
                                       data['y'][int(plot_profile_id)],
                                       xlabel=data['x_field'],
                                       ylabel=data['y_field'],
                                       axis_font=axis_font,
                                       tick_font=tick_font,
                                       line=use_line,
                                       scatter=use_scatter,
                                       **kwargs)
            else:
                # return something
                ooi_plots.plot_profile(fig,
                                       ax,
                                       data['x'][0],
                                       data['y'][0],
                                       xlabel=data['x_field'],
                                       ylabel=data['y_field'],
                                       axis_font=axis_font,
                                       tick_font=tick_font,
                                       line=use_line,
                                       scatter=use_scatter,
                                       **kwargs)
        plt.gca().invert_yaxis()

    elif plot_layout == 'ts_diagram':
        '''
        Plot a Temperature-Salinity diagram
        '''

        current_app.logger.debug('Plotting T-S Diagram')

        # Define some plot parameters
        kwargs = dict(color='r', marker='o')

        # This should be used with 'real' data only (NO COUNTS!!)
        x = data['y'][data['y_field'][0]]
        y = data['y'][data['y_field'][1]]
        xlabel = data['y_field'][0]
        ylabel = data['y_field'][1]

        ooi_plots.plot_ts_diagram(ax, x, y,
                                  title=data['title'],
                                  xlabel=xlabel,
                                  ylabel=ylabel,
                                  title_font=title_font,
                                  axis_font=axis_font,
                                  tick_font=tick_font,
                                  **kwargs)

    elif plot_layout == 'quiver':
        '''
        Plot magnitude and direction as a time series on a quiver plot
        '''

        current_app.logger.debug('Plotting Quiver')
        # color='#0000FF',
        # edgecolors='#000000',
        kwargs = dict(units='y',
                      scale_units='y',
                      scale=1,
                      headlength=10,
                      headaxislength=5,
                      width=0.1,
                      alpha=0.5)
        time = mdates.date2num(data['x']['time'])
        u = data['y'][data['y_field'][0]]
        v = data['y'][data['y_field'][1]]

        ooi_plots.plot_1d_quiver(fig, ax, time, u, v,
                                 title=data['title']+'\n'+'Quiver Plot',
                                 ylabel='Velocity (m/s)',
                                 tick_font=tick_font,
                                 title_font=title_font,
                                 axis_font=axis_font)

    elif plot_layout == '3d_scatter':
        '''
        Plot 3d scatter plot
        '''

        current_app.logger.debug('Plotting 3D Scatter')

        time = data['x']['time']
        xlabel = data['y_field'][0]
        ylabel = data['y_field'][1]
        zlabel = data['y_field'][2]
        x = data['y'][xlabel]
        y = data['y'][ylabel]
        z = data['y'][zlabel]

        ooi_plots.plot_3d_scatter(fig, ax, x, y, z,
                                  title=data['title']+'\n'+'3D Scatter',
                                  xlabel=xlabel,
                                  ylabel=ylabel,
                                  zlabel=zlabel,
                                  title_font=title_font,
                                  tick_font=tick_font,
                                  axis_font=axis_font)

    elif plot_layout == 'rose':
        '''
        Plot rose
        '''
        plt.close(fig)  # Need to create new fig and axes here
        current_app.logger.debug('Plotting Rose')

        xlabel = data['y_field'][0]
        ylabel = data['y_field'][1]
        magnitude = data['y'][xlabel]
        direction = data['y'][ylabel]
        size = height if height <= width else width
        size = 6 if size < 6 else size
        print size
        hypot = np.sqrt(size**2 + size**2) + 1
        fig = ooi_plots.plot_rose(magnitude, direction,
                                  figsize=size,
                                  bins=5,
                                  title=data['title'],
                                  title_font=title_font,
                                  fontsize=int(hypot)+2)

    buf = io.BytesIO()

    # plt.tight_layout()
    # plt.tick_params(axis='both', which='major', labelsize=10)

    if plot_format not in ['svg', 'png']:
        plot_format = 'svg'
    plt.savefig(buf, format=plot_format)
    buf.seek(0)

    plt.close(fig)

    return buf
