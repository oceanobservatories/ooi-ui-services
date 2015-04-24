#!/usr/bin/env python
'''
ooiservices/app/main/plotting.py

Support for generating svg plots
'''

from netCDF4 import num2date
from ooiservices.app import cache
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import ScalarFormatter
import matplotlib.pyplot as plt
import io
import numpy as np
import matplotlib.dates as mdates
import prettyplotlib as ppl
import seawater as sw

__author__ = 'Andy Bird'

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

plt.style.use('bmh')
colors = plt.rcParams['axes.color_cycle']

def generate_plot(data, plot_format, plot_layout, use_line, use_scatter, plot_profile_id=None, width_in= 8.3):

    fig, ax = ppl.subplots(1, 1, figsize=(data['width'], data['height']))
    kwargs = dict(linewidth=1.0, alpha=0.7)

    is_timeseries = False
    if "time" == data['x_field'][0]:
        data['x']['time'] = num2date(data['x']['time'], units='seconds since 1900-01-01 00:00:00', calendar='gregorian')
        is_timeseries = True
        #print '****START', data['x']['time'][0], '*** END', data['x']['time'][-1]

    if plot_layout == "timeseries":

        if len(data['x_field']) == 1 and len(data['y_field']) == 1:
            xlabel = data['x_field'][0]
            ylabel = data['y_field'][0]
            xdata = data['x'][xlabel]
            ydata = data['y'][ylabel]

            plot_time_series(fig, is_timeseries, ax, xdata, ydata,
                             title=data['title'],
                             xlabel=xlabel,
                             ylabel=ylabel,
                             title_font=title_font_default,
                             axis_font=axis_font_default,
                             line = use_line,
                             scatter = use_scatter,
                             **kwargs)
        elif len(data['y_field']) > 1:
            xdata = data['x'][data['x_field'][0]]
            ydata = data['y']

            plot_multiple_yaxes(fig, ax,
                                xdata,
                                ydata,
                                colors,
                                title=data['title'],
                                axis_font=axis_font_default,
                                title_font=title_font_default,
                                scatter = use_scatter,
                                width_in = width_in,
                                **kwargs)
        elif len(data['x_field']) > 1:
            ydata = data['y'][data['y_field'][0]]
            xdata = data['x']

            plot_multiple_xaxes(fig, ax,
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
        if plot_profile_id is None:
            for profile_id in range(0, np.shape(data['x'])[0]):
                plot_profile(fig,
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
                plot_profile(fig,
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
                plot_profile(fig,
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

        # This should be used with 'real' data only (NO COUNTS!!)
        x = np.asarray(data['x'])
        y = np.asarray(data['y'])

        kwargs = dict(color='r', marker='o')
        plot_ts_diagram(ax, x, y,
                        title=data['title'],
                        xlabel=data['x_field'],
                        ylabel=data['y_field'],
                        title_font=title_font_default,
                        axis_font=axis_font_default,
                        **kwargs)

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


@cache.memoize(timeout=3600)
def plot_profile(fig, ax, x, y, xlabel='', ylabel='',
                 axis_font={}, line=True , scatter=False, **kwargs):

    if not axis_font:
        axis_font = axis_font_default
    if line:
        ppl.plot(ax, x, y, **kwargs)
    if scatter:
        ppl.scatter(ax, x, y, **kwargs)

    if xlabel:
        ax.set_xlabel(xlabel, labelpad=5, **axis_font)
    if ylabel:
        ax.set_ylabel(ylabel, labelpad=11, **axis_font)
    ax.xaxis.set_label_position('top')  # this moves the label to the top
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.get_major_locator()._nbins = 5
    ax.grid(True)
    # ax.set_title(title, **title_font)


@cache.memoize(timeout=3600)
def plot_time_series(fig, is_timeseries, ax, x, y, fill=False, title='', xlabel='', ylabel='',
                     title_font={}, axis_font={}, line=True, scatter=False , **kwargs):

    if not title_font:
        title_font = title_font_default
    if not axis_font:
        axis_font = axis_font_default

    if line:
        h = ppl.plot(ax, x, y, **kwargs)
    if scatter:
        ppl.scatter(ax, x, y, **kwargs)

    if is_timeseries:
        get_time_label(ax, x)
        fig.autofmt_xdate()
    else:
        ax.set_xlabel(xlabel, **axis_font)

    if ylabel:
        ax.set_ylabel(ylabel, **axis_font)
    if title:
        ax.set_title(title, **title_font)
    if 'degree' in ylabel:
        ax.set_ylim([0, 360])
    ax.grid(True)
    if fill:
        miny = min(ax.get_ylim())
        ax.fill_between(x, y, miny+1e-7, facecolor = h[0].get_color(), alpha=0.15)

    plt.tick_params(axis='both', which='major', labelsize=10)


@cache.memoize(timeout=3600)
def plot_multiple_xaxes(ax, xdata, ydata, colors, ylabel='Depth (m)', title='', title_font={},
                        axis_font={},width_in=8.3, **kwargs):
    # Acknowledgment: This function is based on code written by Jae-Joon Lee,
    # URL= http://matplotlib.svn.sourceforge.net/viewvc/matplotlib/trunk/matplotlib/
    # examples/pylab_examples/multiple_yaxis_with_spines.py?revision=7908&view=markup

    if not title_font:
        title_font = title_font_default
    if not axis_font:
        axis_font = axis_font_default

    n_vars = len(xdata)
    if n_vars > 6:
        raise Exception('This code currently handles a maximum of 6 independent variables.')
    elif n_vars < 2:
        raise Exception('This code currently handles a minimum of 2 independent variables.')

    # Generate the plot.
    # Use twiny() to create extra axes for all dependent variables except the first
    # (we get the first as part of the ax axes).
    x_axis = n_vars * [0]
    x_axis[0] = ax
    for i in range(1, n_vars):
        x_axis[i] = ax.twiny()

    ax.spines["top"].set_visible(False)
    make_patch_spines_invisible(x_axis[1])
    set_spine_direction(x_axis[1], "top")

    offset = [1.10, -0.1, -0.20, 1.20]
    spine_directions = ["top", "bottom", "bottom", "top", "top", "bottom"]

    count = 0
    for i in range(2, n_vars):
        x_axis[i].spines[spine_directions[count]].set_position(("axes", offset[count]))
        make_patch_spines_invisible(x_axis[i])
        set_spine_direction(x_axis[i], spine_directions[count])
        count += 1

    # Adjust the axes left/right accordingly
    if n_vars >= 4:
        plt.subplots_adjust(bottom=0.2, top=0.8)
    elif n_vars == 3:
        plt.subplots_adjust(bottom=0.0, top=0.8)

    # Label the y-axis:
    ax.set_ylabel(ylabel,  **axis_font)
    for ind, key in enumerate(xdata):
        x_axis[ind].plot(xdata[key], ydata, colors[ind], **kwargs)
        # Label the x-axis and set text color:
        x_axis[ind].set_xlabel(key, **axis_font)
        x_axis[ind].xaxis.label.set_color(colors[ind])
        x_axis[ind].spines[spine_directions[ind]].set_color(colors[ind])

        for obj in x_axis[ind].xaxis.get_ticklines():
            # `obj` is a matplotlib.lines.Line2D instance
            obj.set_color(colors[ind])
            obj.set_markeredgewidth(2)

        for obj in x_axis[ind].xaxis.get_ticklabels():
            obj.set_color(colors[ind])

    ax.invert_yaxis()
    ax.grid(True)
    ax.set_title(title, y=1.23, **title_font)


@cache.memoize(timeout=3600)
def plot_multiple_yaxes(fig, ax, xdata, ydata, colors, title, scatter=False,
                        axis_font={}, title_font={}, width_in=8.3 ,**kwargs):
    # Plot a timeseries with multiple y-axes
    #
    # ydata is a python dictionary of all the data to plot. Key values are used as plot labels
    #
    # Acknowledgment: This function is based on code written by Jae-Joon Lee,
    # URL= http://matplotlib.svn.sourceforge.net/viewvc/matplotlib/trunk/matplotlib/
    # examples/pylab_examples/multiple_yaxis_with_spines.py?revision=7908&view=markup
    #
    # http://matplotlib.org/examples/axes_grid/demo_parasite_axes2.html

    if not axis_font:
        axis_font = axis_font_default
    if not title_font:
        title_font = title_font_default

    n_vars = len(ydata)
    if n_vars > 6:
        raise Exception('This code currently handles a maximum of 6 independent variables.')
    elif n_vars < 2:
        raise Exception('This code currently handles a minimum of 2 independent variables.')

    if scatter:
        kwargs['marker'] = 'o'
    # Generate the plot.
    # Use twinx() to create extra axes for all dependent variables except the first
    # (we get the first as part of the ax axes).

    y_axis = n_vars * [0]
    y_axis[0] = ax
    for i in range(1, n_vars):
        y_axis[i] = ax.twinx()

    ax.spines["top"].set_visible(False)
    make_patch_spines_invisible(y_axis[1])
    set_spine_direction(y_axis[1], "top")

    # Define the axes position offsets for each 'extra' axis
    spine_directions = ["left", "right", "left", "right", "left", "right"]


    # Adjust the axes left/right accordingly    
    if n_vars >= 4:        
        if width_in<8.3:    
            #set axis location
            offset = [1.2, -0.2, 1.40, -0.40]
            #overwrite width
            l_mod = 0.3
            r_mod = 0.8
        else:
            offset = [1.10, -0.10, 1.20, -0.20]
            l_mod = 0.5
            r_mod = 1.2

        plt.subplots_adjust(left=l_mod, right=r_mod)
    elif n_vars == 3:
        offset = [1.20, -0.20, 1.40, -0.40]
        plt.subplots_adjust(left=0.0, right=0.7)

    count = 0
    for i in range(2, n_vars):
        y_axis[i].spines[spine_directions[count+1]].set_position(("axes", offset[count]))
        make_patch_spines_invisible(y_axis[i])
        set_spine_direction(y_axis[i], spine_directions[count+1])
        count += 1

    # Plot the data
    for ind, key in enumerate(ydata):

        y_axis[ind].plot(xdata, ydata[key], colors[ind], **kwargs)

        # Label the y-axis and set text color:

        # Been experimenting with other ways to handle tick labels with spines
        y_axis[ind].yaxis.get_major_formatter().set_useOffset(False)

        y_axis[ind].set_ylabel(key.replace("_", " "), labelpad=10, **axis_font)
        y_axis[ind].yaxis.label.set_color(colors[ind])
        y_axis[ind].spines[spine_directions[ind]].set_color(colors[ind])
        y_axis[ind].tick_params(axis='y', labelsize=8, colors=colors[ind])

    get_time_label(ax, xdata)
    fig.autofmt_xdate()

    ax.tick_params(axis='x', labelsize=10)
    ax.set_title(title.replace("_", " "), y=1.05, **title_font)
    ax.grid(True)


@cache.memoize(timeout=3600)
def plot_ts_diagram(ax, sal, temp, xlabel='Salinity', ylabel='Temperature', title='',
                    axis_font={}, title_font={}, **kwargs):

    if not axis_font:
        axis_font = axis_font_default
    if not title_font:
        title_font = title_font_default

    sal = np.ma.array(sal, mask=np.isnan(sal))
    temp = np.ma.array(temp, mask=np.isnan(temp))
    if len(sal) != len(temp):
        raise Exception('Sal and Temp arrays are not the same size!')

    # Figure out boudaries (mins and maxs)
    smin = sal.min() - (0.01 * sal.min())
    smax = sal.max() + (0.01 * sal.max())
    tmin = temp.min() - (0.1 * temp.max())
    tmax = temp.max() + (0.1 * temp.max())

    # Calculate how many gridcells we need in the x and y dimensions
    xdim = round((smax-smin)/0.1+1, 0)
    ydim = round((tmax-tmin)+1, 0)

    # Create empty grid of zeros
    dens = np.zeros((ydim, xdim))

    # Create temp and sal vectors of appropiate dimensions
    ti = np.linspace(1, ydim-1, ydim)+tmin
    si = np.linspace(1, xdim-1, xdim)*0.1+smin

    # Loop to fill in grid with densities
    for j in range(0, int(ydim)):
        for i in range(0, int(xdim)):
            dens[j, i] = sw.dens(si[i], ti[j], 0)

    # Substract 1000 to convert to sigma-t
    dens = dens - 1000

    # Plot data
    cs = plt.contour(si, ti, dens, linestyles='dashed', colors='k')

    plt.clabel(cs, fontsize=12, inline=1, fmt='%1.0f')  # Label every second level
    ppl.scatter(ax, sal, temp, **kwargs)

    ax.set_xlabel(xlabel, **axis_font)
    ax.set_ylabel(ylabel, **axis_font)
    ax.set_title(title, **title_font)


@cache.memoize(timeout=3600)
def plot_stacked_time_series(fig, ax, x, y, z, title='', ylabel='',
                             cbar_title='', title_font={}, axis_font={},
                             **kwargs):

    if not title_font:
        title_font = title_font_default
    if not axis_font:
        axis_font = axis_font_default
    z = np.ma.array(z, mask=np.isnan(z))
    h = plt.pcolormesh(x, y, z, shading='gouraud', **kwargs)
    # h = plt.pcolormesh(x, y, z, **kwargs)
    if ylabel:
        ax.set_ylabel(ylabel, **axis_font)
    if title:
        ax.set_title(title, **title_font)
    plt.axis([x.min(), x.max(), y.min(), y.max()])
    ax.xaxis_date()
    date_list = mdates.num2date(x)
    get_time_label(ax, date_list)
    fig.autofmt_xdate()
    ax.invert_yaxis()
    cbar = plt.colorbar(h)
    if cbar_title:
        cbar.ax.set_ylabel(cbar_title)
    ax.grid(True)


def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.itervalues():
        sp.set_visible(False)


def set_spine_direction(ax, direction):
    if direction in ["right", "left"]:
        ax.yaxis.set_ticks_position(direction)
        ax.yaxis.set_label_position(direction)
    elif direction in ["top", "bottom"]:
        ax.xaxis.set_ticks_position(direction)
        ax.xaxis.set_label_position(direction)
    else:
        raise ValueError("Unknown Direction: %s" % (direction,))
    ax.spines[direction].set_visible(True)


def get_time_label(ax, dates):
    '''
    Custom date axis formatting
    '''
    def format_func(x, pos=None):
        x = mdates.num2date(x)
        if pos == 0:
            fmt = '%Y-%m-%d %H:%M'
        else:
            fmt = '%H:%M'
        label = x.strftime(fmt)
        # label = label.rstrip("0")
        # label = label.rstrip(".")
        return label
    day_delta = (max(dates)-min(dates)).days

    if day_delta < 1:
        ax.xaxis.set_major_formatter(FuncFormatter(format_func))
    else:
        # pass
        major = mdates.AutoDateLocator()
        formt = mdates.AutoDateFormatter(major, defaultfmt=u'%Y-%m-%d')
        formt.scaled[1.0] = '%Y-%m-%d'
        formt.scaled[30] = '%Y-%m'
        formt.scaled[1./24.] = '%Y-%m-%d %H:%M:%S'
        # formt.scaled[1./(24.*60.)] = FuncFormatter(format_func)
        ax.xaxis.set_major_locator(major)
        ax.xaxis.set_major_formatter(formt)
