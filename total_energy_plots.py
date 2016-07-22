#!/usr/bin/env python
import Tkinter as Tk
import ttk as ttk
import matplotlib
import numpy as np
import numpy.ma as ma
import new_cmaps
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as PathEffects

class TotEnergyPanel:
    # A dictionary of all of the parameters for this plot with the default parameters

    plot_param_dict = {'twoD': 0,
                       'show_prtl_KE': True,
                       'show_field_E': True,
                       'y_min': 0,
                       'y_max' : 10,
                       'set_y_min': False,
                       'set_y_max': False,
                       'show_legend': True,
                       'x_min': 0,
                       'x_max' : 10,
                       'set_x_min': False,
                       'set_x_max': False,
                       'yLog': True,
                       'spatial_x': False,
                       'spatial_y': False}

    # We need the types of all the parameters for the config file
    BoolList = ['twoD', 'set_y_min', 'set_y_max','show_prtl_KE', 'show_field_E',
                'yLog', 'spatial_x', 'spatial_y', 'set_x_min', 'set_x_max', 'show_legend']
    IntList = ['E_type']
    FloatList = ['y_min', 'y_max','x_min', 'x_max']
    StrList = []

    def __init__(self, parent, figwrapper):
        self.settings_window = None
        self.FigWrap = figwrapper
        self.parent = parent
        self.ChartTypes = self.FigWrap.PlotTypeDict.keys()
        self.chartType = self.FigWrap.chartType
        self.figure = self.FigWrap.figure
    def ChangePlotType(self, str_arg):
        self.FigWrap.ChangeGraph(str_arg)

    def set_plot_keys(self):
        '''A helper function that will insure that each hdf5 file will only be
        opened once per time step'''
        # First make sure that omega_plasma & xi is loaded so we can fix the
        # distances. We need all 3 magnetic field directions to calculate the FFT
        # or Chi
        self.arrs_needed = []
        return self.arrs_needed

    def LoadData(self):
        ''' A Helper function that loads the data for the plot'''
        # We don't need to do anything here, but we still need this function defined
        pass

    def LimFinder(self, arr, isLog = False):
        oneD_lims = [arr.min(), arr.max()]
        # now give it a bit of spacing, a 4% percent difference of the distance
        dist = oneD_lims[1]-oneD_lims[0]

        if isLog:
            oneD_lims[0] *= .5
            oneD_lims[1] *= 2
        else:
            oneD_lims[0] -= 0.04*dist
            oneD_lims[1] += 0.04*dist
        return oneD_lims

    def draw(self):

        ''' A function that draws the data. In the interest in speeding up the
        code, draw should only be called when you want to recreate the whole
        figure, i.e. it  will be slow. Most times you will only want to update
        what has changed in the figure. This will be done in a function called
        refresh, that should be much much faster.'''

        # Set the tick color
        tick_color = 'black'

        # Create a gridspec to handle spacing better
        self.gs = gridspec.GridSpecFromSubplotSpec(100,100, subplot_spec = self.parent.gs0[self.FigWrap.pos])
        self.axes = self.figure.add_subplot(self.gs[self.parent.axes_extent[0]:self.parent.axes_extent[1], self.parent.axes_extent[2]:self.parent.axes_extent[3]])

        self.prtlcolor = new_cmaps.cmaps[self.parent.MainParamDict['ColorMap']](0.2)
        self.fieldcolor = new_cmaps.cmaps[self.parent.MainParamDict['ColorMap']](0.8)

        self.prtl_plot = self.axes.plot(self.parent.TotalEnergyTimes, self.parent.TotalPrtlEnergy, ls= ':', marker = 'd', markeredgecolor = self.prtlcolor, color = self.prtlcolor)
        if not self.GetPlotParam('show_prtl_KE'):
            self.prtl_plot[0].set_visible(False)
        self.field_plot = self.axes.plot(self.parent.TotalEnergyTimes, self.parent.TotalMagEnergy, ls= ':', marker = '8', markeredgecolor = self.fieldcolor, color = self.fieldcolor)
        if not self.GetPlotParam('show_field_E'):
            self.field_plot[0].set_visible(False)

        self.axes.set_axis_bgcolor('lightgrey')
        self.axes.tick_params(labelsize = self.parent.MainParamDict['NumFontSize'], color=tick_color)


        if self.GetPlotParam('yLog'):
            self.axes.set_yscale('log')
        tmp_y_lims = []
        if self.GetPlotParam('show_prtl_KE'):
            tmp_y_lims = self.LimFinder(self.parent.TotalPrtlEnergy, self.GetPlotParam('yLog'))
        if self.GetPlotParam('show_field_E'):
            if len(tmp_y_lims) ==0:
                tmp_y_lims = self.LimFinder(self.parent.TotalMagEnergy, self.GetPlotParam('yLog'))
            else:
                tmp_y_lims[0] = min(tmp_y_lims[0],self.LimFinder(self.parent.TotalMagEnergy, self.GetPlotParam('yLog'))[0])
                tmp_y_lims[1] = max(tmp_y_lims[1],self.LimFinder(self.parent.TotalMagEnergy, self.GetPlotParam('yLog'))[1])
        self.axes.set_ylim(tmp_y_lims)
        if self.GetPlotParam('set_y_min'):
            self.axes.set_ylim(ymin = self.GetPlotParam('y_min'))
        if self.GetPlotParam('set_y_max'):
            self.axes.set_ylim(ymax = self.GetPlotParam('y_max'))

        if self.GetPlotParam('set_x_min'):
            self.axes.set_xlim(xmin = self.GetPlotParam('x_min'))
        if self.GetPlotParam('set_x_max'):
            self.axes.set_xlim(xmax = self.GetPlotParam('x_max'))
        if self.GetPlotParam('show_legend'):
            # now make the total energy legend
            legend_handles = []
            legend_labels = []

            if self.GetPlotParam('show_prtl_KE'):
                legend_handles.append(self.prtl_plot[0])
                legend_labels.append('Particles')
            if self.GetPlotParam('show_field_E'):
                legend_handles.append(self.field_plot[0])
                legend_labels.append('EM Fields')
            self.legend = self.axes.legend(legend_handles, legend_labels,
            framealpha = .05, fontsize = 11, loc = 'best')
            self.legend.get_frame().set_facecolor('k')
            self.legend.get_frame().set_linewidth(0.0)

        self.axes.set_xlabel(r'$t\ \  [\omega^{-1}_{pe}]$', labelpad = self.parent.MainParamDict['xLabelPad'], color = 'black')
        self.axes.set_ylabel('Energy Density', labelpad = self.parent.MainParamDict['yLabelPad'], color = 'black')

    def refresh(self):

        '''This is a function that will be called only if self.axes already
        holds a total energy type plot. We only update things that have changed & are
        shown.  If hasn't changed or isn't shown, don't touch it. The difference
        between this and last time, is that we won't actually do any drawing in
        the plot. The plot will be redrawn after all subplots are refreshed. '''


        # Main goal, only change what is showing..

        self.prtl_plot[0].set_data(self.parent.TotalEnergyTimes, self.parent.TotalPrtlEnergy)
        self.field_plot[0].set_data(self.parent.TotalEnergyTimes, self.parent.TotalMagEnergy)
        tmp_y_lims = []
        if self.GetPlotParam('show_prtl_KE'):
            tmp_y_lims = self.LimFinder(self.parent.TotalPrtlEnergy, self.GetPlotParam('yLog'))
        if self.GetPlotParam('show_field_E'):
            if len(tmp_y_lims) ==0:
                tmp_y_lims = self.LimFinder(self.parent.TotalMagEnergy, self.GetPlotParam('yLog'))
            else:
                tmp_y_lims[0] = min(tmp_y_lims[0],self.LimFinder(self.parent.TotalMagEnergy, self.GetPlotParam('yLog'))[0])
                tmp_y_lims[1] = max(tmp_y_lims[1],self.LimFinder(self.parent.TotalMagEnergy, self.GetPlotParam('yLog'))[1])
        self.axes.set_ylim(tmp_y_lims)
        if self.GetPlotParam('set_y_min'):
            self.axes.set_ylim(ymin = self.GetPlotParam('y_min'))
        if self.GetPlotParam('set_y_max'):
            self.axes.set_ylim(ymax = self.GetPlotParam('y_max'))

        self.axes.set_xlim(self.LimFinder(self.parent.TotalEnergyTimes))
        if self.GetPlotParam('set_x_min'):
            self.axes.set_xlim(xmin = self.GetPlotParam('x_min'))
        if self.GetPlotParam('set_x_max'):
            self.axes.set_xlim(xmax = self.GetPlotParam('x_max'))


        # now make the total energy legend
        legend_handles = []
        legend_labels = []

        if self.GetPlotParam('show_prtl_KE'):
            legend_handles.append(self.prtl_plot[0])
            legend_labels.append('Particles')
        if self.GetPlotParam('show_field_E'):
            legend_handles.append(self.field_plot[0])
            legend_labels.append('EM Fields')
        self.legend = self.axes.legend(legend_handles, legend_labels,
        framealpha = .05, fontsize = 11, loc = 'best')
        self.legend.get_frame().set_facecolor('k')
        self.legend.get_frame().set_linewidth(0.0)
        self.legend.set_visible(self.GetPlotParam('show_legend'))


    def GetPlotParam(self, keyname):
        return self.FigWrap.GetPlotParam(keyname)

    def SetPlotParam(self, keyname, value, update_plot = True):
        self.FigWrap.SetPlotParam(keyname, value, update_plot = update_plot)

    def OpenSettings(self):
        if self.settings_window is None:
            self.settings_window = TotEnergySettings(self)
        else:
            self.settings_window.destroy()
            self.settings_window = TotEnergySettings(self)


class TotEnergySettings(Tk.Toplevel):
    def __init__(self, parent):
        self.parent = parent
        Tk.Toplevel.__init__(self)

        self.wm_title('TotEnergy (%d,%d) Settings' % self.parent.FigWrap.pos)
        self.parent = parent
        frm = ttk.Frame(self)
        frm.pack(fill=Tk.BOTH, expand=True)
        self.protocol('WM_DELETE_WINDOW', self.OnClosing)
        self.bind('<Return>', self.TxtEnter)

        # Create the OptionMenu to chooses the Chart Type:
        self.ctypevar = Tk.StringVar(self)
        self.ctypevar.set(self.parent.chartType) # default value
        self.ctypevar.trace('w', self.ctypeChanged)

        ttk.Label(frm, text="Choose Chart Type:").grid(row=0, column = 0)
        ctypeChooser = apply(ttk.OptionMenu, (frm, self.ctypevar, self.parent.chartType) + tuple(self.parent.ChartTypes))
        ctypeChooser.grid(row =0, column = 1, sticky = Tk.W + Tk.E)

        # the Check boxes for the dimension
        ttk.Label(frm, text='Dimenison:').grid(row = 1, column = 0, sticky = Tk.W)

        self.ShowPrtlVar = Tk.IntVar(self) # Create a var to track whether or not to show X
        self.ShowPrtlVar.set(self.parent.GetPlotParam('show_prtl_KE'))
        cb = ttk.Checkbutton(frm, text = "Show Prtl Energy",
            variable = self.ShowPrtlVar,
            command = self.Selector)
        cb.grid(row = 2, column = 0, sticky = Tk.W)

        self.ShowFieldVar = Tk.IntVar(self) # Create a var to track whether or not to plot Y
        self.ShowFieldVar.set(self.parent.GetPlotParam('show_field_E'))
        cb = ttk.Checkbutton(frm, text = "Show E&M Energy",
            variable = self.ShowFieldVar,
            command = self.Selector)
        cb.grid(row = 3, column = 0, sticky = Tk.W)



        # Now the x & y lim
        self.setZminVar = Tk.IntVar()
        self.setZminVar.set(self.parent.GetPlotParam('set_y_min'))
        self.setZminVar.trace('w', self.setZminChanged)

        self.setZmaxVar = Tk.IntVar()
        self.setZmaxVar.set(self.parent.GetPlotParam('set_y_max'))
        self.setZmaxVar.trace('w', self.setZmaxChanged)



        self.Zmin = Tk.StringVar()
        self.Zmin.set(str(self.parent.GetPlotParam('y_min')))

        self.Zmax = Tk.StringVar()
        self.Zmax.set(str(self.parent.GetPlotParam('y_max')))


        cb = ttk.Checkbutton(frm, text ='Set y min',
                        variable = self.setZminVar)
        cb.grid(row = 2, column = 2, sticky = Tk.W)
        self.ZminEnter = ttk.Entry(frm, textvariable=self.Zmin, width=7)
        self.ZminEnter.grid(row = 2, column = 3)

        cb = ttk.Checkbutton(frm, text ='Set y max',
                        variable = self.setZmaxVar)
        cb.grid(row = 3, column = 2, sticky = Tk.W)

        self.ZmaxEnter = ttk.Entry(frm, textvariable=self.Zmax, width=7)
        self.ZmaxEnter.grid(row = 3, column = 3)

        self.setXminVar = Tk.IntVar()
        self.setXminVar.set(self.parent.GetPlotParam('set_x_min'))
        self.setXminVar.trace('w', self.setXminChanged)

        self.setXmaxVar = Tk.IntVar()
        self.setXmaxVar.set(self.parent.GetPlotParam('set_x_max'))
        self.setXmaxVar.trace('w', self.setXmaxChanged)



        self.Xmin = Tk.StringVar()
        self.Xmin.set(str(self.parent.GetPlotParam('x_min')))

        self.Xmax = Tk.StringVar()
        self.Xmax.set(str(self.parent.GetPlotParam('x_max')))


        cb = ttk.Checkbutton(frm, text ='Set x min',
                        variable = self.setXminVar)
        cb.grid(row = 4, column = 2, sticky = Tk.W)
        self.XminEnter = ttk.Entry(frm, textvariable=self.Xmin, width=7)
        self.XminEnter.grid(row = 4, column = 3)

        cb = ttk.Checkbutton(frm, text ='Set x max',
                        variable = self.setXmaxVar)
        cb.grid(row = 5, column = 2, sticky = Tk.W)

        self.XmaxEnter = ttk.Entry(frm, textvariable=self.Xmax, width=7)
        self.XmaxEnter.grid(row = 5, column = 3)


        # Now whether or not the y axes should be in logspace

        self.yLogVar = Tk.IntVar()
        self.yLogVar.set(self.parent.GetPlotParam('yLog'))
        self.yLogVar.trace('w', self.yLogChanged)



        cb = ttk.Checkbutton(frm, text ='y-axis logscale',
                        variable = self.yLogVar)
        cb.grid(row = 4, column = 0, sticky = Tk.W)

        self.LegendVar = Tk.IntVar()
        self.LegendVar.set(self.parent.GetPlotParam('show_legend'))
        self.LegendVar.trace('w', self.showLegendChanged)



        cb = ttk.Checkbutton(frm, text ='Show legend',
                        variable = self.LegendVar)
        cb.grid(row = 4, column = 1, sticky = Tk.W)




    def ctypeChanged(self, *args):
        if self.ctypevar.get() == self.parent.chartType:
            pass
        else:
            self.parent.ChangePlotType(self.ctypevar.get())
            self.destroy()

    def setZminChanged(self, *args):
        if self.setZminVar.get() == self.parent.GetPlotParam('set_y_min'):
            pass
        else:
            self.parent.SetPlotParam('set_y_min', self.setZminVar.get())

    def setZmaxChanged(self, *args):
        if self.setZmaxVar.get() == self.parent.GetPlotParam('set_y_max'):
            pass
        else:
            self.parent.SetPlotParam('set_y_max', self.setZmaxVar.get())

    def setXminChanged(self, *args):
        if self.setXminVar.get() == self.parent.GetPlotParam('set_x_min'):
            pass
        else:
            self.parent.SetPlotParam('set_x_min', self.setXminVar.get())

    def setXmaxChanged(self, *args):
        if self.setXmaxVar.get() == self.parent.GetPlotParam('set_x_max'):
            pass
        else:
            self.parent.SetPlotParam('set_x_max', self.setXmaxVar.get())


    def yLogChanged(self, *args):
        if self.yLogVar.get() == self.parent.GetPlotParam('yLog'):
            pass
        else:
            if self.yLogVar.get():
                self.parent.axes.set_yscale('log')
            else:
                self.parent.axes.set_yscale('linear')

            self.parent.SetPlotParam('yLog', self.yLogVar.get())

    def showLegendChanged(self, *args):
        if self.LegendVar.get() == self.parent.GetPlotParam('show_legend'):
            pass
        else:
            self.parent.SetPlotParam('show_legend', self.LegendVar.get())

    def Selector(self):
        # First check if it is 2-D:
        if self.parent.GetPlotParam('show_prtl_KE') != self.ShowPrtlVar.get():
            self.parent.prtl_plot[0].set_visible(self.ShowPrtlVar.get())
            self.parent.SetPlotParam('show_prtl_KE', self.ShowPrtlVar.get())

        elif self.parent.GetPlotParam('show_field_E') != self.ShowFieldVar.get():
            self.parent.field_plot[0].set_visible(self.ShowFieldVar.get())
            self.parent.SetPlotParam('show_field_E', self.ShowFieldVar.get())


    def TxtEnter(self, e):
        self.FieldsCallback()

    def FieldsCallback(self):
        tkvarLimList = [self.Zmin, self.Zmax, self.Xmin, self.Xmax]
        plot_param_List = ['y_min', 'y_max', 'x_min', 'x_max']
        tkvarSetList = [self.setZminVar, self.setZmaxVar, self.setXminVar, self.setXmaxVar]
        to_reload = False
        for j in range(len(tkvarLimList)):
            try:
            #make sure the user types in a int
                if np.abs(float(tkvarLimList[j].get()) - self.parent.GetPlotParam(plot_param_List[j])) > 1E-4:
                    self.parent.SetPlotParam(plot_param_List[j], float(tkvarLimList[j].get()), update_plot = False)
                    to_reload += True*tkvarSetList[j].get()

            except ValueError:
                #if they type in random stuff, just set it ot the param value
                tkvarLimList[j].set(str(self.parent.GetPlotParam(plot_param_List[j])))
        if to_reload:
            self.parent.SetPlotParam('y_min', self.parent.GetPlotParam('y_min'))


    def OnClosing(self):
        self.parent.settings_window = None
        self.destroy()