# The MIT License (MIT)

# Copyright (c) 2015 Michael Caverley

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from cx_Freeze import setup, Executable
build_exe_options = {"packages": ["scipy.sparse.csgraph._validation", "win32com", "scipy"], "includes": ["win32com"], "excludes": ["Tkconstants", "Tkinter", "tcl", "matplotlib.backends.backend_tkagg",
                                             "matplotlib.backends.backend_gtk", "matplotlib.backends.backend_gdk",
                                             "matplotlib.backends.backend_qt", "matplotlib.backends.backend_qt4",
                                             "matplotlib.backends.backend_gtkagg", "matplotlib.backends.backend_pdf",
                                             "matplotlib.backends.backend_ps",
                                             "matplotlib.backends._ns_backend_gdk",
                                             "matplotlib.backends._nc_backend_gdk", "matplotlib.backends._na_backend_gdk",
                                             "matplotlib.backends._gtkagg", 'collections.abc']}

setup(
    name = "pyOptomip",
    version = "1.0",
    description = "pyOptomip",
    options = {"build_exe": build_exe_options},
    executables = [Executable("pyOptomip.pyw", base = "Win32GUI")])