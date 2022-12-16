import wx
import wx.lib.agw.hyperlink as hl

class MyFrame(wx.Frame):

    def __init__(self, parent):

        wx.Frame.__init__(self, parent, -1, "HyperLink Demo")

        panel = wx.Panel(self, -1)

        # Default Web links:
        hyper1 = hl.HyperLinkCtrl(panel, -1, "wxPython Main Page", pos=(100, 100),
                                  URL="http://www.wxpython.org/")


        # Web link with underline rollovers, opens in same window
        hyper2 = hl.HyperLinkCtrl(panel, -1, "My Home Page", pos=(100, 150),
                                  URL="http://xoomer.virgilio.it/infinity77/")

        hyper2.AutoBrowse(False)
        hyper2.SetColours("BLUE", "BLUE", "BLUE")
        hyper2.EnableRollover(True)
        hyper2.SetUnderlines(False, False, True)
        hyper2.SetBold(True)
        hyper2.OpenInSameWindow(True)
        hyper2.SetToolTip(wx.ToolTip("Hello World!"))
        hyper2.UpdateLink()


# our normal wxApp-derived class, as usual

app = wx.App(0)

frame = MyFrame(None)
app.SetTopWindow(frame)
frame.Show()

app.MainLoop()