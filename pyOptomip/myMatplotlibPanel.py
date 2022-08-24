      
# This module modifies some of the routines in the matplotlib module. The code
# for the modified routines are copied here and modified.
# Copyright (c) 2012-2013 Matplotlib Development Team; All Rights Reserved

import wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
from matplotlib.figure import Figure
import os
import warnings
from scipy.io import savemat

from matplotlib.backends.backend_wx import  DEBUG_MSG, error_msg_wx

class myToolbar(NavigationToolbar):
    # Remove unused toolbar elements
    toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
      )

    def set_history_buttons(self):
        pass

    # Home button zooms to display all the data instead of going to the initial zoom level
    def home(self, *args):
        ax = self.canvas.figure.gca()
        ax.axis('auto')
        self.canvas.draw()

    # Added an option to save a .mat file. .mat is added to the file save dialog and code was added
    # to save a mat file.
    def save_figure(self, *args):
        # Fetch the required filename and file type.
        filetypes, exts, filter_index = self.canvas._get_imagesave_wildcards()
        default_file = self.canvas.get_default_filename()
        dlg = wx.FileDialog(self._parent, "Save to file", "", default_file,
                            filetypes,
                            wx.SAVE|wx.OVERWRITE_PROMPT)
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

    # Added feature where double clicking on the graph zooms out to show all the data                    
    def press_zoom(self, event):
        """the press mouse button in zoom to rect mode callback"""
        if event.dblclick:
            self.home()
            return
        elif event.button == 1:
            self._button_pressed=1
        elif  event.button == 3:
            self._button_pressed=3
        else:
            self._button_pressed=None
            return

        x, y = event.x, event.y

        # push the current view to define home if stack is empty
        if self._views.empty(): self.push_current()

        self._xypress=[]
        for i, a in enumerate(self.canvas.figure.get_axes()):
            if (x is not None and y is not None and a.in_axes(event) and
                a.get_navigate() and a.can_zoom()) :
                self._xypress.append(( x, y, a, i, a.viewLim.frozen(),
                                       a.transData.frozen() ))

        id1 = self.canvas.mpl_connect('motion_notify_event', self.drag_zoom)
        id2 = self.canvas.mpl_connect('key_press_event',
                                      self._switch_on_zoom_mode)
        id3 = self.canvas.mpl_connect('key_release_event',
                                      self._switch_off_zoom_mode)

        self._ids_zoom = id1, id2, id3
        self._zoom_mode = event.key

        self.press(event)                
    
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
