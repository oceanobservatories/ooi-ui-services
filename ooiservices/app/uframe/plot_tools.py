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
        day_delta = (max(dates)-min(dates)).days

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

    def plot_time_series(self, fig, is_timeseries, ax, x, y, fill=False, title='', xlabel='', ylabel='',
                         title_font={}, axis_font={}, tick_font={}, scatter=False, qaqc=[], events={}, **kwargs):

        if not title_font:
            title_font = title_font_default
        if not axis_font:
            axis_font = axis_font_default

        if scatter:
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
                ax.fill_between(x, y, miny+1e-7, facecolor = h[0].get_color(), alpha=0.15)
            else:
                ax.fill_between(x, y, miny+1e-7, facecolor = axis_font_default['color'], alpha=0.15)

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

        if not title_font:
            title_font = title_font_default
        if not axis_font:
            axis_font = axis_font_default
        z = np.ma.array(z, mask=np.isnan(z))
        h = plt.pcolormesh(x, y, z, shading='gouraud', **kwargs)
        # h = plt.pcolormesh(x, y, z, **kwargs)
        if ylabel:
            ax.set_ylabel(ylabel.replace("_", " "), **axis_font)
        if title:
            ax.set_title(title.replace("_", " "), **title_font)
        plt.axis([x.min(), x.max(), y.min(), y.max()])
        ax.xaxis_date()
        date_list = mdates.num2date(x)
        self.get_time_label(ax, date_list)
        fig.autofmt_xdate()
        ax.invert_yaxis()
        cbar = plt.colorbar(h)
        if cbar_title:
            cbar.ax.set_ylabel(cbar_title)
        ax.grid(True)
        if tick_font:
            ax.tick_params(**tick_font)
        plt.tight_layout()

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

        if not title_font:
            title_font = title_font_default

        fig, ax = self.new_axes(figsize)
        magnitude = magnitude[~np.isnan(magnitude)]
        direction = direction[~np.isnan(direction)]
        cmap = plt.cm.rainbow
        ax.bar(direction, magnitude, bins=bins, normed=normed, cmap=cmap,
               opening=opening, edgecolor=edgecolor, nsector=nsector)

        self.set_legend(ax, legend_title, fontsize)
        ax.set_title(title.replace("_", " "), **title_font)

        return fig

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

        ax.set_xlabel(xlabel.replace("_", " "), labelpad=10, **axis_font)
        ax.set_ylabel(ylabel.replace("_", " "), labelpad=10, **axis_font)
        ax.set_title(title.replace("_", " "), **title_font)
        ax.set_aspect(1./ax.get_data_ratio())  # make axes square
        if tick_font:
            ax.tick_params(**tick_font)
        plt.tight_layout()

    def plot_3d_scatter(self, fig, ax, x, y, z, title='', xlabel='', ylabel='', zlabel='',
                        title_font={}, axis_font={}, tick_font={}):

        if not title_font:
            title_font = title_font_default
        if not axis_font:
            axis_font = axis_font_default

        cmap = plt.cm.jet
        h = plt.scatter(x, y, c=z, cmap=cmap)
        ax.set_aspect(1./ax.get_data_ratio())  # make axes square
        cbar = plt.colorbar(h, orientation='vertical', aspect=30, shrink=0.9)

        if xlabel:
            ax.set_xlabel(xlabel.replace("_", " "), labelpad=10, **axis_font)
        if ylabel:
            ax.set_ylabel(ylabel.replace("_", " "), labelpad=10, **axis_font)
        if zlabel:
            cbar.ax.set_ylabel(zlabel.replace("_", " "), labelpad=10, **axis_font)
        if tick_font:
            ax.tick_params(**tick_font)
        if title:
            ax.set_title(title.replace("_", " "), **title_font)
        ax.grid(True)
        plt.tight_layout()
