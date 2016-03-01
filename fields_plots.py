#!/usr/bin/env pythonw
import Tkinter as Tk
import ttk as ttk
import matplotlib
import numpy as np
import numpy.ma as ma
import new_cmaps
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as PathEffects

class FieldsPanel:
    # A diction of all of the parameters for this plot with the default parameters

    plot_param_dict = {'twoD': 0,
                       'field_type': 0, #0 = B-Field, 1 = E-field
                       'show_x' : 1,
                       'show_y' : 1,
                       'show_z' : 1,
                       'show_cbar': True,
                       'set_color_limits': False,
                       'z_min': None,
                       'z_max' : None,
                       'OutlineText': True,
                       'interpolation': 'hermite'}

    def __init__(self, parent, figwrapper):
        self.settings_window = None
        self.FigWrap = figwrapper
        self.parent = parent
        self.ChartTypes = self.FigWrap.PlotTypeDict.keys()
        self.chartType = self.FigWrap.chartType
        self.figure = self.FigWrap.figure
        self.InterpolationMethods = ['nearest', 'bilinear', 'bicubic', 'spline16',
            'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
            'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']


    def ChangePlotType(self, str_arg):
        self.FigWrap.ChangeGraph(str_arg)

    def set_plot_keys(self):
        '''A helper function that will insure that each hdf5 file will only be
        opened once per time step'''
        # First make sure that omega_plasma & xi is loaded so we can fix the
        # x & y distances.

        self.arrs_needed = ['c_omp', 'istep', 'sizex']
        # Then see if we are plotting E-field or B-Field
        if self.GetPlotParam('field_type') == 0: # Load the B-Field
            if self.GetPlotParam('show_x'):
                self.arrs_needed.append('bx')
            if self.GetPlotParam('show_y'):
                self.arrs_needed.append('by')
            if self.GetPlotParam('show_z'):
                self.arrs_needed.append('bz')

        if self.GetPlotParam('field_type') == 1: # Load the E-Field
            if self.GetPlotParam('show_x'):
                self.arrs_needed.append('ex')
            if self.GetPlotParam('show_y'):
                self.arrs_needed.append('ey')
            if self.GetPlotParam('show_z'):
                self.arrs_needed.append('ez')

        return self.arrs_needed

    def draw(self):
        # Get the x, y, and z colors from the colormap
        self.xcolor = new_cmaps.cmaps[self.parent.cmap](0.2)
        self.ycolor = new_cmaps.cmaps[self.parent.cmap](0.5)
        self.zcolor = new_cmaps.cmaps[self.parent.cmap](0.8)


        self.c_omp = self.FigWrap.LoadKey('c_omp')[0]
        self.istep = self.FigWrap.LoadKey('istep')[0]

        if self.GetPlotParam('OutlineText'):
            self.annotate_kwargs = {'horizontalalignment': 'right',
            'verticalalignment': 'top',
            'size' : 18,
            'path_effects' : [PathEffects.withStroke(linewidth=1.5,foreground="k")]
            }
        else:
            self.annotate_kwargs = {'horizontalalignment' : 'right',
            'verticalalignment' : 'top',
            'size' : 18}

        # Set the tick color
        tick_color = 'black'

        # Create a gridspec to handle spacing better
        self.gs = gridspec.GridSpecFromSubplotSpec(100,100, subplot_spec = self.parent.gs0[self.FigWrap.pos])#, bottom=0.2,left=0.1,right=0.95, top = 0.95)

        self.fx = None
        self.fy = None
        self.fz = None

        if self.GetPlotParam('field_type') == 0: # Load the B-Field
            if self.GetPlotParam('show_x'):
                self.fx = self.FigWrap.LoadKey('bx')[0,:,:]
            if self.GetPlotParam('show_y'):
                self.fy = self.FigWrap.LoadKey('by')[0,:,:]
            if self.GetPlotParam('show_z'):
                self.fz = self.FigWrap.LoadKey('bz')[0,:,:]

        if self.GetPlotParam('field_type') == 1: # Load the e-Field
            if self.GetPlotParam('show_x'):
                self.fx = self.FigWrap.LoadKey('ex')[0,:,:]
            if self.GetPlotParam('show_y'):
                self.fy = self.FigWrap.LoadKey('ey')[0,:,:]
            if self.GetPlotParam('show_z'):
                self.fz = self.FigWrap.LoadKey('ez')[0,:,:]

        # Generate the x and y axes
        if self.GetPlotParam('show_x'):
            self.y_values =  np.arange(self.fx.shape[0])/self.c_omp*self.istep
            self.x_values =  np.arange(self.fx.shape[1])/self.c_omp*self.istep

        elif self.GetPlotParam('show_y'):
            self.y_values =  np.arange(self.fy.shape[0])/self.c_omp*self.istep
            self.x_values =  np.arange(self.fy.shape[1])/self.c_omp*self.istep


        elif self.GetPlotParam('show_z'):
            self.y_values =  np.arange(self.fz.shape[0])/self.c_omp*self.istep
            self.x_values =  np.arange(self.fz.shape[1])/self.c_omp*self.istep

        self.axes = self.figure.add_subplot(self.gs[18:92,:])

        self.zval = None
        # Now that the data is loaded, start making the plots
        if self.GetPlotParam('twoD'):
            # First choose the 'zval' to plot, we can only do one because it is 2-d.
            if self.GetPlotParam('show_x'):
                self.zval = self.fx
                self.two_d_labels = (r'$B_x$', r'$E_x$')

                # set the other plot values to zero in the PlotParams
                self.SetPlotParam('show_y', 0, update_plot = False)
                self.SetPlotParam('show_z', 0, update_plot = False)

            elif self.GetPlotParam('show_y'):
                self.zval = self.fy
                self.two_d_labels = (r'$B_y$', r'$E_y$')

                # set the other plot values to zero in the PlotParams
                self.SetPlotParam('show_x', 0, update_plot = False)
                self.SetPlotParam('show_z', 0, update_plot = False)

            else:
                # make sure z is loaded, (something has to be)
                # set the other plot values to zero in the PlotParams
                self.SetPlotParam('show_x', 0, update_plot = False)
                self.SetPlotParam('show_y', 0, update_plot = False)

                # set show_z to 1 to be consistent
                self.SetPlotParam('show_z', 1, update_plot = False)

                self.zval = self.fz
                self.two_d_labels = (r'$B_z$', r'$E_z$')


            self.ymin = 0
            self.ymax =  self.zval.shape[0]/self.c_omp*self.istep
            self.xmin = 0
            self.xmax =  self.zval.shape[1]/self.c_omp*self.istep

            self.cax = self.axes.imshow(self.zval,
                cmap = new_cmaps.cmaps[self.parent.cmap],
                origin = 'lower', aspect = 'auto',
                extent = (self.xmin,self.xmax, self.ymin, self.ymax),
                interpolation=self.GetPlotParam('interpolation'))

            self.axes.annotate(self.two_d_labels[self.GetPlotParam('field_type')],
                            xy = (0.9,.9),
                            xycoords= 'axes fraction',
                            color = 'white',
                            **self.annotate_kwargs)
            self.axes.set_axis_bgcolor('lightgrey')

            if self.GetPlotParam('show_cbar'):
                self.axC = self.figure.add_subplot(self.gs[:4,:])
                self.cbar = self.figure.colorbar(self.cax, ax = self.axes, cax = self.axC, orientation = 'horizontal')

                self.cbar.set_ticks(np.linspace(self.zval.min(),self.zval.max(), 5))
                self.cbar.ax.tick_params(labelsize=10)

            self.axes.set_axis_bgcolor('lightgrey')
            self.axes.tick_params(labelsize = 10, color=tick_color)
#        self.axes.set_xlim(self.xmin,self.xmax)
            self.axes.set_xlabel(r'$x\ [c/\omega_{\rm pe}]$', labelpad = -2, color = 'black')
            self.axes.set_ylabel(r'$y\ [c/\omega_{\rm pe}]$', labelpad = 0, color = 'black')

        else:
            self.annotate_pos = [0.8,0.9]
            if self.GetPlotParam('show_x'):
                self.axes.plot(self.x_values, self.fx[self.fx.shape[0]/2,:], color = self.xcolor)
                if self.GetPlotParam('field_type') == 0:
                    tmp_str = r'$B_x$'
                else:
                    tmp_str = r'$E_x$'
                self.axes.annotate(tmp_str, xy = self.annotate_pos,
                                xycoords = 'axes fraction',
                                color = self.xcolor,
                                **self.annotate_kwargs)
                self.annotate_pos[0] += .08
            if self.GetPlotParam('show_y'):
                self.axes.plot(self.x_values, self.fy[self.fy.shape[0]/2,:], color = self.ycolor)
                if self.GetPlotParam('field_type') == 0:
                    tmp_str = r'$B_y$'
                else:
                    tmp_str = r'$E_y$'
                self.axes.annotate(tmp_str, xy = self.annotate_pos,
                                xycoords= 'axes fraction',
                                color = self.ycolor,
                                **self.annotate_kwargs)

                self.annotate_pos[0] += .08

            if self.GetPlotParam('show_z'):
                self.axes.plot(self.x_values, self.fz[self.fz.shape[0]/2,:], color = self.zcolor)
                if self.GetPlotParam('field_type') == 0:
                    tmp_str = r'$B_z$'
                else:
                    tmp_str = r'$E_z$'
                self.axes.annotate(tmp_str, xy = self.annotate_pos,
                                xycoords= 'axes fraction',
                                color = self.zcolor,
                                **self.annotate_kwargs
                                )


            self.axes.set_axis_bgcolor('lightgrey')
            self.axes.tick_params(labelsize = 10, color=tick_color)
            self.axes.set_xlim(self.x_values[0],self.x_values[-1])
            self.axes.set_xlabel(r'$x\ [c/\omega_{\rm pe}]$', labelpad = -2, color = 'black')


    def GetPlotParam(self, keyname):
        return self.FigWrap.GetPlotParam(keyname)

    def SetPlotParam(self, keyname, value, update_plot = True):
        self.FigWrap.SetPlotParam(keyname, value, update_plot = update_plot)

    def OpenSettings(self):
        if self.settings_window is None:
            self.settings_window = FieldSettings(self)
        else:
            self.settings_window.destroy()
            self.settings_window = FieldSettings(self)


class FieldSettings(Tk.Toplevel):
    def __init__(self, parent):
        self.parent = parent
        Tk.Toplevel.__init__(self)

        self.wm_title('Field Plot (%d,%d) Settings' % self.parent.FigWrap.pos)
        self.parent = parent
        frm = ttk.Frame(self)
        frm.pack(fill=Tk.BOTH, expand=True)
        self.protocol('WM_DELETE_WINDOW', self.OnClosing)
        #Create some sizers




#                   'field_type': 0, #0 = B-Field, 1 = E-field
#                   'show_x' : 1,
#                   'show_y' : 1,
#                   'show_z' : 1,
#                   'show_cbar': True,
#                   'set_color_limits': False,
#                   'v_min': None,
#                   'OutlineText': True,
#                   'interpolation': 'hermite',
#                   'v_max': None
        # Create the OptionMenu to chooses the Chart Type:
        self.InterpolVar = Tk.StringVar(self)
        self.InterpolVar.set(self.parent.GetPlotParam('interpolation')) # default value
        self.InterpolVar.trace('w', self.InterpolChanged)

        ttk.Label(frm, text="Interpolation Method:").grid(row=0, column = 2)
        InterplChooser = apply(ttk.OptionMenu, (frm, self.InterpolVar, self.parent.GetPlotParam('interpolation')) + tuple(self.parent.InterpolationMethods))
        InterplChooser.grid(row =0, column = 3, sticky = Tk.W + Tk.E)

        # Create the OptionMenu to chooses the Chart Type:
        self.ctypevar = Tk.StringVar(self)
        self.ctypevar.set(self.parent.chartType) # default value
        self.ctypevar.trace('w', self.ctypeChanged)

        ttk.Label(frm, text="Choose Chart Type:").grid(row=0, column = 0)
        cmapChooser = apply(ttk.OptionMenu, (frm, self.ctypevar, self.parent.chartType) + tuple(self.parent.ChartTypes))
        cmapChooser.grid(row =0, column = 1, sticky = Tk.W + Tk.E)


        self.TwoDVar = Tk.IntVar(self) # Create a var to track whether or not to plot in 2-D
        self.TwoDVar.set(self.parent.GetPlotParam('twoD'))
        cb = ttk.Checkbutton(frm, text = "Show in 2-D",
                variable = self.TwoDVar,
                command = self.Change2d)
        cb.grid(row = 1, sticky = Tk.W)

        # the Radiobox Control to choose the Field Type
        self.FieldList = ['B Field', 'E field']
        self.FieldTypeVar  = Tk.IntVar()
        self.FieldTypeVar.set(self.parent.GetPlotParam('field_type'))

        ttk.Label(frm, text='Choose Field:').grid(row = 2, sticky = Tk.W)

        for i in range(len(self.FieldList)):
            ttk.Radiobutton(frm,
                text=self.FieldList[i],
                variable=self.FieldTypeVar,
                command = self.RadioField,
                value=i).grid(row = 3+i, sticky =Tk.W)

        # the Check boxes for the dimension
        ttk.Label(frm, text='Dimenison:').grid(row = 1, column = 1, sticky = Tk.W)

        self.ShowXVar = Tk.IntVar(self) # Create a var to track whether or not to plot in 2-D
        self.ShowXVar.set(self.parent.GetPlotParam('show_x'))
        cb = ttk.Checkbutton(frm, text = "Show x",
            variable = self.ShowXVar,
            command = self.Selector)
        cb.grid(row = 2, column = 1, sticky = Tk.W)

        self.ShowYVar = Tk.IntVar(self) # Create a var to track whether or not to plot in 2-D
        self.ShowYVar.set(self.parent.GetPlotParam('show_y'))
        cb = ttk.Checkbutton(frm, text = "Show y",
            variable = self.ShowYVar,
            command = self.Selector)
        cb.grid(row = 3, column = 1, sticky = Tk.W)

        self.ShowZVar = Tk.IntVar(self) # Create a var to track whether or not to plot in 2-D
        self.ShowZVar.set(self.parent.GetPlotParam('show_z'))
        cb = ttk.Checkbutton(frm, text = "Show z",
            variable = self.ShowZVar,
            command = self.Selector)
        cb.grid(row = 4, column = 1, sticky = Tk.W)


        # Control whether or not Cbar is shown
        self.CbarVar = Tk.IntVar()
        self.CbarVar.set(self.parent.GetPlotParam('show_cbar'))
        cb = ttk.Checkbutton(frm, text = "Show Color bar",
                        variable = self.CbarVar,
                        command = lambda:
                        self.parent.SetPlotParam('show_cbar', self.CbarVar.get()))
        cb.grid(row = 6, sticky = Tk.W)


    def Change2d(self):

        if self.TwoDVar.get() == self.parent.GetPlotParam('twoD'):
            pass
        else:
            if self.TwoDVar.get():
                # Make sure only one dimension checked
                if self.parent.GetPlotParam('show_x'):
                    self.ShowYVar.set(0)
                    self.ShowZVar.set(0)

                elif self.parent.GetPlotParam('show_y'):
                    self.ShowZVar.set(0)

                elif ~self.parent.GetPlotParam('show_z'):
                    self.ShowXVar.set(1)

            self.parent.SetPlotParam('twoD', self.TwoDVar.get())



    def ctypeChanged(self, *args):
        if self.ctypevar.get() == self.parent.chartType:
            pass
        else:
            self.parent.ChangePlotType(self.ctypevar.get())
            self.destroy()

    def InterpolChanged(self, *args):
        if self.InterpolVar.get() == self.parent.GetPlotParam('interpolation'):
            pass
        else:
            self.parent.SetPlotParam('interpolation', self.InterpolVar.get())

    def RadioField(self):
        if self.FieldTypeVar.get() == self.parent.GetPlotParam('field_type'):
            pass
        else:
            self.parent.SetPlotParam('field_type', self.FieldTypeVar.get())

    def Selector(self):
        # First check if it is 2-D:
        if self.parent.GetPlotParam('twoD'):

            if self.ShowXVar.get() == 0 and self.ShowYVar.get() == 0 and self.ShowZVar.get() == 0:
                # All are zero, something must be selected for this plot
                self.ShowXVar.set(1)


            if self.parent.GetPlotParam('show_x') != self.ShowXVar.get():
                # set the other plot values to zero in the PlotParams
                self.parent.SetPlotParam('show_y', 0, update_plot = False)

                self.parent.SetPlotParam('show_z', 0, update_plot = False)

                # Uncheck the boxes
                self.ShowYVar.set(self.parent.GetPlotParam('show_y'))
                self.ShowZVar.set(self.parent.GetPlotParam('show_z'))

                self.parent.SetPlotParam('show_x', self.ShowXVar.get())


            elif self.parent.GetPlotParam('show_y') != self.ShowYVar.get():
                # set the other plot values to zero in the PlotParams
                self.parent.SetPlotParam('show_x', 0 ,update_plot = False)
                self.parent.SetPlotParam('show_z', 0 ,update_plot = False)

                # Uncheck the boxes
                self.ShowXVar.set(self.parent.GetPlotParam('show_x'))
                self.ShowZVar.set(self.parent.GetPlotParam('show_z'))


                self.parent.SetPlotParam('show_y', self.ShowYVar.get())

            elif self.parent.GetPlotParam('show_z') != self.ShowZVar.get():
                # set the other plot values to zero in the PlotParams
                self.parent.SetPlotParam('show_x', 0 ,update_plot = False)
                self.parent.SetPlotParam('show_y', 0 ,update_plot = False)

                # Uncheck the boxes

                self.ShowXVar.set(self.parent.GetPlotParam('show_x'))
                self.ShowYVar.set(self.parent.GetPlotParam('show_y'))

                self.parent.SetPlotParam('show_z', self.ShowZVar.get())


        else:

            if self.parent.GetPlotParam('show_x') != self.ShowXVar.get():
                self.parent.SetPlotParam('show_x', self.ShowXVar.get())

            elif self.parent.GetPlotParam('show_y') != self.ShowYVar.get():
                self.parent.SetPlotParam('show_y', self.ShowYVar.get())

            elif self.parent.GetPlotParam('show_z') != self.ShowZVar.get():
                self.parent.SetPlotParam('show_z', self.ShowZVar.get())


    def OnClosing(self):
        self.parent.settings_window = None
        self.destroy()