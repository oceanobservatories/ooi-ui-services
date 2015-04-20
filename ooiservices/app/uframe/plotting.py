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

__author__ = 'Andy Bird'

# Define some default settings for fonts
axis_font_default = {'fontname': 'Calibri',
                     'size': '12',
                     'color': 'black',
                     'weight': 'bold',
                     'verticalalignment': 'bottom'}

title_font_default = {'fontname': 'Arial',
                      'size': '16',
                      'color': 'black',
                      'weight': 'bold',
                      'verticalalignment': 'bottom'}

# Define the matplotlib style sheet and some colors from that style
plt.style.use('bmh')
colors = plt.rcParams['axes.color_cycle']

# Instantiate the OOIPlots class
ooi_plots = OOIPlots()


def generate_plot(data, plot_format, plot_layout, use_line, use_scatter, plot_profile_id=None, width_in= 8.3):

    fig, ax = ppl.subplots(1, 1, figsize=(data['width'], data['height']))

    # plot_layout = 'quiver'
    is_timeseries = False
    if "time" == data['x_field'][0]:
        data['x']['time'] = num2date(data['x']['time'], units='seconds since 1900-01-01 00:00:00', calendar='gregorian')
        is_timeseries = True

    if plot_layout == "timeseries":
        '''
        Plot time series data
        '''

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
                                       title_font=title_font_default,
                                       axis_font=axis_font_default,
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
                                           axis_font=axis_font_default,
                                           title_font=title_font_default,
                                           scatter = use_scatter,
                                           width_in = width_in,
                                           **kwargs)

    elif plot_layout == "depthprofile":
        '''
        Plot depth profiles (overlay)
        '''

        # Define some plot parameters
        kwargs = dict(linewidth=1.5, alpha=0.7)

        if plot_profile_id is None:

            for profile_id in range(0, np.shape(data['x'])[0]):
                print data['time'][profile_id]
                ooi_plots.plot_profile(fig,
                                       ax,
                                       data['x'][profile_id],
                                       data['y'][profile_id],
                                       xlabel=data['x_field'],
                                       ylabel=data['y_field'],
                                       axis_font=axis_font_default,
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
                                       axis_font=axis_font_default,
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
                                       axis_font=axis_font_default,
                                       line=use_line,
                                       scatter=use_scatter,
                                       **kwargs)
        plt.gca().invert_yaxis()

    elif plot_layout == 'ts_diagram':
        '''
        Plot a Temperature-Salinity diagram
        '''

        # Define some plot parameters
        kwargs = dict(color='r', marker='o')

        # This should be used with 'real' data only (NO COUNTS!!)
        x = np.asarray(data['x'])
        y = np.asarray(data['y'])

        ooi_plots.plot_ts_diagram(ax, x, y,
                                  title=data['title'],
                                  xlabel=data['x_field'],
                                  ylabel=data['y_field'],
                                  title_font=title_font_default,
                                  axis_font=axis_font_default,
                                  **kwargs)

    elif plot_layout == 'quiver':
        '''
        Plot magnitude and direction as a time series on a quiver plot
        '''
        kwargs = dict(color='#0000FF',
                      units='y',
                      scale_units='y',
                      scale=1,
                      headlength=10,
                      headaxislength=5,
                      edgecolors='#000000',
                      width=0.1,
                      alpha=0.5)
        time = mdates.date2num(data['x']['time'])
        u = data['y'][data['y_field'][0]]
        v = data['y'][data['y_field'][1]]

        ooi_plots.plot_1d_quiver(fig, ax, time, u, v,
                                 title=data['title']+'\n'+'Quiver Plot',
                                 ylabel='Velocity (m/s)',
                                 title_font=title_font_default,
                                 axis_font=axis_font_default)

    elif plot_layout == '3d_scatter':
        '''
        Plot 3d scatter plot
        '''

        # print 'Plotting 3D Scatter'
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
                                  title_font=title_font_default,
                                  axis_font=axis_font_default)

    buf = io.BytesIO()

    plt.tight_layout()
    # plt.tick_params(axis='both', which='major', labelsize=10)

    if plot_format not in ['svg', 'png']:
        plot_format = 'svg'
    plt.savefig(buf, format=plot_format)
    buf.seek(0)

    plt.clf()
    plt.cla()

    return buf
