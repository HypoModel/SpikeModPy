## HypoModPython
##
## Started 5/11/18
## Continued 24/8/22
##
## Duncan MacGregor
##


import wx

from HypoModPy.hypomain import *


#from Cocoa import NSApp, NSApplication


app = wx.App(False)
pos = wx.DefaultPosition
size = wx.Size(400, 500)
mainpath = ""
respath = ""
modname = "Spike"
mainwin = HypoMain("HypoMod", pos, size, respath, mainpath, modname)
mainwin.Show()
mainwin.SetFocus()
app.MainLoop()



