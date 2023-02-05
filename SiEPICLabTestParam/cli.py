from TestParameters import testParameters
import wx

if __name__ == '__main__':
  app = wx.App(redirect=False)
  testParameters()
  app.MainLoop()
  app.Destroy()
  del app