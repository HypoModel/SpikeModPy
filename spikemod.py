

import wx
import random
import numpy as np

from HypoModPy.hypomods import *
from HypoModPy.hypoparams import *
from HypoModPy.hypodat import *
from HypoModPy.hypogrid import *
from HypoModPy.hypospikes import *


class SpikeMod(Mod):
    def __init__(self, mainwin, tag):
        Mod.__init__(self, mainwin, tag)

        if mainwin.modpath != "": self.path = mainwin.modpath + "/Spike"
        else: self.path = "Spike"

        if os.path.exists(self.path) == False: 
            os.mkdir(self.path)

        self.mainwin = mainwin

        # tool boxes
        self.gridbox = GridBox(self, "Data Grid", wx.Point(0, 0), wx.Size(320, 500), 100, 20)
        self.gridbox.NeuroButton()
        self.spikemodbox = SpikeModBox(self, "spikemod", "Spike Model", wx.Point(0, 0), wx.Size(320, 500))
        self.spikedatabox = SpikeDataBox(self, "spikedatabox", "Spike Data", wx.Point(0, 0), wx.Size(320, 500))

        # link mod owned boxes
        mainwin.gridbox = self.gridbox
        mainwin.spikedatabox = self.spikedatabox

        # spike data analysis stores
        self.cellspike = SpikeDat()
        self.modspike = SpikeDat()

        # spike data stores
        self.spikedata = []

        self.AddTool(self.spikemodbox)
        self.AddTool(self.gridbox)
        self.AddTool(self.spikedatabox)
    
        self.spikemodbox.Show(True)
        self.modbox = self.spikemodbox

        self.ModLoad()
        print("Spike Model OK")

        self.PlotData()
        self.graphload = True


    ## PlotData() defines all the available plots, each linked to a data array in osmodata
    ##
    def PlotData(self):
        # Data plots
        #
        # AddPlot(PlotDat(data array, xfrom, xto, yfrom, yto, label string, plot type, bin size, colour), tag string)
        # ----------------------------------------------------------------------------------
        self.plotbase.AddPlot(PlotDat(self.cellspike.hist5, 0, 2000, 0, 500, "Cell Hist 5ms", "line", 1, "blue"), "datahist5")
        self.plotbase.AddPlot(PlotDat(self.cellspike.hist5norm, 0, 2000, 0, 500, "Cell Hist 5ms Norm", "line", 1, "blue"), "datahist5norm")
        self.plotbase.AddPlot(PlotDat(self.cellspike.haz5, 0, 2000, 0, 100, "Cell Haz 5ms", "line", 1, "blue"), "datahaz5")
        self.plotbase.AddPlot(PlotDat(self.modspike.hist5, 0, 2000, 0, 100, "Mod Hist 5ms", "line", 1, "green"), "modhist5")
        self.plotbase.AddPlot(PlotDat(self.modspike.hist5norm, 0, 2000, 0, 100, "Mod Hist 5ms Norm", "line", 1, "green"), "modhist5norm")
        self.plotbase.AddPlot(PlotDat(self.modspike.haz5, 0, 2000, 0, 100, "Mod Haz 5ms", "line", 1, "green"), "modhaz5")

        self.plotbase.AddPlot(PlotDat(self.cellspike.srate1s, 0, 500, 0, 20, "Cell Spike Rate 1s", "spikes", 1, "red"), "cellrate1s")
        self.plotbase.AddPlot(PlotDat(self.modspike.srate1s, 0, 500, 0, 20, "Mod Spike Rate 1s", "spikes", 1, "purple"), "modrate1s")

        self.IoDGraph(self.cellspike.IoDdata, self.cellspike.IoDdataX, "IoD Cell", "iodcell", "lightblue", 10)
        self.IoDGraph(self.modspike.IoDdata, self.modspike.IoDdataX, "IoD Mod", "iodmod", "lightgreen", 0)



    def DefaultPlots(self):
        if len(self.mainwin.panelset) > 0: self.mainwin.panelset[0].settag = "datahist5"
        if len(self.mainwin.panelset) > 1: self.mainwin.panelset[1].settag = "datahaz5"
        if len(self.mainwin.panelset) > 2: self.mainwin.panelset[2].settag = "modhist5"


    def NeuroData(self):
        DiagWrite("NeuroData() call\n")

        self.cellindex = self.spikedatabox.cellpanel.cellindex
        self.cellspike.Analysis(self.spikedata[self.cellindex])
        self.cellspike.id = self.cellindex
        self.cellspike.name = self.spikedata[self.cellindex].name
        self.spikedatabox.cellpanel.PanelData(self.cellspike)

        self.mainwin.scalebox.GraphUpdateAll()


    def ModelData(self):
        DiagWrite("ModelData() call\n")

        self.modspike.Analysis()
        self.mainwin.scalebox.GraphUpdateAll()


    def OnModThreadComplete(self, event):
        self.mainwin.scalebox.GraphUpdateAll()
        DiagWrite(f"Model thread OK, test value {event.GetInt()}\n\n")
        self.runflag = False
        self.ModelData()


    def OnModThreadProgress(self, event):
        self.spikemodbox.SetCount(event.GetInt())
        #DiagWrite(f"Model thread progress, value {event.GetInt()}\n\n")


    def RunModel(self):
        if not self.runflag:
            self.mainwin.SetStatusText("Spike Model Run")
            self.runflag = True
            modthread = SpikeModel(self)
            modthread.start()


class SpikeModel(ModThread):
    def __init__(self, mod):
        ModThread.__init__(self, mod.modbox, mod.mainwin)

        self.mod = mod
        self.spikemodbox = mod.spikemodbox
        self.mainwin = mod.mainwin
        self.scalebox = mod.mainwin.scalebox


    # run() is the thread entry function, used to initialise and call the main Model() function   
    def run(self):
        # Read model flags
        self.randomflag = self.spikemodbox.modflags["randomflag"]      # model flags are useful for switching elements of the model code while running

        if self.randomflag: random.seed(0)
        else: random.seed(datetime.now().microsecond)

        DiagWrite("Running Spike Model\n")

        self.Model()
        completeevent = ModThreadEvent(ModThreadCompleteEvent)
        wx.QueueEvent(self.mod, completeevent)


    # Model() reads in the model parameters, initialises variables, and runs the main model loop
    def Model(self):
        spikedata = self.mod.modspike
        params = self.spikemodbox.GetParams()
        #protoparams = self.mod.protobox.GetParams()


        # Read parameters
        runtime = int(params["runtime"])
        hstep = params["hstep"]
        Vthresh = params["Vthresh"]
        Vrest = params["Vrest"]
        pspmag = params["pspmag"]
        psprate = params["psprate"]
        pspratio = params["pspratio"]
        halflifeMem = params["halflifeMem"]
        kHAP = params["kHAP"]
        halflifeHAP = params["halflifeHAP"]
        kAHP = params["kAHP"]
        halflifeAHP = params["halflifeAHP"]
        kDAP = params["kDAP"]
        halflifeDAP = params["halflifeDAP"]

        epspmag = pspmag
        ipspmag = pspmag
        absref = 2
        

        # Time Constants - conversion from half-life
        # Spiking 
        tauMem = math.log(2) / halflifeMem
        tauHAP = math.log(2) / halflifeHAP
        tauAHP = math.log(2) / halflifeAHP
        tauDAP = math.log(2) / halflifeDAP

        # Initialise variables
        epsprate = 0
        ipsprate = 0
        epspt = 0
        ipspt = 0
        ttime = 0
        V = Vrest
        inputPSP = 0
        tPSP = 0
        tHAP = 0
        tAHP = 0
        tDAP = 0

        spikedata.spikecount = 0
        maxspikes = spikedata.maxspikes
        neurotime = 0
        runtime = runtime * 1000

        # Run model loop
        for i in range(1, runtime + 1):
            ttime += 1
            neurotime += 1
            if i%(runtime/100) == 0: 
                progevent = ModThreadEvent(ModThreadProgressEvent)
                progevent.SetInt(math.floor(neurotime / runtime * 100)) 
                wx.QueueEvent(self.mod, progevent)                        # Update run progress % in model panel

            # PSP input signal
            nepsp = 0
            nipsp = 0
            epsprate = psprate / 1000
            ipsprate = epsprate * pspratio

            if epsprate > 0: 
                while epspt < hstep:
                    erand = random.random()
                    nepsp += 1
                    epspt = -math.log(1 - erand) / epsprate + epspt
                epspt = epspt - hstep

            if ipsprate > 0: 
                while ipspt < hstep:
                    irand = random.random()
                    nipsp += 1
                    ipspt = -math.log(1 - irand) / ipsprate + ipspt
                ipspt = ipspt - hstep

            inputPSP = nepsp * epspmag - nipsp * ipspmag


            # Spiking Model
            tPSP = tPSP + inputPSP - tPSP * tauMem

            tHAP = tHAP - tHAP * tauHAP

            tAHP = tAHP - tAHP * tauAHP

            tDAP = tDAP - tDAP * tauDAP

            V = Vrest + tPSP - tHAP - tAHP + tDAP

            #print(f"SpikeModel step {i}  V {V:.2f}  tPSP {tPSP:.2f}  inputPSP {inputPSP:.2f}  nepsp {nepsp}")


            # Spiking
            if V > Vthresh and ttime >= absref:

                # record spike time
                if spikedata.spikecount < maxspikes: 
                    spikedata.times[spikedata.spikecount] = neurotime
                    spikedata.spikecount += 1
    
                # Spike incremented variable
                # afterpotentials
                tHAP = tHAP + kHAP
                tAHP = tAHP + kAHP
                tDAP = tDAP + kDAP

        freq = spikedata.spikecount / (runtime / 1000)
        DiagWrite(f"Spike Model OK, generated {spikedata.spikecount} spikes, freq {freq:.2f}\n")


class SpikeModBox(ParamBox):
    def __init__(self, mod, tag, title, position, size):
        ParamBox.__init__(self, mod, title, position, size, tag, 0, 1)

        self.autorun = False

        # Initialise Menu 
        self.InitMenu()

        # Model Flags
        ID_randomflag = wx.NewIdRef()   # request a new control ID
        self.AddFlag(ID_randomflag, "randomflag", "Fixed Random Seed", 0)  # menu accessed flags for switching model code


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
        self.paramset.AddCon("kDAP", "kDAP", 0, 0.01, 2)
        self.paramset.AddCon("halflifeDAP", "halflifeDAP", 150, 1, 2)

        self.ParamLayout(2)   # layout parameter controls in two columns

        # ----------------------------------------------------------------------------------

        runbox = self.RunBox()
        paramfilebox = self.StoreBoxSync()


        ID_Grid = wx.NewIdRef()
        self.AddPanelButton(ID_Grid, "Grid", self.mod.gridbox)

        self.mainbox.AddSpacer(5)
        self.mainbox.Add(self.pconbox, 1, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddStretchSpacer(5)
        self.mainbox.Add(runbox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddSpacer(5)
        self.mainbox.Add(paramfilebox, 0, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)    
        #self.mainbox.AddStretchSpacer()
        self.mainbox.Add(self.buttonbox, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 0)
        self.mainbox.AddSpacer(5)
        #self.mainbox.AddSpacer(2)
        self.panel.Layout()


    def SetCount(self, value):
        self.runcount.SetLabel(f"{value} %")


class NeuroBox(ParamBox):
    def __init__(self, mod, tag, title, position, size):
        ParamBox.__init__(self, mod, title, position, size, tag, 0, 1)

        self.autorun = True

        # Initialise Menu 
        #self.InitMenu()

        # Model Flags
    

        # Parameter controls
        #
        # AddCon(tag string, display string, initial value, click increment, decimal places)
        # ----------------------------------------------------------------------------------
        self.paramset.AddCon("drinkstart", "Drink Start", 0, 1, 0)
        self.paramset.AddCon("drinkstop", "Drink Stop", 0, 1, 0)
        self.paramset.AddCon("drinkrate", "Drink Rate", 10, 1, 0)

        self.ParamLayout(3)   # layout parameter controls in two columns

        # ----------------------------------------------------------------------------------

        self.mainbox.AddSpacer(5)
        self.mainbox.Add(self.pconbox, 1, wx.ALIGN_CENTRE_HORIZONTAL|wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 0)
        self.mainbox.AddStretchSpacer(5)
        self.mainbox.AddSpacer(2)
        self.panel.Layout()
