#!/usr/bin/env python
'''
ooiservices/app/main/plotting.py

Support for generating svg plots
'''

__author__ = 'Andy Bird'

#plotting
import matplotlib
import matplotlib.pyplot as plt
import io
import numpy as np
import time
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import prettyplotlib as ppl
from netCDF4 import num2date
from ooiservices.app import cache

axis_font = {'fontname': 'Calibri',
                     'size': '14',
                     'color': 'black',
                     'weight': 'bold',
                     'verticalalignment': 'bottom'}

title_font = {'fontname': 'Arial',
                      'size': '18',
                      'color': 'black',
                      'weight': 'bold',
                      'verticalalignment': 'bottom'}

PRESSURE_RATIO = 100

def generate_plot(title,xlabel,ylabel,x,y,xvar,yvar,height_in,width_in,plot_format,plot_layout,use_line,use_scatter,plot_profile_id=None):

    fig, ax = ppl.subplots(1, 1, figsize=(width_in, height_in))
    kwargs = dict(linewidth=1.0,alpha=0.7)
    
    is_timeseries = False
    if "_timestamp" in xvar:
        x = num2date(x, units='seconds since 1900-01-01 00:00:00', calendar='gregorian')
        is_timeseries = True
    
    if plot_layout == "timeseries":
        plot_time_series(fig, is_timeseries, ax, x, y,
                             title=title,
                             xlabel=xlabel,
                             ylabel=ylabel,
                             title_font=title_font,
                             axis_font=axis_font,
                             line = use_line,
                             scatter = use_scatter,
                             **kwargs)

    elif plot_layout == "depthprofile":            
        if plot_profile_id is None:
          for profile_id in range(0,np.shape(x)[0]):            
            plot_profile(fig, 
                          ax, 
                          x[profile_id], 
                          y[profile_id],
                          xlabel=xlabel, 
                          ylabel=ylabel,
                          axis_font=axis_font, 
                          line = use_line,
                          scatter= False,
                          **kwargs)
        else:          
          if int(plot_profile_id) < int(np.shape(x)[0]) :
            print "\t   less than"
            #get the profile selected            
            plot_profile(fig, 
                          ax, 
                          x[int(plot_profile_id)], 
                          y[int(plot_profile_id)],
                          xlabel=xlabel, 
                          ylabel=ylabel,
                          axis_font=axis_font, 
                          line = use_line,
                          scatter= False,
                          **kwargs)
          else:
            print "\t   couldnt find it"
            #return something
            plot_profile(fig, 
                          ax, 
                          x[0], 
                          y[0],
                          xlabel=xlabel, 
                          ylabel=ylabel,
                          axis_font=axis_font, 
                          line = use_line,
                          scatter= False,
                          **kwargs)
        plt.tight_layout()

    buf = io.BytesIO()
    
    if plot_format not in ['svg', 'png']:
        plot_format = 'svg'
    plt.savefig(buf, format=plot_format)
    buf.seek(0)

    plt.clf()
    plt.cla()

    return buf 

@cache.memoize(timeout=3600)
def plot_profile(fig,ax, x, y, xlabel='', ylabel='',
                 axis_font={},line=True , scatter=True, **kwargs):
    
    y = (np.array(y))/ PRESSURE_RATIO

    if not axis_font:
        axis_font = axis_font_default
    ppl.plot(ax, x, y, **kwargs)
    if xlabel:
        ax.set_xlabel(xlabel,labelpad=5, **axis_font)
    if ylabel:
        ax.set_ylabel(ylabel, labelpad=11, **axis_font)
    ax.invert_yaxis()
    ax.xaxis.set_label_position('top')  # this moves the label to the top
    ax.xaxis.set_ticks_position('top')
    ax.grid(True)    
    # ax.set_title(title, **title_font)

@cache.memoize(timeout=3600)
def plot_time_series(fig, is_timeseries, ax, x, y, fill=False, title='',xlabel='', ylabel='',
                         title_font={}, axis_font={}, line=True, scatter=False ,**kwargs):

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
         ax.set_xlabel(xlabel,**axis_font)

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
    # plt.subplots_adjust(top=0.85)
    plt.tight_layout()

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

def plot_scatter(fig, ax, x, y, title='', xlabel='', ylabel='',
                     title_font={}, axis_font={}, **kwargs):

        if not title_font:
            title_font = title_font_default
        if not axis_font:
            axis_font = axis_font_default

        ppl.scatter(ax, x, y, **kwargs)
        if xlabel:
            ax.set_xlabel(xlabel, labelpad=10, **axis_font)
        if ylabel:
            ax.set_ylabel(ylabel, labelpad=10, **axis_font)
        ax.set_title(title, **title_font)
        ax.grid(True)
        ax.set_aspect(1./ax.get_data_ratio())  # make axes square

