# This module modifies some of the routines in the matplotlib module. The code
# for the modified routines are copied here and modified.
# Copyright (c) 2012-2013 Matplotlib Development Team; All Rights Reserved

import wx
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import backend_bases
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import warnings
from scipy.io import savemat

from matplotlib.backends.backend_wx import error_msg_wx

class myMatplotlibPanel(wx.Panel):
    def __init__(self, parent):
        # mpl.rcParams['toolbar'] = 'None'
        backend_bases.NavigationToolbar2.toolitems = (
            ('Home', 'Reset original view', 'home', 'home'),
            ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
            ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
            ('Save', 'Save the figure', 'filesave', 'save_figure'),
        )

        wx.Panel.__init__(self, parent)
        self.figure = mpl.figure.Figure()
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.axes = self.figure.add_subplot(111)
        self.points = self.axes.plot([0, 0])
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)
        