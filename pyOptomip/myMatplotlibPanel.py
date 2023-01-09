
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

from matplotlib.backends.backend_wx import error_msg_wx  # DEBUG_MSG
from matplotlib.backends.backend_wx import  DEBUG_MSG, error_msg_wx

class myToolbar(NavigationToolbar):
    # Remove unused toolbar elements
    toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
      )

    # Added an option to save a .mat file. .mat is added to the file save dialog and code was added
    # to save a mat file.
    def save_figure(self, *args):
        # Fetch the required filename and file type.
        filetypes, exts, filter_index = self.canvas._get_imagesave_wildcards()
        default_file = self.canvas.get_default_filename()
        dlg = wx.FileDialog(self, "Save to file", "", default_file,
                            filetypes,
                            wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        dlg.SetFilterIndex(filter_index)
        if dlg.ShowModal() == wx.ID_OK:
            dirname  = dlg.GetDirectory()
            filename = dlg.GetFilename()
            DEBUG_MSG('Save file dir:%s name:%s' % (dirname, filename), 3, self)
            format = exts[dlg.GetFilterIndex()]
            basename, ext = os.path.splitext(filename)
            if ext.startswith('.'):
                ext = ext[1:]
            if ext in ('svg', 'pdf', 'ps', 'eps', 'png') and format!=ext:
                #looks like they forgot to set the image type drop
                #down, going with the extension.
                warnings.warn('extension %s did not match the selected image type %s; going with %s'%(ext, format, ext), stacklevel=0)
                format = ext
            if ext == 'mat':

                savemat(os.path.join(dirname, filename), self.canvas.sweepResultDict)

            else:
                try:
                    self.canvas.print_figure(
                        os.path.join(dirname, filename), format=format)
                except Exception as e:
                    error_msg_wx(str(e))


class myMatplotlibPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent)
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)

        self.points = self.axes.plot([0,0])
        #plt.plot([0,0])
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.canvas = FigureCanvas(self,-1, self.figure)
        self.canvas.filetypes['mat'] = 'MATLAB' # Add mat filetype to save file dialog
        self.toolbar = myToolbar(self.canvas)
        vbox.Add(self.canvas, 1, wx.EXPAND)
        vbox.Add(self.toolbar, 0)
        self.SetSizer(vbox)
        #self.toolbar.Hide()
