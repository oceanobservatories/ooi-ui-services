"""
Plotting tools for OOI data
"""
from ooiservices.app import cache
from netCDF4 import num2date
import numpy as np
import prettyplotlib as ppl
from prettyplotlib import plt
from ooiservices.app.uframe.windrose import WindroseAxes
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import seawater as sw
from matplotlib.dates import datestr2num
from matplotlib.image import NonUniformImage
from mpl_toolkits.axes_grid1 import make_axes_locatable

axis_font_default = {'fontname': 'Calibri',
                     'size': '14',
                     'color': 'black',
                     'weight': 'bold',
                     'verticalalignment': 'bottom'}

title_font_default = {'fontname': 'Arial',
                      'size': '18',
                      'color': 'black',
                      'weight': 'bold',
                      'verticalalignment': 'bottom'}


class OOIPlots(object):

    def get_time_label(self, ax, dates):
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
            return label
        day_delta = (max(dates) - min(dates)).days

        if day_delta < 1:
            ax.xaxis.set_major_formatter(FuncFormatter(format_func))
        else:
            major = mdates.AutoDateLocator()
            formt = mdates.AutoDateFormatter(major, defaultfmt=u'%Y-%m-%d')
            formt.scaled[1.0] = '%Y-%m-%d'
            formt.scaled[30] = '%Y-%m'
            formt.scaled[1./24.] = '%Y-%m-%d %H:%M'
            # formt.scaled[1./(24.*60.)] = FuncFormatter(format_func)
            ax.xaxis.set_major_locator(major)
            ax.xaxis.set_major_formatter(formt)

    def add_annotation(self, ax):
        '''
        This method adds annotation to the plot figure in the lower left corner next to the watermark
        '''
        annotation = 'Color bar is set to +/- 95th percentile value'
        ax.annotate(annotation, xy=(40, 0), xycoords='figure pixels',
                    horizontalalignment='left', verticalalignment='bottom', fontsize=8, style='italic')

    def plot_time_series(self, fig, is_timeseries, ax, x, y, fill=False, title='', xlabel='', ylabel='',
                         title_font={}, axis_font={}, tick_font={}, scatter=False, qaqc=[], events={}, **kwargs):

        debug = False
        if debug: print '\n debug -- Entered plot_time_series...'
        if not title_font:
            title_font = title_font_default
        if not axis_font:
            axis_font = axis_font_default

        if scatter:
            ppl.scatter(ax, x, y, **kwargs)
            ppl.scatter(ax, x, y, **kwargs)
        else:
            h = ppl.plot(ax, x, y, **kwargs)

        if is_timeseries:
            self.get_time_label(ax, x)
            fig.autofmt_xdate()
        else:
            ax.set_xlabel(xlabel.replace("_", " "), **axis_font)

        if ylabel:
            ax.set_ylabel(ylabel.replace("_", " "), **axis_font)
        if title:
            ax.set_title(title.replace("_", " "), **title_font)

        ax.grid(True)
        if fill:
            miny = min(ax.get_ylim())
            if not scatter:
                ax.fill_between(x, y, miny + 1e-7, facecolor = h[0].get_color(), alpha=0.15)
            else:
                #ax.fill_between(x, y, miny + 1e-7, facecolor = axis_font_default['color'], alpha=0.15)
                ax.fill_between(x, y, miny + 1e-5, facecolor = axis_font_default['color'], alpha=0.15)

        if events:
            ylim = ax.get_ylim()
            for event in events['events']:
                time = datestr2num(event['start_date'])
                x = np.array([time, time])
                h = ax.plot(x, ylim, '--', label=event['class'])

            legend = ax.legend()
            if legend:
                for label in legend.get_texts():
                    label.set_fontsize(10)

        if len(qaqc) > 0:
            bad_data = np.where(qaqc > 0)
            h = ppl.plot(ax, x[bad_data], y[bad_data],
                         marker='o',
                         mfc='none',
                         linestyle='None',
                         markersize=6,
                         markeredgewidth=2,
                         mec='r')

        # plt.tick_params(axis='both', which='major', labelsize=10)
        if tick_font:
            ax.tick_params(**tick_font)
        plt.tight_layout()

    def plot_stacked_time_series(self, fig, ax, x, y, z, title='', ylabel='',
                                 cbar_title='', title_font={}, axis_font={}, tick_font = {},
                                 **kwargs):

        print '\n debug -- plot_stacked_time_series entered...'
        if not title_font:
            title_font = title_font_default
        if not axis_font:
            axis_font = axis_font_default

        # Mask NaN items in z
        print '\n debug -- plot_stacked_time_series - Mask NaN items in z'
        z = np.ma.array(z, mask=np.isnan(z))

        # create a limit for the colorbar that disregards outliers
        print '\n debug -- plot_stacked_time_series - create a limit for the colorbar that disregards outliers...'
        lim = float("%2.2f" % np.nanpercentile(abs(z), 95))

        # Test...
        h = plt.pcolormesh(x, y, z, vmin=-lim, vmax=lim, cmap='RdBu', shading='gouraud', **kwargs)
        #h = plt.pcolormesh(x, y, z, **kwargs)

        if ylabel:
            ax.set_ylabel(ylabel.replace("_", " "), **axis_font)
        if title:
            ax.set_title(title.replace("_", " "), **title_font)

        plt.axis([x.min(), x.max(), y.min(), y.max()])
        ax.xaxis_date()
        date_list = mdates.num2date(x)
        self.get_time_label(ax, date_list)
        fig.autofmt_xdate()

        # Inverts left vertical axis only
        ax.invert_yaxis()
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='3%', pad=0.05)
        cbar = plt.colorbar(h, cax=cax)
        cbar.ax.invert_yaxis()
        if cbar_title:
            cbar.ax.set_ylabel(cbar_title.replace("_", " "), **axis_font)
        ax.grid(True)
        if tick_font:
            ax.tick_params(**tick_font)
        plt.tight_layout()
        self.add_annotation(ax)


    def plot_stacked_time_series_spkir(self, fig, ax, x, y, z, title='', ylabel='',
                                 cbar_title='', title_font={}, axis_font={}, tick_font = {},
                                 **kwargs):
        print '\n debug -- plot_stacked_time_series_spkir entered...'
        if not title_font:
            title_font = title_font_default
        if not axis_font:
            axis_font = axis_font_default

        # Mask NaN items in z
        z = np.ma.array(z, mask=np.isnan(z))
        h = plt.pcolormesh(x, y, z, **kwargs)

        if ylabel:
            ax.set_ylabel(ylabel.replace("_", " "), **axis_font)
        if title:
            ax.set_title(title.replace("_", " "), **title_font)

        plt.axis([x.min(), x.max(), y.min(), y.max()])
        ax.xaxis_date()
        date_list = mdates.num2date(x)
        self.get_time_label(ax, date_list)
        fig.autofmt_xdate()

        # Inverts left vertical axis only
        ax.invert_yaxis()
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='3%', pad=0.05)
        cbar = plt.colorbar(h, cax=cax)
        cbar.ax.invert_yaxis()

        if cbar_title:
            cbar.ax.set_ylabel(cbar_title.replace("_", " "), **axis_font)
        #---------
        ax.grid(True)
        if tick_font:
            ax.tick_params(**tick_font)
        plt.tight_layout()

    '''
    def plot_stacked_time_series_zplsc(self, fig, ax, x, y, z, stacked_depth_ranges, title='', ylabel='',
                                 cbar_title='', title_font={}, axis_font={}, tick_font = {},
                                 **kwargs):
        debug = True
        if debug:
            print '\n *************************************************************'
            print '\n\t debug -- plot_stacked_time_series_zplsc Entered...'
        if not title_font:
            title_font = title_font_default
        if not axis_font:
            axis_font = axis_font_default

        if debug:
            # {'color': 'k', 'width': 1, 'labelsize': 10, 'axis': 'both'}
            print '\n\t debug -- tick_font: ', tick_font
            print '\n\t debug -- Plotting Stacked: stacked_depth_ranges [0]: ', stacked_depth_ranges[0][0:20]

        if debug:
            print '\n debug -- Initial type of z type(z): ', type(z)
            print '\n debug -- z.min(): ', z.min()
            print '\n debug -- z.max(): ', z.max()



        # Mask NaN items in z
        z = np.ma.array(z, mask=np.isnan(z))

        # Get min/max for y (5/95)
        lim_max = float("%2.2f" % np.nanpercentile(abs(z), 95))
        lim_min = float("%2.2f" % np.nanpercentile(abs(z), 5))
        if z.min() < 0:
            lim_max = -lim_max
        if z.max() < 0:
            lim_min = -lim_min
        if debug:
            print '\n debug -- ----------------------- New Limits -------------------'
            print '\n debug -- lim_min: ', lim_min
            print '\n debug -- lim_max: ', lim_max
            print '\n debug -- ------------------------------------------------------'



        """
        lim = float("%2.2f" % np.nanpercentile(abs(z), 90))     # testing - added to test

        # Test
        min_lim = float("%2.2f" % z.min())
        max_lim = float("%2.2f" % z.max())
        int_lim_min = int(round(min_lim))
        int_lim_max = int(round(max_lim))
        if debug:
            print '\n debug -- z min/max ......................'
            print '\n debug -- z.min(): ', z.min()
            print '\n debug -- z.max(): ', z.max()
            print '\n debug -- min_lim: ', min_lim
            print '\n debug -- max_lim: ', max_lim
            print '\n debug -- int_lim_min: ', int_lim_min
            print '\n debug -- int_lim_max: ', int_lim_max

        if debug:
            print '\n debug -- New limit values for plotting.......'
            if lim is None or not lim:
                if debug: print '\n debug -- lim is empty or None!   CHECK'
                print '\n debug -- type(lim): ', type(lim)
                print '\n debug -- lim: ', lim
                print '\n debug -- -lim: ', -lim
        """

        """
        # Depth processing for additional y axis (left side of plot)
        _depths = np.ma.array(stacked_depth_ranges, mask=np.isnan(stacked_depth_ranges))
        if debug:
            print '\n\t debug -- _depths.min(): ', _depths.min()
            print '\n\t debug -- _depths.max(): ', _depths.max()
            print '\n\t debug -- len(_depths): ', len(_depths)
            print '\n\t debug -- type(_depths): ', type(_depths)
            print '\n\t debug -- len(x): ', len(x)
            print '\n\t debug -- type(x): ', type(x)
            print '\n\t debug -- len(y): ', len(y)
            print '\n\t debug -- type(y): ', type(y)
            print '\n\t debug -- len(stacked_depth_ranges): ', len(stacked_depth_ranges)
            print '\n\t debug -- type(stacked_depth_ranges): ', type(stacked_depth_ranges)
            print '\n\t debug -- stacked_depth_ranges.min(): ', stacked_depth_ranges.min()
            print '\n\t debug -- stacked_depth_ranges.max(): ', stacked_depth_ranges.max()
        """

        #h = plt.pcolormesh(x, y, z, **kwargs)          Original

        ## Working with depth value for min max (wrong)
        ##vertical_min = 0.36126
        ##vertical_max = 30.26704
        ##h = plt.pcolormesh(x, y, z, vmin=vertical_min, vmax=vertical_max, **kwargs)

        ## Working with values from rene
        #vertical_min = -150
        #vertical_max = -10
        #h = plt.pcolormesh(x, y, z, vmin=vertical_min, vmax=vertical_max, **kwargs)

        """
        z_copy = z.copy()
        if debug:
            print '\n debug -- Initial type of z_copy type(z_copy): ', type(z_copy)
            print '\n debug -- z_copy.min(): ', z_copy.min()
            print '\n debug -- z_copy.max(): ', z_copy.max()
        if debug:
            print '\n debug -----------------------------------------------------------------'
            print '\n debug -- Creating new test_z 90 percent....'

        test_z = np.nanpercentile(z_copy, q=[90], axis=-1)
        if debug:
            print '\n debug -- test_z.min(): ', test_z.min()
            print '\n debug -- test_z.max(): ', test_z.max()


            #ma_test_z = np.ma.array(test_z, mask=np.isnan(test_z))
            #print '\n debug -- after masking nan for ma_test_z....type(ma_test_z): ', type(ma_test_z)
            #print '\n debug -- ma_test_z.min(): ', ma_test_z.min()
            #print '\n debug -- ma_test_z.max(): ', ma_test_z.max()

        """
        """
        # Using z 90 value min/max debug -- (test_z.min(): 73.5799163818, test_z.max():  1.03166353703)
        test_z_min_lim = float("%2.2f" % test_z.min())
        test_z_max_lim = float("%2.2f" % test_z.max())
        int_lim_min = int(round(test_z_min_lim))
        int_lim_max = int(round(test_z_max_lim))
        if debug:
            print '\n debug -- int_lim_min: ', int_lim_min
            print '\n debug -- int_lim_max: ', int_lim_max
            #print '\n debug -- len(test_z): ', len(test_z)
            #print '\n debug -- len(test_z): ', len(z)
        #h = plt.pcolormesh(x, y, z, vmin=int_lim_min, vmax=int_lim_max, **kwargs)
        """
        h = plt.pcolormesh(x, y, z, vmin=lim_min, vmax=lim_max, **kwargs)
        #h = plt.pcolormesh(x, y, z, vmin=z.min(), vmax=z.max(), **kwargs)

        # Using z value min/max (z.min():  -106.308227539, z.max():  1.46598482132)
        #h = plt.pcolormesh(x, y, z, vmin=z.min(), vmax=z.max(), **kwargs)

        # old incorrect -lim/lim
        ###h = plt.pcolormesh(x, y, z, vmin=-lim, vmax=lim, **kwargs)
        ###h = plt.pcolormesh(x, stacked_depth_ranges, z, **kwargs)

        if debug: print '\n debug -- after plt.colormesh...'
        if ylabel:
            ax.set_ylabel(ylabel.replace("_", " "), **axis_font)
        if title:
            ax.set_title(title.replace("_", " "), **title_font)

        if debug:
            print '\n debug *****************************************'
            print '\n debug -- x.min(): ', x.min()
            print '\n debug -- x.max(): ', x.max()
            print '\n debug -- y.min(): ', y.min()
            print '\n debug -- y.max(): ', y.max()
            print '\n debug -- z.min(): ', z.min()
            print '\n debug -- z.max(): ', z.max()
            print '\n debug *****************************************'

        # Test remove
        plt.axis([x.min(), x.max(), y.min(), y.max()])

        #plt.xticks(visible=False)
        #plt.axis([x.min(), x.max(), stacked_depth_ranges.max(), stacked_depth_ranges.min()])
        #plt.axis([x.min(), x.max(), y.max(), y.min(), z.min(), z.max()])  # Test flip left axis
        ax.xaxis_date()
        date_list = mdates.num2date(x)
        self.get_time_label(ax, date_list)
        fig.autofmt_xdate()

        # Inverts left vertical axis only
        ax.invert_yaxis()
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='3%', pad=0.05)
        cbar = plt.colorbar(h, cax=cax)


        """
        # Test...
        lim = float("%2.2f" % np.nanpercentile(abs(z), 90))
        h = plt.pcolormesh(x, y, z, vmin=-lim, vmax=lim, cmap='RdBu', shading='gouraud', **kwargs)
        lax = divider.append_axes('left', size='3%', pad=0.05)
        lbar = plt.colorbar(h, cax=lax, ticks=_depths, orientation='vertical')

        #cbar = plt.colorbar(lax, ticks=_depths, orientation='vertical')
        #cbar.ax.set_xticklabels(['Low', 'Medium', 'High'])  # horizontal colorbar

        #cbar.ax.invert_yaxis()     # Flips right axis color bar and labels (if used)
        """

        if cbar_title:
            cbar.ax.set_ylabel(cbar_title.replace("_", " "), **axis_font)
        #---------
        ax.grid(True)
        if tick_font:
            ax.tick_params(**tick_font)
        """
        ax.tick_params(
            axis='y',          # changes apply to the y-axis
            which='both',      # both major and minor ticks are affected
            bottom='off',      # ticks along the bottom edge are off
            top='off',         # ticks along the top edge are off
            labelbottom='off') # labels along the bottom edge are off
        """
        plt.tight_layout()
    '''

    def plot_stacked_time_series_zplsc(self, fig, ax, x, y, z, stacked_depth_ranges, title='', ylabel='',
                                 cbar_title='', title_font={}, axis_font={}, tick_font = {},
                                 **kwargs):
        debug = False
        if debug:
            print '\n *************************************************************'
            print '\n\t debug -- plot_stacked_time_series_zplsc Entered...'
        if not title_font:
            title_font = title_font_default
        if not axis_font:
            axis_font = axis_font_default

        if debug:
            # {'color': 'k', 'width': 1, 'labelsize': 10, 'axis': 'both'}
            print '\n\t debug -- tick_font: ', tick_font
            print '\n\t debug -- Plotting Stacked: stacked_depth_ranges [0]: ', stacked_depth_ranges[0][0:20]

        if debug:
            print '\n debug -- Initial type of z type(z): ', type(z)
            print '\n debug -- z.min(): ', z.min()
            print '\n debug -- z.max(): ', z.max()

        # Mask NaN items in z
        z = np.ma.array(z, mask=np.isnan(z))

        # Get min/max for y (5/95)
        lim_max = float("%2.2f" % np.nanpercentile(abs(z), 95))
        lim_min = float("%2.2f" % np.nanpercentile(abs(z), 5))
        if z.min() < 0:
            lim_max = -lim_max
        if z.max() < 0:
            lim_min = -lim_min
        if debug:
            print '\n debug -- ----------------------- New Limits -------------------'
            print '\n debug -- lim_min: ', lim_min
            print '\n debug -- lim_max: ', lim_max
            print '\n debug -- ------------------------------------------------------'


        """
        # Depth processing for additional y axis (left side of plot)
        _depths = np.ma.array(stacked_depth_ranges, mask=np.isnan(stacked_depth_ranges))
        if debug:
            print '\n\t debug -- _depths.min(): ', _depths.min()
            print '\n\t debug -- _depths.max(): ', _depths.max()
            print '\n\t debug -- len(_depths): ', len(_depths)
            print '\n\t debug -- type(_depths): ', type(_depths)
            print '\n\t debug -- len(x): ', len(x)
            print '\n\t debug -- type(x): ', type(x)
            print '\n\t debug -- len(y): ', len(y)
            print '\n\t debug -- type(y): ', type(y)
            print '\n\t debug -- len(stacked_depth_ranges): ', len(stacked_depth_ranges)
            print '\n\t debug -- type(stacked_depth_ranges): ', type(stacked_depth_ranges)
            print '\n\t debug -- stacked_depth_ranges.min(): ', stacked_depth_ranges.min()
            print '\n\t debug -- stacked_depth_ranges.max(): ', stacked_depth_ranges.max()
        """

        #h = plt.pcolormesh(x, y, z, **kwargs)          Original

        ## Working with depth value for min max (wrong)
        ##vertical_min = 0.36126
        ##vertical_max = 30.26704
        ##h = plt.pcolormesh(x, y, z, vmin=vertical_min, vmax=vertical_max, **kwargs)

        ## Working with values from rene
        #vertical_min = -150
        #vertical_max = -10
        #h = plt.pcolormesh(x, y, z, vmin=vertical_min, vmax=vertical_max, **kwargs)


        h = plt.pcolormesh(x, y, z, vmin=lim_min, vmax=lim_max, **kwargs)
        #h = plt.pcolormesh(x, y, z, vmin=z.min(), vmax=z.max(), **kwargs)

        # Using z value min/max (z.min():  -106.308227539, z.max():  1.46598482132)
        #h = plt.pcolormesh(x, y, z, vmin=z.min(), vmax=z.max(), **kwargs)

        # old incorrect -lim/lim
        ###h = plt.pcolormesh(x, y, z, vmin=-lim, vmax=lim, **kwargs)
        ###h = plt.pcolormesh(x, stacked_depth_ranges, z, **kwargs)

        if debug: print '\n debug -- after plt.colormesh...'
        if ylabel:
            ax.set_ylabel(ylabel.replace("_", " "), **axis_font)
        if title:
            ax.set_title(title.replace("_", " "), **title_font)

        if debug:
            print '\n debug *****************************************'
            print '\n debug -- x.min(): ', x.min()
            print '\n debug -- x.max(): ', x.max()
            print '\n debug -- y.min(): ', y.min()
            print '\n debug -- y.max(): ', y.max()
            print '\n debug -- z.min(): ', z.min()
            print '\n debug -- z.max(): ', z.max()
            print '\n debug *****************************************'

        # Test remove
        plt.axis([x.min(), x.max(), y.min(), y.max()])

        #plt.xticks(visible=False)
        #plt.axis([x.min(), x.max(), stacked_depth_ranges.max(), stacked_depth_ranges.min()])
        #plt.axis([x.min(), x.max(), y.max(), y.min(), z.min(), z.max()])  # Test flip left axis
        ax.xaxis_date()
        date_list = mdates.num2date(x)
        self.get_time_label(ax, date_list)
        fig.autofmt_xdate()

        # Inverts left vertical axis only
        ax.invert_yaxis()
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='3%', pad=0.05)
        cbar = plt.colorbar(h, cax=cax)

        if cbar_title:
            cbar.ax.set_ylabel(cbar_title.replace("_", " "), **axis_font)
        #---------
        ax.grid(True)
        if tick_font:
            ax.tick_params(**tick_font)
        plt.tight_layout()


    def plot_stacked_time_series_image(self, fig, ax, x, y, z, title='', ylabel='',
                                       cbar_title='', title_font={}, axis_font={}, tick_font = {},
                                       **kwargs):
        '''
        This plot is a stacked time series that uses NonUniformImage with regualrly spaced ydata from
        a linear interpolation. Designed to support FRF ADCP data.
        '''
        print '\n debug -- plot_stacked_time_series_image entered...'
        if not title_font:
            title_font = title_font_default
        if not axis_font:
            axis_font = axis_font_default
        # z = np.ma.array(z, mask=np.isnan(z))

        h = NonUniformImage(ax, interpolation='bilinear', extent=(min(x), max(x), min(y), max(y)),
                            cmap=plt.cm.jet)
        h.set_data(x, y, z)
        ax.images.append(h)
        ax.set_xlim(min(x), max(x))
        ax.set_ylim(min(y), max(y))
        # h = plt.pcolormesh(x, y, z, shading='gouraud', **kwargs)
        # h = plt.pcolormesh(x, y, z, **kwargs)
        if ylabel:
            ax.set_ylabel(ylabel, **axis_font)
        if title:
            ax.set_title(title, **title_font)
        # plt.axis('tight')
        ax.xaxis_date()
        date_list = mdates.num2date(x)
        self.get_time_label(ax, date_list)
        fig.autofmt_xdate()
        # if invert:
        ax.invert_yaxis()
        cbar = plt.colorbar(h)
        if cbar_title:
            cbar.ax.set_ylabel(cbar_title, **axis_font)

        ax.grid(True)
        if tick_font:
            ax.tick_params(**tick_font)
        # plt.show()

    def plot_profile(self, fig, ax, x, y, xlabel='', ylabel='',
                     axis_font={}, tick_font={}, scatter=False, **kwargs):

        if not axis_font:
            axis_font = axis_font_default

        if scatter:
            ppl.scatter(ax, x, y, **kwargs)
        else:
            ppl.plot(ax, x, y, **kwargs)

        if xlabel:
            ax.set_xlabel(xlabel.replace("_", " "), labelpad=5, **axis_font)
        if ylabel:
            ax.set_ylabel(ylabel.replace("_", " "), labelpad=11, **axis_font)
        if tick_font:
            ax.tick_params(**tick_font)
        ax.xaxis.set_label_position('top')  # this moves the label to the top
        ax.xaxis.set_ticks_position('top')
        ax.xaxis.get_major_locator()._nbins = 5
        ax.grid(True)
        plt.tight_layout()
        # ax.set_title(title, **title_font)

    def plot_histogram(self, ax, x, bins, title='', xlabel='', title_font={},
                       axis_font={}, tick_font={}, **kwargs):

        if not title_font:
            title_font = title_font_default
        if not axis_font:
            axis_font = axis_font_default
        x = x[~np.isnan(x)]
        ppl.hist(ax, x, bins, grid='y', **kwargs)
        if xlabel:
            ax.set_xlabel(xlabel.replace("_", " "), labelpad=10, **axis_font)
        if tick_font:
            ax.tick_params(**tick_font)
        ax.set_ylabel('No. of Occurrences', **axis_font)
        ax.set_title(title.replace("_", " "), **title_font)
        # ax.grid(True)

    # A quick way to create new windrose axes...
    def new_axes(self, figsize):
        fig = plt.figure(figsize=(figsize, figsize), facecolor='w', edgecolor='w')
        rect = [0.1, 0.1, 0.8, 0.8]
        ax = WindroseAxes(fig, rect, axisbg='w')
        fig.add_axes(ax)
        return fig, ax

    def set_legend(self, ax, label='', fontsize=8):
        """Adjust the legend box."""
         # Shrink current axis by 20%
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])

        # Put a legend to the right of the current axis
        l = ax.legend(title=label, loc='lower left', bbox_to_anchor=(1, 0))
        plt.setp(l.get_texts(), fontsize=fontsize)

    def plot_rose(self, magnitude, direction, bins=8, nsector=16, figsize=8,
                  title='', title_font={}, legend_title='', normed=True,
                  opening=0.8, edgecolor='white', fontsize=8):

        # Note:
        # title_font_default:  {'color': 'black', 'fontname': 'Arial', 'verticalalignment': 'bottom',
        # 'weight': 'bold', 'size': '18'}
        if not title_font:
            title_font = title_font_default

        if title_font['size'] > 12:
            title_font['size'] = 12

        fig, ax = self.new_axes(figsize)
        magnitude = magnitude[~np.isnan(magnitude)]
        direction = direction[~np.isnan(direction)]
        cmap = plt.cm.rainbow
        ax.bar(direction, magnitude, bins=bins, normed=normed, cmap=cmap,
               opening=opening, edgecolor=edgecolor, nsector=nsector)

        #self.set_legend(ax, legend_title, fontsize)
        self.rose_set_legend(ax, legend_title, fontsize)
        ax.set_title(title, **title_font)

        return fig

    def rose_set_legend(self, ax, label='', fontsize=8):
        """Adjust the legend box."""
         # Shrink current axis by 20%

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])

        # Put a legend to the right of the current axis
        l = ax.legend(title=label, loc='lower left', bbox_to_anchor=(1.05, 0), fontsize=12, fancybox=True)
        plt.setp(l.get_title(), fontsize='x-small')
        #plt.setp(l.get_texts(), fontsize=fontsize)
        plt.setp(l.get_texts(), fontsize=10)

    def plot_1d_quiver(self, fig, ax, time, u, v, title='', ylabel='',
                       title_font={}, axis_font={}, tick_font={}, key_units='m/s',
                       legend_title="Magnitude", start=None, end=None, **kwargs):

        if not title_font:
            title_font = title_font_default
        if not axis_font:
            axis_font = axis_font_default
        # Plot quiver
        magnitude = (u**2 + v**2)**0.5
        maxmag = max(magnitude)
        ax.set_ylim(-maxmag, maxmag)
        dx = time[-1] - time[0]

        if start and end:
            ax.set_xlim(start - 0.05 * dx, end + 0.05 * dx)
        else:
            ax.set_xlim(time[0] - 0.05 * dx, time[-1] + 0.05 * dx)
        # ax.fill_between(time, magnitude, 0, color='k', alpha=0.1)

        # # Fake 'box' to be able to insert a legend for 'Magnitude'
        # p = ax.add_patch(plt.Rectangle((1, 1), 1, 1, fc='k', alpha=0.1))
        # leg1 = ax.legend([p], [legend_title], loc='lower right')
        # leg1._drawFrame = False
        mean_val = np.mean(magnitude)
        # Quick conversion of most popular key_units
        if key_units == 'm s-1':
            key_units = 'm/s'
        key_str = '{0:.2f} {1}'.format(mean_val, key_units)

        # 1D Quiver plot
        q = ax.quiver(time, 0, u, v, **kwargs)
        plt.quiverkey(q, 0.1, 0.05, mean_val,
                      key_str,
                      labelpos='W',
                      fontproperties={'weight': 'light',
                                      'style': 'italic',
                                      'size': 'small',
                                      'stretch': 'condensed'})

        ax.xaxis_date()
        date_list = mdates.num2date(time)
        self.get_time_label(ax, date_list)
        fig.autofmt_xdate()

        if ylabel:
            ax.set_ylabel(ylabel.replace("_", " "), labelpad=20, **axis_font)
        if tick_font:
            ax.tick_params(**tick_font)
        ax.set_title(title.replace("_", " "), **title_font)
        plt.tight_layout()

    def make_patch_spines_invisible(self, ax):
        ax.set_frame_on(True)
        ax.patch.set_visible(False)
        for sp in ax.spines.itervalues():
            sp.set_visible(False)

    def set_spine_direction(self, ax, direction):
        if direction in ["right", "left"]:
            ax.yaxis.set_ticks_position(direction)
            ax.yaxis.set_label_position(direction)
        elif direction in ["top", "bottom"]:
            ax.xaxis.set_ticks_position(direction)
            ax.xaxis.set_label_position(direction)
        else:
            raise ValueError("Unknown Direction: %s" % (direction,))

        ax.spines[direction].set_visible(True)

    def plot_multiple_xaxes(self, ax, xdata, ydata, colors, ylabel='Depth (m)', title='', title_font={},
                            axis_font={}, tick_font={}, width_in=8.3, **kwargs):
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
        self.make_patch_spines_invisible(x_axis[1])
        self.set_spine_direction(x_axis[1], "top")

        offset = [1.10, -0.1, -0.20, 1.20]
        spine_directions = ["top", "bottom", "bottom", "top", "top", "bottom"]

        count = 0
        for i in range(2, n_vars):
            x_axis[i].spines[spine_directions[count]].set_position(("axes", offset[count]))
            self.make_patch_spines_invisible(x_axis[i])
            self.set_spine_direction(x_axis[i], spine_directions[count])
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
            x_axis[ind].set_xlabel(key.replace("_", " "), **axis_font)
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
        if tick_font:
            ax.tick_params(**tick_font)
        ax.set_title(title.replace("_", " "), y=1.23, **title_font)
        plt.tight_layout()

    def plot_multiple_yaxes(self, fig, ax, xdata, ydata, colors, title, units=[], scatter=False,
                            axis_font={}, title_font={}, tick_font={}, width_in=8.3, qaqc={}, **kwargs):
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
        self.make_patch_spines_invisible(y_axis[1])
        self.set_spine_direction(y_axis[1], "top")

        # Define the axes position offsets for each 'extra' axis
        spine_directions = ["left", "right", "left", "right", "left", "right"]

        # Adjust the axes left/right accordingly
        if n_vars >= 4:
            if width_in < 8.3:
                # set axis location
                offset = [1.2, -0.2, 1.40, -0.40]
                # overwrite width
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
            self.make_patch_spines_invisible(y_axis[i])
            self.set_spine_direction(y_axis[i], spine_directions[count+1])
            count += 1

        # Plot the data
        for ind, key in enumerate(ydata):

            y_axis[ind].plot(xdata[key], ydata[key], colors[ind], **kwargs)

            if len(qaqc[key]) > 0:
                bad_data = np.where(qaqc[key] > 0)
                y_axis[ind].plot(xdata[key][bad_data], ydata[key][bad_data],
                                 marker='o',
                                 mfc='none',
                                 linestyle='None',
                                 markersize=6,
                                 markeredgewidth=2,
                                 mec='r')
            # Label the y-axis and set text color:

            # Been experimenting with other ways to handle tick labels with spines
            y_axis[ind].yaxis.get_major_formatter().set_useOffset(False)

            y_axis[ind].set_ylabel(key.replace("_", " ") + ' (' + units[ind] + ')', labelpad=10, **axis_font)
            y_axis[ind].yaxis.label.set_color(colors[ind])
            y_axis[ind].spines[spine_directions[ind]].set_color(colors[ind])
            if tick_font:
                labelsize = tick_font['labelsize']
            y_axis[ind].tick_params(axis='y', labelsize=labelsize, colors=colors[ind])

        self.get_time_label(ax, xdata['time'])
        fig.autofmt_xdate()

        # ax.tick_params(axis='x', labelsize=10)
        ax.set_title(title.replace("_", " "), y=1.05, **title_font)
        ax.grid(True)
        plt.tight_layout()

    def plot_multiple_streams(self, fig, ax, datasets, colors, axis_font={}, title_font={},
                              tick_font={}, width_in=8.3 , plot_qaqc=0, scatter=False, **kwargs):
        # Plot a timeseries with multiple y-axes using multiple streams from uFrame
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

        n_vars = len(datasets)
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
        self.make_patch_spines_invisible(y_axis[1])
        self.set_spine_direction(y_axis[1], "top")

        # Define the axes position offsets for each 'extra' axis
        spine_directions = ["left", "right", "left", "right", "left", "right"]

        # Adjust the axes left/right accordingly
        if n_vars >= 4:
            if width_in < 8.3:
                # set axis location
                offset = [1.2, -0.2, 1.40, -0.40]
                # overwrite width
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
            self.make_patch_spines_invisible(y_axis[i])
            self.set_spine_direction(y_axis[i], spine_directions[count+1])
            count += 1

        # Plot the data
        legend_handles = []
        legend_labels = []

        for ind, data in enumerate(datasets):
            xlabel = data['x_field'][0]
            ylabel = data['y_field'][0]
            xdata = data['x'][xlabel]
            ydata = data['y'][ylabel]

            # Handle the QAQC data
            qaqc = data['qaqc'][ylabel]
            if plot_qaqc >= 10:
                # Plot all of the qaqc flags results
                # qaqc_data = data['qaqc'][ylabel]
                pass
            elif plot_qaqc >= 1:
                # This is a case where the user wants to plot just one of the 9 QAQC tests
                ind = np.where(qaqc != plot_qaqc)
                qaqc[ind] = 0

            else:
                qaqc = []

            h, = y_axis[ind].plot(xdata, ydata, colors[ind], label=data['title'], **kwargs)
            if len(qaqc) > 0:
                bad_data = np.where(qaqc > 0)
                y_axis[ind].plot(xdata[bad_data], ydata[bad_data],
                                 marker='o',
                                 mfc='none',
                                 linestyle='None',
                                 markersize=6,
                                 markeredgewidth=2,
                                 mec='r')

            # Label the y-axis and set text color:
            # Been experimenting with other ways to handle tick labels with spines
            y_axis[ind].yaxis.get_major_formatter().set_useOffset(False)

            y_axis[ind].set_ylabel(ylabel.replace("_", " "), labelpad=10, **axis_font)
            y_axis[ind].yaxis.label.set_color(colors[ind])
            y_axis[ind].spines[spine_directions[ind]].set_color(colors[ind])
            if tick_font:
                labelsize = tick_font['labelsize']
            y_axis[ind].tick_params(axis='y', labelsize=labelsize, colors=colors[ind])
            legend_handles.append(h)
            legend_labels.append(data['title'][0:20])

        self.get_time_label(ax, xdata)
        fig.autofmt_xdate()

        ax.legend(legend_handles, legend_labels)

        # ax.tick_params(axis='x', labelsize=10)
        # ax.set_title(title.replace("_", " "), y=1.05, **title_font)
        ax.grid(True)
        plt.tight_layout()

    def plot_ts_diagram(self, ax, sal, temp, xlabel='Salinity', ylabel='Temperature', title='',
                        axis_font={}, title_font={}, tick_font={}, **kwargs):

        if not axis_font:
            axis_font = axis_font_default
        if not title_font:
            title_font = title_font_default

        sal = np.ma.array(sal, mask=np.isnan(sal))
        temp = np.ma.array(temp, mask=np.isnan(temp))
        if len(sal) != len(temp):
            raise Exception('Sal and Temp arrays are not the same size.')

        # Figure out boundaries (mins and maxs)
        smin = sal.min() - (0.01 * sal.min())
        smax = sal.max() + (0.01 * sal.max())
        tmin = temp.min() - (0.1 * temp.max())
        tmax = temp.max() + (0.1 * temp.max())

        # Calculate how many gridcells we need in the x and y dimensions
        xdim = round((smax-smin)/0.1+1, 0)
        ydim = round((tmax-tmin)+1, 0)

        # Create empty grid of zeros
        dens = np.zeros((ydim, xdim))

        # Create temp and sal vectors of appropriate dimensions.
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

        ax.set_xlabel(xlabel.replace("_", " "), labelpad=10, **axis_font)
        ax.set_ylabel(ylabel.replace("_", " "), labelpad=10, **axis_font)
        ax.set_title(title.replace("_", " "), **title_font)
        ax.set_aspect(1./ax.get_data_ratio())  # make axes square
        if tick_font:
            ax.tick_params(**tick_font)
        plt.tight_layout()

    def plot_3d_scatter(self, fig, ax, x, y, z, title='', xlabel='', ylabel='', zlabel='',
                        title_font={}, axis_font={}, tick_font={}, number_points=0):

        # {'color': 'black', 'fontname': 'Calibri', 'weight': 'bold', 'size': 12}
        if not title_font:
            title_font = title_font_default
        if title_font['size'] < 14:
            title_font['size'] = 14

        # Format {'fontname': 'Calibri', 'weight': 'bold', 'size': 10}
        if not axis_font:
            axis_font = axis_font_default
        if axis_font['size'] < 12:
            axis_font['size'] = 12
        # Format tick font: {'color': 'k', 'width': 1, 'labelsize': 7, 'axis': 'both'}

        """
        print '\n debug -- plot_tools.py: 3d_scatter: xlabel: ', xlabel
        print '\n debug -- plot_tools.py: 3d_scatter: ylabel: ', ylabel
        print '\n debug -- plot_tools.py: 3d_scatter: zlabel: ', zlabel
        x_display_label = None
        if xlabel is not None:
            x_display_label = xlabel[:]
        """

        # http://stackoverflow.com/questions/2051744/reverse-y-axis-in-pyplot
        cmap = plt.cm.jet
        h = plt.scatter(x, y, c=z, cmap=cmap)
        ax = plt.gca()
        """
        print '\n ax.get_ylim(): ', ax.get_ylim()
        print '\n ax.get_ylim()[::-1]: ', ax.get_ylim()[::-1]
        """
        ax.set_ylim(ax.get_ylim()[::-1])
        # testing -- h = plt.scatter(x, y, c=z, cmap=cmap)

        """
        # original two lines
        cmap = plt.cm.jet
        h = ax.scatter(x, y, c=z, cmap=cmap)
        """

        if 'time' in xlabel.lower():
            xlabel = None
            ax.xaxis_date()
            date_list = mdates.num2date(x)
            self.get_time_label(ax, date_list)
            fig.autofmt_xdate()

        ax.set_aspect(1. / ax.get_data_ratio())  # make axes square
        #cbar = plt.colorbar(h, orientation='vertical', aspect=30, shrink=0.76)
        cbar = plt.colorbar(h, orientation='vertical', aspect=30, shrink=0.76)

        """
        if x_display_label:
            ax.set_xlabel(x_display_label, labelpad=10, **axis_font)

        if xlabel:
            ax.set_xlabel(xlabel.replace("_", " "), labelpad=10, **axis_font)
        """
        if ylabel:
            ax.set_ylabel(ylabel.replace("_", " "), labelpad=10, **axis_font)
        if zlabel:
            cbar.ax.set_ylabel(zlabel.replace("_", " "), **axis_font)
        if tick_font:
            ax.tick_params(**tick_font)
        if title:
            ax.set_title(title.replace("_", " "), **title_font)
        if number_points:
            nice_number = "{:,}".format(number_points)
            message = 'Number of data points: %s' % nice_number
            self.add_annotation_message(ax, message)
        ax.grid(True)
        plt.tight_layout()


    def add_annotation_message(self, ax, message):
        """
        This method adds annotation to the plot figure in the lower left corner.
        """
        annotation = message
        ax.annotate(annotation, xy=(40, 10), xycoords='figure pixels',
                    horizontalalignment='left', verticalalignment='bottom', fontsize=8, style='italic')
