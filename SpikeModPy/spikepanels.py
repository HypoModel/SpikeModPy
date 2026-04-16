
import wx

from HypoModPy.hypoparams import ParamBox



class SpikeBox(ParamBox):
    def __init__(self, mod, tag, title, position, size):
        ParamBox.__init__(self, mod, title, position, size, tag, 0, 1)

        self.autorun = False

        # Initialise Menu 
        self.InitMenu()

        # Model Flags
        self.AddFlag("randomflag", "Fixed Random Seed", 0)  # menu accessed flags for switching model code


        # Parameter controls
        #
        # AddCon(tag string, display string, initial value, click increment, decimal places)
        # ----------------------------------------------------------------------------------
        self.paramset.AddCon("runtime", "Run Time", 2000, 1, 0)
        self.paramset.AddCon("hstep", "h Step", 1, 0.1, 1)
        self.paramset.AddCon("Vrest", "Vrest", -62, 0.1, 2)
        self.paramset.AddCon("Vthresh", "Vthresh", -50, 0.1, 2)
        self.paramset.AddCon("psprate", "PSP Rate", 300, 1, 0)
        self.paramset.AddCon("pspratio", "PSP ratio", 1, 0.1, 2)
        self.paramset.AddCon("pspmag", "PSP mag", 3, 0.1, 2)
        self.paramset.AddCon("halflifeMem", "halflifeMem", 7.5, 0.1, 2)
        self.paramset.AddCon("kHAP", "kHAP", 60, 0.1, 2)
        self.paramset.AddCon("halflifeHAP", "halflifeHAP", 8, 0.1, 2)
        self.paramset.AddCon("kAHP", "kAHP", 0.5, 0.01, 2)
        self.paramset.AddCon("halflifeAHP", "halflifeAHP", 500, 1, 2)

        self.paramset.AddCon("pspmag2", "pspmag2", 0, 0.1, 4)
        self.paramset.AddCon("psprate2", "psprate2", 0, 1, 2)
        self.paramset.AddCon("halflifePSP2", "halflifePSP2", 5, 0.1, 4)

        self.paramset.GetCon("runtime").SetMinMax(10, 10000)

        self.ParamLayout(2)   # layout parameter controls in two columns

        # ----------------------------------------------------------------------------------

        runbox = self.RunBox()
        paramfilebox = self.StoreBoxSync()

        databox = wx.BoxSizer(wx.HORIZONTAL)
        self.freq = self.NumPanel(60, wx.ALIGN_RIGHT)
        label = wx.StaticText(self.panel, wx.ID_STATIC, "Freq")
        #label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        label.SetFont(self.confont)
        databox.Add(label,0, (wx.ALIGN_CENTRE|wx.ST_NO_AUTORESIZE))
        databox.AddSpacer(10)   
        databox.Add(self.freq)

        ID_Grid = wx.NewIdRef()
        self.AddPanelButton(ID_Grid, "Grid", self.mod.gridbox)
        ID_Sec = wx.NewIdRef()
        self.AddPanelButton(ID_Sec, "Sec", self.mod.secbox)

        self.mainbox.AddSpacer(5)
        self.mainbox.Add(self.pconbox, 1, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddStretchSpacer(5)
        self.mainbox.Add(runbox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddSpacer(5)
        self.mainbox.Add(databox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddSpacer(5)
        self.mainbox.Add(paramfilebox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)    
        self.mainbox.Add(self.buttonbox, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 0)
        self.mainbox.AddSpacer(5)
        self.panel.Layout()


    def SpikeData(self, data):
        self.freq.SetLabel(f"{data.freq:.2f} Hz")


    def OnStore(self, event):
        if self.synccheck.GetValue():
            filetag = self.storetag.GetValue()
            self.mod.secbox.ParamStore(filetag)   
        return super().OnStore(event)
    

    def OnLoad(self, event):
        if self.synccheck.GetValue():
            filetag = self.storetag.GetValue()
            self.mod.secbox.ParamLoad(filetag)   
        return super().OnLoad(event)



class SecBox(ParamBox):
    def __init__(self, mod, tag, title, position, size):
        ParamBox.__init__(self, mod, title, position, size, tag, 0, 1)

        self.autorun = False

        # Initialise Menu 
        self.InitMenu()

        # Parameter controls
        #
        # AddCon(tag string, display string, initial value, click increment, decimal places)
        # ----------------------------------------------------------------------------------
        self.paramset.con_labelwidth = 80
        self.paramset.AddCon("kB", "kB", 0.021, 0.001, 3)
        self.paramset.AddCon("halflifeB", "halflifeB", 2000, 50, 0)
        self.paramset.AddCon("Bbase", "Bbase", 0.5, 0.05, 2)
        self.paramset.AddCon("kC", "SlowCa K", 0.0003, 0.00001, 5)
        self.paramset.AddCon("halflifeC", "C HL", 20000, 1000, 0)
        self.paramset.AddCon("kE", "FastCa K", 1.5, 0.02, 2)
        self.paramset.AddCon("halflifeE", "E HL", 100, 5, 1)
        self.paramset.AddCon("Cth", "Cth", 0.14, 0.01, 3)
        self.paramset.AddCon("Cgradient", "C Grad", 5, 0.1, 2)
        self.paramset.AddCon("Eth", "Eth", 12, 0.05, 2)
        self.paramset.AddCon("Egradient", "E Grad", 5, 0.1, 2)
        self.paramset.AddCon("beta", "beta", 120, 1, 1)
        self.paramset.AddCon("Rmax", "Res Max", 1000000, 100000, 0)
        self.paramset.AddCon("Rinit", "Res Init", 1000000, 100000, 0)
        self.paramset.AddCon("Pmax", "Pool Max", 5000, 500, 0)
        self.paramset.AddCon("alpha", "alpha", 0.003, 0.0001, 6)
        self.paramset.AddCon("plasma_hstep", "hstep Plas", 1, 1, 0)
        self.paramset.AddCon("halflifeDiff", "Diff HL", 61, 5, 0)   # 100sec, half life to pass between plasma and ECF. Just a guess.
        self.paramset.AddCon("halflifeClear", "Clear HL", 68, 5, 0)   # 58sec half life to be destroyed through the kidneys.
        self.paramset.AddCon("VolPlasma", "Plasma (ml)", 100, 0.5, 1)   # Total amount of plasma in a rat. 8.5ml for a 250g rat.
        self.paramset.AddCon("VolEVF", "EVFluid (ml)", 9.75, 0.5, 2)   # Total amount of Extra Cellular Fluid (without plasma) in a rat.
        self.paramset.AddCon("secExp", "Sec Exp", 2, 0.1, 2)  # Exponent of the fast [Ca2+], e, when calculating the final secretion.

        self.ParamLayout(2)   # layout parameter controls in two columns

        # ----------------------------------------------------------------------------------

        self.mainbox.AddSpacer(5)
        self.mainbox.Add(self.pconbox, 1, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddStretchSpacer(5)
        
        self.panel.Layout()