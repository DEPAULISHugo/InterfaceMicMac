import os
from tkinter import *
from tkinter.filedialog import *
import tkinter.ttk as ttk
from classMicMac import *
from classTkinter import *
import numpy as np
from ComparePosition import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure 
import matplotlib.pyplot as plt

class TkNewChunk(Toplevel):
    def __init__(self) :
        super().__init__(interface)
        self.title("Add chunk")
        self.placeComponents()
    
    def placeComponents(self):
        self.name = SaisieString(self,"Name:")
        self.directory = SaisieNomDossier(self,"Directory:")
        Label(self,text="Extension of photos:",anchor=W,width=30).pack()
        self.extension = ttk.Combobox(self,values=["JPG","jpg","png"],width=27)
        self.extension.pack()
        Button(self,text="Ok",command=self.validate,width=12).pack(side=LEFT,padx=5,pady=7)
        Button(self,text="Cancel",command=self.destroy,width=12).pack(side=RIGHT,padx=5,pady=7)
        
    def validate(self):
        name = self.name.get()
        directory = self.directory.get()
        extension = self.extension.get()
        newChunk = Chunk(name, directory, extension)
        interface.listChunks.append(newChunk)
        interface.selectedObject = newChunk
        interface.currentChunk = newChunk
        interface.currentPointsLiaisons = 0
        interface.currentCaliEtMEP = 0
        interface.currentNuagePoints = 0
        interface.currentOrtho = 0
        self.destroy()
        interface.canvas.draw()
        
class TkFindTiePoints(Toplevel):
    def __init__(self) :
        super().__init__(interface)
        self.title("Find tie points")
        self.placeComponents()
        
    def callBackMode(self, event):
        if self.mode.get() == "Line" :
            self.nbreImages.pack()
            self.checkCirc.pack()
            self.proj4.pack_forget()
            self.lowResolution.pack_forget()
        elif self.mode.get() == "Mulscale":
            self.lowResolution.pack()
            self.nbreImages.pack_forget()
            self.checkCirc.pack_forget()
            self.proj4.pack_forget()
        elif self.mode.get() == "GPS coordinates" :
            self.proj4.pack()
            self.nbreImages.pack_forget()
            self.checkCirc.pack_forget()
            self.lowResolution.pack_forget()
        else :
            self.nbreImages.pack_forget()
            self.checkCirc.pack_forget()
            self.lowResolution.pack_forget()
            self.proj4.pack_forget()
            
    def placeComponents(self):
        self.name = SaisieString(self,"Name:")
        self.resolution = SaisieInt(self,"Resolution:",1500)
        Label(self,text="Tie points computation mode:",anchor=W,width=30).pack()
        self.mode = ttk.Combobox(self,values=["All","GPS coordinates","Line","Mulscale"],width=27)
        self.mode.pack()
        self.mode.bind("<<ComboboxSelected>>", self.callBackMode)
        ## Start Line
        self.circ = BooleanVar()
        self.circ.set(False)
        self.nbreImages = SaisieInt(self,"Number of adjacent images:",5)
        self.nbreImages.pack_forget()
        self.checkCirc = Checkbutton(self, text="Circular acquisition", var=self.circ)
        self.checkCirc.pack_forget()
        ## End Line
        ## Start Mulscale
        self.lowResolution = SaisieInt(self,"Low resolution for first computation:",500)
        self.lowResolution.pack_forget()
        ## End Mulscale
        ## Start GPS
        self.proj4 = SaisieString(self,"Proj4 of the system:")
        self.proj4.pack_forget()
        ## End GPS
        frame = Frame(self)
        Button(frame,text="Ok",command=self.validate,width=12).pack(side=LEFT,padx=5,pady=7)
        Button(frame,text="Cancel",command=self.destroy,width=12).pack(side=RIGHT,padx=5,pady=7)
        frame.pack(side=BOTTOM)
        
    def validate(self):
        name = self.name.get()
        resolution = str(self.resolution.get())
        mode = self.mode.get()
        if mode == "Line" :
            nbreImages = str(self.nbreImages.get())
            circ = self.circ.get()
            newPointsLiaisons = PointsLiaisonsLine(name, resolution, interface.currentChunk, nbreImages, circ)
        elif mode == "Mulscale" :
            lowResolution = self.lowResolution.get()
            newPointsLiaisons = PointsLiaisonsMulscale(name, resolution, interface.currentChunk, lowResolution)
        elif mode == "GPS coordinates" :
            proj4 = self.proj4.get()
            newPointsLiaisons = PointsLiaisonsGPS(name, resolution, proj4, interface.currentChunk)
        else :
            newPointsLiaisons = PointsLiaisonsAll(name, resolution, interface.currentChunk)
        interface.currentPointsLiaisons = newPointsLiaisons
        interface.selectedObject = newPointsLiaisons
        interface.currentChunk.listPointsLiaisons.append(newPointsLiaisons)
        interface.currentCaliEtMEP = 0
        interface.currentNuagePoints = 0
        interface.currentOrtho = 0
        self.destroy()
        interface.canvas.draw()

class TkCalcCalib(Toplevel):
    def __init__(self) :
        super().__init__(interface)
        self.title("Calculate calibration and align photos")
        self.placeComponents()
        
    def callBackMode(self, event):
        if self.mode.get() == "Figee" :
            self.labelFigee.pack()
            self.calibration.pack()
        else :
            self.labelFigee.pack_forget()
            self.calibration.pack_forget()
            
    def placeComponents(self):
        self.name = SaisieString(self,"Name:")
        Label(self,text="Type of calibration:",anchor=W,width=30).pack()
        self.mode = ttk.Combobox(self,values=["RadialBasic", "RadialStd", "RadialExtended", "FraserBasic", "Fraser", "Figee"],width=27)
        self.mode.pack()
        self.mode.bind("<<ComboboxSelected>>", self.callBackMode)
        ## Start Figee
        self.labelFigee = Label(self,text="Calibration:",anchor=W,width=30)
        valueCali = []
        for pointsLiaison in interface.currentChunk.listPointsLiaisons :
            for calibEtMEP in pointsLiaison.listCaliEtMEP :
                valueCali.append(calibEtMEP.nom)
        self.calibration = ttk.Combobox(self,values=valueCali,width=27)
        ## End Figee
        frame = Frame(self)
        Button(frame,text="Ok",command=self.validate,width=12).pack(side=LEFT,padx=5,pady=7)
        Button(frame,text="Cancel",command=self.destroy,width=12).pack(side=RIGHT,padx=5,pady=7)
        frame.pack(side=BOTTOM)
        
    def validate(self):
        name = self.name.get()
        mode = self.mode.get()
        if mode == "Figee" :
            calibration = self.calibration.get()
            newCaliEtMEP = CaliEtMEPFigee(name, mode, calibration, interface.currentPointsLiaisons)
        else :
            newCaliEtMEP = CaliEtMEP(name, mode, interface.currentPointsLiaisons)
        interface.currentCaliEtMEP = newCaliEtMEP
        interface.selectedObject = newCaliEtMEP
        interface.currentPointsLiaisons.listCaliEtMEP.append(newCaliEtMEP)
        interface.currentNuagePoints = 0
        interface.currentOrtho = 0
        self.destroy()
        interface.canvas.draw()

class TkCalcCalibMergedChunk(Toplevel):
    def __init__(self) :
        super().__init__(interface)
        self.title("Calculate calibration and align photos")
        self.placeComponents()
        
    def callBackMode(self, event):
        if self.mode.get() == "Figee" :
            self.labelFigee.pack()
            self.calibration.pack()
        else :
            self.labelFigee.pack_forget()
            self.calibration.pack_forget()
            
    def placeComponents(self):
        self.name = SaisieString(self,"Name:")
        self.listLabels = []
        self.listCaliName = []
        self.listAlign = []
        for chunk in interface.currentChunk.listChunks:
            self.listLabels.append(Label(self,text="Calibration for "+chunk.nom+":",anchor=W,width=30))
            valueCali = []
            for pointsLiaison in chunk.listPointsLiaisons :
                for calibEtMEP in pointsLiaison.listCaliEtMEP :
                    valueCali.append(calibEtMEP.nom)
            self.listCaliName.append(ttk.Combobox(self,values=valueCali,width=27))
            value = BooleanVar()
            value.set(False)
            self.listAlign.append(value)
            self.checkAlign = Checkbutton(self, text="Use the alignment of "+chunk.nom, var=self.listAlign[-1])
            self.listLabels[-1].pack()
            self.listCaliName[-1].pack()
            self.checkAlign.pack()   
        frame = Frame(self)
        Button(frame,text="Ok",command=self.validate,width=12).pack(side=LEFT,padx=5,pady=7)
        Button(frame,text="Cancel",command=self.destroy,width=12).pack(side=RIGHT,padx=5,pady=7)
        frame.pack(side=BOTTOM)
        
    def validate(self):
        name = self.name.get()
        mode = "Figee"
        listCaliSelected = []
        for caliName in self.listCaliName :
            for chunk in interface.currentChunk.listChunks:
                for pointsLiaison in chunk.listPointsLiaisons :
                    for calibEtMEP in pointsLiaison.listCaliEtMEP :
                        if calibEtMEP.nom == caliName.get():
                            listCaliSelected.append(calibEtMEP)
        for i in range(len(self.listAlign)):
            self.listAlign[i] = self.listAlign[i].get()
        newCaliEtMEP = CaliEtMEPMerge(name, mode, listCaliSelected, self.listAlign, interface.currentPointsLiaisons)
        interface.currentCaliEtMEP = newCaliEtMEP
        interface.selectedObject = newCaliEtMEP
        interface.currentPointsLiaisons.listCaliEtMEP.append(newCaliEtMEP)
        interface.currentNuagePoints = 0
        interface.currentOrtho = 0
        self.destroy()
        interface.canvas.draw()

class TkSwitchSystem(Toplevel):
    def __init__(self) :
        super().__init__(interface)
        self.title("Switch to a new coordinate system")
        self.placeComponents()
        
    def callBackMode(self, event):
        if self.mode.get() == "GPS coordinates" :
            self.proj4.pack()
            self.GCPFile.pack_forget()
        elif self.mode.get() == "GCP and markers" :
            self.GCPFile.pack()
            self.proj4.pack_forget()
        else :
            self.GCPFile.pack_forget()
            self.proj4.pack_forget()
            
    def placeComponents(self):
        self.name = SaisieString(self,"Name:")
        Label(self,text="Method:",anchor=W,width=30).pack()
        self.mode = ttk.Combobox(self,values=["GPS coordinates", "GCP and markers"],width=27)
        self.mode.pack()
        self.mode.bind("<<ComboboxSelected>>", self.callBackMode)
        ## Start GPS
        self.proj4 = SaisieString(self,"Proj4 of the system:")
        self.proj4.pack_forget()
        ## End GPS
        ## Start GCP and markers
        self.GCPFile = SaisieNomFichier(self, "GCP file:")
        self.GCPFile.pack_forget()
        ## End GCP and markers
        frame = Frame(self)
        Button(frame,text="Ok",command=self.validate,width=12).pack(side=LEFT,padx=5,pady=7)
        Button(frame,text="Cancel",command=self.destroy,width=12).pack(side=RIGHT,padx=5,pady=7)
        frame.pack(side=BOTTOM)
        
    def validate(self):
        name = self.name.get()
        mode = self.mode.get()
        proj4 = self.proj4.get()
        GCPFileName = self.GCPFile.fileName.get()
        if mode == "GPS coordinates" :
            newCaliEtMEP = CaliEtMEPBasculeGPS(name, mode, proj4, interface.currentPointsLiaisons, interface.currentCaliEtMEP)
        elif mode == "GCP and markers" :
            newCaliEtMEP = CaliEtMEPBasculeGCP(name, mode, interface.currentPointsLiaisons, GCPFileName, "0", interface.currentCaliEtMEP)
        interface.currentCaliEtMEP = newCaliEtMEP
        interface.selectedObject = newCaliEtMEP
        interface.currentPointsLiaisons.listCaliEtMEP.append(newCaliEtMEP)
        interface.currentNuagePoints = 0
        interface.currentOrtho = 0
        self.destroy()
        interface.canvas.draw()
        
class TkBuildCloud(Toplevel):
    def __init__(self) :
        super().__init__(interface)
        self.title("Build dense cloud")
        self.placeComponents()
            
    def placeComponents(self):
        self.name = SaisieString(self,"Name:")
        self.offset = SaisieCoord(self, "Offset:", 0, 0, 0)
        Label(self,text="Quality:",anchor=W,width=30).pack()
        self.mode = ttk.Combobox(self,values=["Medium", "Good", "Excellent", "Highest"],width=27)
        self.mode.pack()
        frame = Frame(self)
        Button(frame,text="Ok",command=self.validate,width=12).pack(side=LEFT,padx=5,pady=7)
        Button(frame,text="Cancel",command=self.destroy,width=12).pack(side=RIGHT,padx=5,pady=7)
        frame.pack(side=BOTTOM)
        
    def validate(self):
        name = self.name.get()
        offset = self.offset.get()
        mode = self.mode.get()
        newNuagePoints = NuagePoints(name, mode, offset, interface.currentCaliEtMEP)
        interface.currentNuagePoints = newNuagePoints
        interface.selectedObject = newNuagePoints
        interface.currentCaliEtMEP.listNuagePoints.append(newNuagePoints)
        interface.currentOrtho = 0
        self.destroy()
        interface.canvas.draw()

class TkBuildOrtho(Toplevel):
    def __init__(self) :
        super().__init__(interface)
        self.title("Build orthomosaic")
        self.placeComponents()
        
    def callBackMode(self, event):
        if self.mode.get() == "Figee" :
            print("Oups !")
            
    def placeComponents(self):
        self.name = SaisieString(self,"Name:")
        self.equaRadio = BooleanVar()
        self.equaRadio.set(False)
        self.checkEqua = Checkbutton(self, text="Equalization radiometric", var=self.equaRadio)
        self.checkEqua.pack()
        Label(self,text="Mode:",anchor=W,width=30).pack()
        self.mode = ttk.Combobox(self,values=["Parallel to the ground", "Perpendicular to the ground"],width=27)
        self.mode.pack()
        frame = Frame(self)
        Button(frame,text="Ok",command=self.validate,width=12).pack(side=LEFT,padx=5,pady=7)
        Button(frame,text="Cancel",command=self.destroy,width=12).pack(side=RIGHT,padx=5,pady=7)
        frame.pack(side=BOTTOM)
        
    def validate(self):
        name = self.name.get()
        equaRadio = self.equaRadio.get()
        mode = self.mode.get()
        newOrtho = Ortho(name, mode, equaRadio, interface.currentNuagePoints)
        interface.currentOrtho = newOrtho
        interface.selectedObject = newOrtho
        interface.currentNuagePoints.listOrthos.append(newOrtho)
        self.destroy()
        interface.canvas.draw()
        
class TkBuildMesh(Toplevel):
    def __init__(self) :
        super().__init__(interface)
        self.title("Build mesh")
        self.placeComponents()
            
    def placeComponents(self):
        self.name = SaisieString(self,"Name:")
        self.depth = SaisieInt(self,"Depth",8)
        self.textured = BooleanVar()
        self.textured.set(False)
        self.checkTextured = Checkbutton(self, text="With texture", var=self.textured)
        self.checkTextured.pack()
        frame = Frame(self)
        Button(frame,text="Ok",command=self.validate,width=12).pack(side=LEFT,padx=5,pady=7)
        Button(frame,text="Cancel",command=self.destroy,width=12).pack(side=RIGHT,padx=5,pady=7)
        frame.pack(side=BOTTOM)
        
    def validate(self):
        name = self.name.get()
        depth = self.depth.get()
        textured = self.textured.get()
        newMesh = Mesh(name, depth, textured, interface.currentNuagePoints)
        interface.currentOrtho = newMesh
        interface.selectedObject = newMesh
        interface.currentNuagePoints.listOrthos.append(newMesh)
        self.destroy()
        interface.canvas.draw()
        
class TkMergeChunks(Toplevel):
    def __init__(self) :
        super().__init__(interface)
        self.title("Merge chunks")
        self.placeComponents()
    
    def placeComponents(self):
        self.name = SaisieString(self,"Name:")
        self.directory = SaisieNomDossier(self,"New directory:")
        self.listChunks = SaisieChoixMultiples(self, "Chunks:", interface.listChunks)
        frame = Frame(self)
        Button(frame,text="Ok",command=self.validate,width=12).pack(side=LEFT,padx=5,pady=7)
        Button(frame,text="Cancel",command=self.destroy,width=12).pack(side=RIGHT,padx=5,pady=7)
        frame.pack(side=BOTTOM)
    
    def validate(self):
        name = self.name.get()
        directory = self.directory.get()
        listChunks = self.listChunks.get()
        extension = listChunks[0].extension
        newChunk = MergedChunk(name, directory, extension, listChunks)
        newChunk.create()
        interface.listChunks.append(newChunk)
        interface.selectedObject = newChunk
        interface.currentChunk = newChunk
        interface.currentPointsLiaisons = 0
        interface.currentCaliEtMEP = 0
        interface.currentNuagePoints = 0
        interface.currentOrtho = 0
        self.destroy()
        interface.canvas.draw()
        
class TkMergePointsCloud(Toplevel):
    def __init__(self) :
        super().__init__(interface)
        self.title("Merge points clouds")
        self.placeComponents()
    
    def CallbackMaster(self):
        nameList = []
        for objet in self.listPointsClouds.get() :
            nameList.append(objet.nom)
        self.masterPC["values"] = nameList
        self.masterPC.current(0)
    
    def CallbackMatrix(self):
        if self.matrixVar.get() == True :
            self.matrix.activate()
        else :
            self.matrix.desactivate()
        
    def placeComponents(self):
        self.name = SaisieString(self,"Name:")
        self.directory = SaisieNomDossier(self,"New directory:")
        self.listPointsClouds = SaisieChoixMultiplesClasses(self, "Points clouds:", interface.getListPointsClouds(), interface.listChunks)
        Label(self,text="Points cloud as reference:",anchor=W,width=30).pack()
        self.masterPC = ttk.Combobox(self,values=[],width=27)
        self.masterPC.pack()
        #Matrix
        self.matrixVar = BooleanVar()
        self.matrixVar.set(False)
        self.matrixButton = Checkbutton(self, text="Use initial transformation", var=self.matrixVar, command=self.CallbackMatrix)
        self.matrixButton.pack()
        self.matrix = SaisieMatrix(self, "Initial transformation:")
        self.matrix.desactivate()
        #ICP
        self.maxIteration = SaisieInt(self,"Number of ICP iterations:",0)
        self.sampling = SaisieInt(self,"Sampling (%):",80)
        frame = Frame(self)
        Button(frame,text="Ok",command=self.validate,width=12).pack(side=LEFT,padx=5,pady=7)
        Button(frame,text="Cancel",command=self.destroy,width=12).pack(side=RIGHT,padx=5,pady=7)
        frame.pack(side=BOTTOM)
    
    def validate(self):
        name = self.name.get()
        directory = self.directory.get()
        listPointsClouds = self.listPointsClouds.get()
        listChunks = []
        for pointsCloud in listPointsClouds :
            if pointsCloud.nom == self.masterPC.get():
                targetPC = pointsCloud
            else :
                sourcePC = pointsCloud
            if not(pointsCloud.caliEtMEP.pointsLiaisons.chunk in listChunks) :
                listChunks.append(pointsCloud.caliEtMEP.pointsLiaisons.chunk)
        if self.matrixVar.get() == True :
            matrix = self.matrix.get()
        else :
            matrix = np.identity(4)
        maxIteration = self.maxIteration.get()
        sampling = int(self.sampling.get()) / 100
        extension = targetPC.caliEtMEP.pointsLiaisons.chunk.extension
        newChunk = MergedChunk("Chunk" + name, directory, extension, listChunks)
        newChunk.create()
        interface.listChunks.append(newChunk)
        interface.selectedObject = newChunk
        interface.currentChunk = newChunk
        newPointsLiaisons = PointsLiaisonsVide("PT" + name, "-1", newChunk)
        interface.currentChunk.listPointsLiaisons.append(newPointsLiaisons)
        interface.currentPointsLiaisons = newPointsLiaisons
        newCaliEtMEP = CaliEtMEPMergePC("Cali" + name, "Merge points clouds", interface.currentPointsLiaisons)
        interface.currentPointsLiaisons.listCaliEtMEP.append(newCaliEtMEP)
        interface.currentCaliEtMEP = newCaliEtMEP
        newNuagePoints = NuagePointsMerge(name, "Merge points clouds", targetPC.offset, targetPC, sourcePC, matrix, maxIteration, sampling, interface.currentCaliEtMEP)
        interface.currentCaliEtMEP.listNuagePoints.append(newNuagePoints)
        interface.currentNuagePoints = newNuagePoints
        interface.currentOrtho = 0
        self.destroy()
        interface.canvas.draw()
        
class TkDelete(Toplevel):
    def __init__(self) :
        super().__init__(interface)
        self.title("Delete selected objects")
        self.placeComponents()
           
    def placeComponents(self):
        Label(self,text="Are you sure to delete this object and all those that came from it ?",width=30, wraplength=200).pack()
        frame = Frame(self)
        Button(frame,text="Yes",command=self.validate,width=12).pack(side=LEFT,padx=5,pady=7)
        Button(frame,text="Cancel",command=self.destroy,width=12).pack(side=RIGHT,padx=5,pady=7)
        frame.pack(side=BOTTOM)
    
    def validate(self):
        interface.selectedObject.delete(interface)
        interface.currentPointsLiaisons = 0
        interface.currentCaliEtMEP = 0
        interface.currentNuagePoints = 0
        interface.currentOrtho = 0
        self.destroy()
        interface.canvas.draw()

class TkCompareCali(Toplevel):
    def __init__(self) :
        super().__init__(interface)
        self.title("Compare alignments")
        self.placeComponents()
    
    def placeComponents(self):
        #Calibration and alignement
        self.labelCali1 = Label(self,text="Calibration and alignment 1:",anchor=W,width=30)
        self.labelCali1.pack()
        self.caliName1 = ttk.Combobox(self,values=interface.getListCaliName(),width=27)
        self.caliName1.pack()
        self.labelCali2 = Label(self,text="Calibration and alignment 2:",anchor=W,width=30)
        self.labelCali2.pack()
        self.caliName2 = ttk.Combobox(self,values=interface.getListCaliName(),width=27)
        self.caliName2.pack()
        self.labelComparisonType = Label(self,text="Type of comparison:",anchor=W,width=30)
        self.labelComparisonType.pack()
        self.comparisonType = ttk.Combobox(self,values=["Position", "Angle"],width=27)
        self.comparisonType.pack()
        frame = Frame(self)
        Button(frame,text="Yes",command=self.validate,width=12).pack(side=LEFT,padx=5,pady=7)
        Button(frame,text="Cancel",command=self.destroy,width=12).pack(side=RIGHT,padx=5,pady=7)
        frame.pack(side=BOTTOM)
    
    def validate(self):
        for chunk in interface.listChunks :
            for pointsLiaison in chunk.listPointsLiaisons :
                for calibEtMEP in pointsLiaison.listCaliEtMEP :
                    if self.caliName1.get() == calibEtMEP.nom :
                        cali1 = calibEtMEP
                    if self.caliName2.get() == calibEtMEP.nom :
                        cali2 = calibEtMEP
        if self.comparisonType.get() == "Position" :
            TkComparePosiCali(cali1, cali2)
        elif self.comparisonType.get() == "Angle" :
            TkCompareAngleCali(cali1, cali2)
                

class TkComparePosiCali(Toplevel):
    def __init__(self, cali1, cali2) :
        super().__init__(interface)
        self.title("Result")
        self.cali1 = cali1
        self.cali2 = cali2
        self.listDistance, self.listDX, self.listDY, self.listDZ, self.listPhotos = comparePosiCali(self.cali1, self.cali2)
        onglets = ttk.Notebook(self)
        
        #Onglet Distances
        onglet1 = ttk.Frame(onglets)
        f1 = Figure(figsize=(7, 5), dpi=100)
        a1 = f1.add_subplot(111)
        a1.hist(self.listDistance)
        f1.gca().set_xlabel("Distances")
        f1.gca().set_ylabel("Count")
        f1.suptitle("Distances " + self.cali1.nom + "-" + self.cali2.nom)
        canvas1 = FigureCanvasTkAgg(f1, onglet1)
        canvas1.get_tk_widget().pack(fill=BOTH, expand=True)
        canvas1._tkcanvas.pack()
        Label(onglet1,text="Statistical results:",anchor=W).pack(fill=BOTH, expand=True)
        Label(onglet1,text=" - Min distance: "+str(min(self.listDistance)) + " (" + self.listPhotos[self.listDistance.index(min(self.listDistance))] + ")",anchor=W).pack(fill=BOTH, expand=True)
        Label(onglet1,text=" - Max distance: "+str(max(self.listDistance)) + " (" + self.listPhotos[self.listDistance.index(max(self.listDistance))] + ")",anchor=W).pack(fill=BOTH, expand=True)
        Label(onglet1,text=" - Avg distance: "+str(sum(self.listDistance)/len(self.listDistance)),anchor=W).pack(fill=BOTH, expand=True)
        onglets.add(onglet1, text="Distances")
        
        #Onglet DX
        onglet2 = ttk.Frame(onglets)
        f2 = Figure(figsize=(7, 5), dpi=100)
        a2 = f2.add_subplot(111)
        a2.hist(self.listDX)
        f2.gca().set_xlabel("dX")
        f2.gca().set_ylabel("Count")
        f2.suptitle("dX " + self.cali1.nom + "-" + self.cali2.nom)
        canvas2 = FigureCanvasTkAgg(f2, onglet2)
        canvas2.get_tk_widget().pack(fill=BOTH, expand=True)
        canvas2._tkcanvas.pack()
        Label(onglet2,text="Statistical results:",anchor=W).pack(fill=BOTH, expand=True)
        self.listDX = np.absolute(np.array(self.listDX))
        Label(onglet2,text=" - Min |dX|: "+str(np.min(self.listDX)),anchor=W).pack(fill=BOTH, expand=True)
        Label(onglet2,text=" - Max |dX|: "+str(np.max(self.listDX)),anchor=W).pack(fill=BOTH, expand=True)
        Label(onglet2,text=" - Avg |dX|: "+str(np.mean(self.listDX)),anchor=W).pack(fill=BOTH, expand=True)
        onglets.add(onglet2, text="dX")
        
        #Onglet DY
        onglet3 = ttk.Frame(onglets)
        f3 = Figure(figsize=(7, 5), dpi=100)
        a3 = f3.add_subplot(111)
        a3.hist(self.listDY)
        f3.gca().set_xlabel("dY")
        f3.gca().set_ylabel("Count")
        f3.suptitle("dY " + self.cali1.nom + "-" + self.cali2.nom)
        canvas3 = FigureCanvasTkAgg(f3, onglet3)
        canvas3.get_tk_widget().pack(fill=BOTH, expand=True)
        canvas3._tkcanvas.pack()
        Label(onglet3,text="Statistical results:",anchor=W).pack(fill=BOTH, expand=True)
        self.listDY = np.absolute(np.array(self.listDY))
        Label(onglet3,text=" - Min |dY|: "+str(np.min(self.listDY)),anchor=W).pack(fill=BOTH, expand=True)
        Label(onglet3,text=" - Max |dY|: "+str(np.max(self.listDY)),anchor=W).pack(fill=BOTH, expand=True)
        Label(onglet3,text=" - Avg |dY|: "+str(np.mean(self.listDY)),anchor=W).pack(fill=BOTH, expand=True)
        onglets.add(onglet3, text="dY")
        
        #Onglet DZ
        onglet4 = ttk.Frame(onglets)
        f4 = Figure(figsize=(7, 5), dpi=100)
        a4 = f4.add_subplot(111)
        a4.hist(self.listDZ)
        f4.gca().set_xlabel("dZ")
        f4.gca().set_ylabel("Count")
        f4.suptitle("dZ " + self.cali1.nom + "-" + self.cali2.nom)
        canvas4 = FigureCanvasTkAgg(f4, onglet4)
        canvas4.get_tk_widget().pack(fill=BOTH, expand=True)
        canvas4._tkcanvas.pack()
        Label(onglet4,text="Statistical results:",anchor=W).pack(fill=BOTH, expand=True)
        self.listDZ = np.absolute(np.array(self.listDZ))
        Label(onglet4,text=" - Min |dZ|: "+str(np.min(self.listDZ)),anchor=W).pack(fill=BOTH, expand=True)
        Label(onglet4,text=" - Max |dZ|: "+str(np.max(self.listDZ)),anchor=W).pack(fill=BOTH, expand=True)
        Label(onglet4,text=" - Avg |dZ|: "+str(np.mean(self.listDZ)),anchor=W).pack(fill=BOTH, expand=True)
        onglets.add(onglet4, text="dZ")
        
        onglets.pack()
        

class TkCompareAngleCali(Toplevel):
    def __init__(self, cali1, cali2) :
        super().__init__(interface)
        self.title("Result")
        self.cali1 = cali1
        self.cali2 = cali2    
        self.listDThetaX, self.listDThetaY, self.listDThetaZ, self.listPhotos = compareAngleCali(self.cali1, self.cali2)
        onglets = ttk.Notebook(self)
        
        #Onglet DThetaX
        onglet2 = ttk.Frame(onglets)
        f2 = Figure(figsize=(7, 5), dpi=100)
        a2 = f2.add_subplot(111)
        a2.hist(self.listDThetaX)
        f2.gca().set_xlabel("dThetaX (°)")
        f2.gca().set_ylabel("Count")
        f2.suptitle("dThetaX " + self.cali1.nom + "-" + self.cali2.nom)
        canvas2 = FigureCanvasTkAgg(f2, onglet2)
        canvas2.get_tk_widget().pack(fill=BOTH, expand=True)
        canvas2._tkcanvas.pack()
        Label(onglet2,text="Statistical results:",anchor=W).pack(fill=BOTH, expand=True)
        self.listDThetaX = np.absolute(np.array(self.listDThetaX))
        Label(onglet2,text=" - Min |dThetaX|: "+str(np.min(self.listDThetaX)),anchor=W).pack(fill=BOTH, expand=True)
        Label(onglet2,text=" - Max |dThetaX|: "+str(np.max(self.listDThetaX)),anchor=W).pack(fill=BOTH, expand=True)
        Label(onglet2,text=" - Avg |dThetaX|: "+str(np.mean(self.listDThetaX)),anchor=W).pack(fill=BOTH, expand=True)
        onglets.add(onglet2, text="dThetaX")
        
        #Onglet DThetaY
        onglet3 = ttk.Frame(onglets)
        f3 = Figure(figsize=(7, 5), dpi=100)
        a3 = f3.add_subplot(111)
        a3.hist(self.listDThetaY)
        f3.gca().set_xlabel("dThetaY (°)")
        f3.gca().set_ylabel("Count")
        f3.suptitle("dThetaY " + self.cali1.nom + "-" + self.cali2.nom)
        canvas3 = FigureCanvasTkAgg(f3, onglet3)
        canvas3.get_tk_widget().pack(fill=BOTH, expand=True)
        canvas3._tkcanvas.pack()
        Label(onglet3,text="Statistical results:",anchor=W).pack(fill=BOTH, expand=True)
        self.listDThetaY = np.absolute(np.array(self.listDThetaY))
        Label(onglet3,text=" - Min |dThetaY|: "+str(np.min(self.listDThetaY)),anchor=W).pack(fill=BOTH, expand=True)
        Label(onglet3,text=" - Max |dThetaY|: "+str(np.max(self.listDThetaY)),anchor=W).pack(fill=BOTH, expand=True)
        Label(onglet3,text=" - Avg |dThetaY|: "+str(np.mean(self.listDThetaY)),anchor=W).pack(fill=BOTH, expand=True)
        onglets.add(onglet3, text="dThetaY")
        
        #Onglet DThetaZ
        onglet4 = ttk.Frame(onglets)
        f4 = Figure(figsize=(7, 5), dpi=100)
        a4 = f4.add_subplot(111)
        a4.hist(self.listDThetaZ)
        f4.gca().set_xlabel("dThetaZ (°)")
        f4.gca().set_ylabel("Count")
        f4.suptitle("dThetaZ " + self.cali1.nom + "-" + self.cali2.nom)
        canvas4 = FigureCanvasTkAgg(f4, onglet4)
        canvas4.get_tk_widget().pack(fill=BOTH, expand=True)
        canvas4._tkcanvas.pack()
        Label(onglet4,text="Statistical results:",anchor=W).pack(fill=BOTH, expand=True)
        self.listDZ = np.absolute(np.array(self.listDThetaZ))
        Label(onglet4,text=" - Min |dThetaZ|: "+str(np.min(self.listDThetaZ)),anchor=W).pack(fill=BOTH, expand=True)
        Label(onglet4,text=" - Max |dThetaZ|: "+str(np.max(self.listDThetaZ)),anchor=W).pack(fill=BOTH, expand=True)
        Label(onglet4,text=" - Avg |dThetaZ|: "+str(np.mean(self.listDThetaZ)),anchor=W).pack(fill=BOTH, expand=True)
        onglets.add(onglet4, text="dThetaZ")
        
        onglets.pack()
        
class TkComparePointCloud(Toplevel):
    def __init__(self) :
        super().__init__(interface)
        self.title("Compare point clouds")
        self.placeComponents()
    
    def placeComponents(self):
        #Calibration and alignement
        self.labelPointCloud1 = Label(self,text="Point cloud 1:",anchor=W,width=30)
        self.labelPointCloud1.pack()
        self.PointCloudName1 = ttk.Combobox(self,values=interface.getListPCName(),width=27)
        self.PointCloudName1.pack()
        self.labelPointCloud2 = Label(self,text="Point cloud 2:",anchor=W,width=30)
        self.labelPointCloud2.pack()
        self.PointCloudName2 = ttk.Combobox(self,values=interface.getListPCName(),width=27)
        self.PointCloudName2.pack()
        frame = Frame(self)
        Button(frame,text="Yes",command=self.validate,width=12).pack(side=LEFT,padx=5,pady=7)
        Button(frame,text="Cancel",command=self.destroy,width=12).pack(side=RIGHT,padx=5,pady=7)
        frame.pack(side=BOTTOM)
    
    def validate(self):
        for chunk in interface.listChunks :
            for pointsLiaison in chunk.listPointsLiaisons :
                for calibEtMEP in pointsLiaison.listCaliEtMEP :
                    for nuagePoints in calibEtMEP.listNuagePoints :
                        if self.PointCloudName1.get() == nuagePoints.nom :
                            PC1 = nuagePoints
                        if self.PointCloudName2.get() == nuagePoints.nom :
                            PC2 = nuagePoints
        TkComparePosiPC(PC1, PC2)
    
class TkComparePosiPC(Toplevel):
    def __init__(self, PC1, PC2) :
        super().__init__(interface)
        self.title("Result")
        self.PC1 = PC1
        self.PC2 = PC2
        self.distances = comparePosiPC(self.PC1, self.PC2)
        f1 = Figure(figsize=(7, 5), dpi=100)
        a1 = f1.add_subplot(111)
        a1.hist(self.distances)
        f1.gca().set_xlabel("Distances")
        f1.gca().set_ylabel("Count")
        f1.suptitle("Distances " + self.PC1.nom + "-" + self.PC2.nom)
        canvas1 = FigureCanvasTkAgg(f1, self)
        canvas1.get_tk_widget().pack(fill=BOTH, expand=True)
        canvas1._tkcanvas.pack()
        Label(self,text="Statistical results:",anchor=W).pack(fill=BOTH, expand=True)
        Label(self,text=" - Min distance: "+str(np.min(self.distances)),anchor=W).pack(fill=BOTH, expand=True)
        Label(self,text=" - Max distance: "+str(np.max(self.distances)),anchor=W).pack(fill=BOTH, expand=True)
        Label(self,text=" - Avg distance: "+str(np.mean(self.distances)),anchor=W).pack(fill=BOTH, expand=True)
        
class CanvasArborescence(Canvas):
    def __init__(self, conteneur, interface, width, height, padx, pady, sizex, sizey) :
        super().__init__(conteneur, width=width, height=height)
        self.interface = interface
        self.width = width
        self.padx = padx
        self.pady = pady
        self.sizex = sizex
        self.sizey = sizey
        ## Chargement des images
        self.imgPlanned = PhotoImage(file="ressources/planned.png")
        self.imgOngoing = PhotoImage(file="ressources/ongoing.png")
        self.imgDone = PhotoImage(file="ressources/done.png")
        self.bind("<Button-1>", self.movement)
        self.draw()
        
    def movement(self, event):
        listForms = self.find_withtag("current")
        for form in listForms :
            if (self.gettags(form)[0] != "current") :
                operation = getOperation(int(self.gettags(form)[0]))
                operation.selected(interface, 0)
                self.draw()
    
    def update_scrollregion(self, n) :
        height = 800
        if n > 13 :
            height = 800 + (n - 13) * (2*self.pady + self.sizey)
        self.configure(scrollregion=(0, 0, self.width, height))
        
    def on_mousewheel(self, event) :
        self.yview_scroll(-1*(event.delta//120), "units")
        
    def draw(self):
        self.delete("all")
        self.drawHeader()
        n = 1
        for chunk in self.interface.listChunks:
            chunk.draw(self, n, 0, chunk == self.interface.currentChunk)
            a = n
            n += 1
            for pointsLiaison in chunk.listPointsLiaisons :
                b = n
                if not(isinstance(pointsLiaison, PointsLiaisonsVide)) :
                    pointsLiaison.draw(self, n, a, pointsLiaison == self.interface.currentPointsLiaisons)
                    n += 1
                else :
                    b -= 1
                for calibEtMEP in pointsLiaison.listCaliEtMEP :
                    calibEtMEP.draw(self, n, b, calibEtMEP == self.interface.currentCaliEtMEP)
                    c = n
                    n += 1
                    for nuagePoints in calibEtMEP.listNuagePoints :
                        nuagePoints.draw(self, n, c, nuagePoints == self.interface.currentNuagePoints)
                        d = n
                        n += 1
                        for ortho in nuagePoints.listOrthos :
                            ortho.draw(self, n, d, ortho == self.interface.currentOrtho)
                            n += 1
        self.update_scrollregion(n)
                        
    
    def drawHeader(self):
        x11 = 10 + self.padx
        x12 = 10 + self.padx + self.sizex
        x21 = 10 + 3 * self.padx + self.sizex
        x22 = 10 + 3 * self.padx + 2 * self.sizex
        x31 = 10 + 5 * self.padx + 2 * self.sizex
        x32 = 10 + 5 * self.padx + 3 * self.sizex
        x41 = 10 + 7 * self.padx + 3 * self.sizex
        x42 = 10 + 7 * self.padx + 4 * self.sizex
        x51 = 10 + 9 * self.padx + 4 * self.sizex
        x52 = 10 + 9 * self.padx + 5 * self.sizex
        y1 = 10 + self.pady 
        y2 = 10 + self.pady + self.sizey
        self.create_rectangle(x11, y1, x12, y2, outline="darkblue", width=2, fill="darkblue")
        self.create_rectangle(x21, y1, x22, y2, outline="darkred", width=2, fill="darkred")
        self.create_rectangle(x31, y1, x32, y2, outline="darkgreen", width=2, fill="darkgreen")
        self.create_rectangle(x41, y1, x42, y2, outline="darkviolet", width=2, fill="darkviolet")
        self.create_rectangle(x51, y1, x52, y2, outline="DarkGoldenrod3", width=2, fill="DarkGoldenrod3")
        self.create_text((x11+x12)/2, y1 + self.sizey/2, text="Chunk", fill="white")
        self.create_text((x21+x22)/2, y1 + self.sizey/2, text="Tie points", fill="white")
        self.create_text((x31+x32)/2, y1 + self.sizey/4, text="Calibration", fill="white")
        self.create_text((x31+x32)/2, y1 + 3*self.sizey/4, text="and alignment", fill="white")
        self.create_text((x41+x42)/2, y1 + self.sizey/2, text="Point Cloud", fill="white")
        self.create_text((x51+x52)/2, y1 + self.sizey/4, text="Photogrammetric", fill="white")
        self.create_text((x51+x52)/2, y1 + 3*self.sizey/4, text="products", fill="white")

class TkInterfaceMicMac(Tk):
    
    def __init__(self):
         super().__init__()
         self.title("Interface MicMac")
         ## Global values
         self.saveName = ""
         self.currentChunk = 0
         self.currentPointsLiaisons = 0
         self.currentCaliEtMEP = 0
         self.currentNuagePoints = 0
         self.currentOrtho = 0
         self.selectedObject = 0
         self.listChunks = []
         self.generateMenu()
         self.generateCanvas()
        
    def updateMenu(self, event):
        
        ## Edit Menu update
        
        self.editmenu.entryconfig(1, stat=DISABLED) # Delete selected object
        
        if self.selectedObject != 0 :
            self.editmenu.entryconfig(1, stat=ACTIVE) # Delete selected object
        
        ## Workflow Menu update
        
        self.workflowmenu.entryconfig(0, stat=DISABLED) # Find tie points
        self.workflowmenu.entryconfig(1, stat=DISABLED) # Calculate calibration and align photos
        self.workflowmenu.entryconfig(2, stat=DISABLED) # Switch to a new coordinate system
        self.workflowmenu.entryconfig(3, stat=DISABLED) # Build dense cloud
        self.workflowmenu.entryconfig(4, stat=DISABLED) # Build orthomosaic
        self.workflowmenu.entryconfig(5, stat=DISABLED) # Build mesh
        self.workflowmenu.entryconfig(7, stat=DISABLED) # Merge chunks
        self.workflowmenu.entryconfig(8, stat=DISABLED) # Merge points cloud
        
        if self.currentChunk != 0:
            self.workflowmenu.entryconfig(0, stat=ACTIVE) # Find tie points
        if self.currentPointsLiaisons != 0:
            self.workflowmenu.entryconfig(1, stat=ACTIVE) # Calculate calibration and align photos
        if self.currentCaliEtMEP != 0:
            self.workflowmenu.entryconfig(2, stat=ACTIVE) # Switch to a new coordinate system
            self.workflowmenu.entryconfig(3, stat=ACTIVE) # Build dense cloud
        if self.currentNuagePoints != 0:
            self.workflowmenu.entryconfig(4, stat=ACTIVE) # Build orthomosaic
            self.workflowmenu.entryconfig(5, stat=ACTIVE) # Build mesh
        if len(self.listChunks) > 1 :
            self.workflowmenu.entryconfig(7, stat=ACTIVE) # Merge chunks
            self.workflowmenu.entryconfig(8, stat=ACTIVE) # Merge points cloud
            
        ## Run Menu update
        
        if self.selectedObject != 0 and not(self.selectedObject.done):
            self.runmenu.entryconfig(0, stat=ACTIVE)
        else :
            self.runmenu.entryconfig(0, stat=DISABLED)
            
        ## View Menu update
        
        self.viewmenu.entryconfig(0, stat=DISABLED)
        
        if self.selectedObject != 0 and self.selectedObject.done and (isinstance(self.selectedObject, CaliEtMEP) or isinstance(self.selectedObject, NuagePoints) or isinstance(self.selectedObject, Mesh) or isinstance(self.selectedObject, Ortho)):
            self.viewmenu.entryconfig(0, stat=ACTIVE)
        
    
    def generateMenu(self):
        self.menubar = Menu(self)
        self.menubar.bind("<<MenuSelect>>", self.updateMenu)

        ## 1 - File Menu
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="New", command=self.reset)
        self.filemenu.add_command(label="Open", command=self.load)
        self.filemenu.add_command(label="Save", command=self.save)
        self.filemenu.add_command(label="Save as...", command=self.saveAs)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.destroy)
        self.filemenu.bind("<<MennuSelect>>", self.updateMenu)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        
        ## 2 - Edit Menu
        self.editmenu = Menu(self.menubar, tearoff=0)
        self.editmenu.add_command(label="Add Chunk", command=TkNewChunk)
        self.editmenu.add_command(label="Delete selected object", command=TkDelete)
        self.editmenu.bind("<<MennuSelect>>", self.updateMenu)
        self.menubar.add_cascade(label="Edit", menu=self.editmenu)
        
        ## 3 - Workflow Menu
        self.workflowmenu = Menu(self.menubar, tearoff=0)
        self.workflowmenu.add_command(label="Find tie points", command=TkFindTiePoints)
        self.workflowmenu.add_command(label="Calculate calibration and align photos", command=self.TkCali)
        self.workflowmenu.add_command(label="Switch to a new coordinate system", command=TkSwitchSystem)
        self.workflowmenu.add_command(label="Build dense cloud", command=TkBuildCloud)
        self.workflowmenu.add_command(label="Build orthomosaic", command=TkBuildOrtho)
        self.workflowmenu.add_command(label="Build mesh", command=TkBuildMesh)
        self.workflowmenu.add_separator()
        self.workflowmenu.add_command(label="Merge chunks", command=TkMergeChunks)
        self.workflowmenu.add_command(label="Merge points cloud", command=TkMergePointsCloud)
        self.menubar.add_cascade(label="Workflow", menu=self.workflowmenu)
        
        ## 4 - Run Menu
        self.runmenu = Menu(self.menubar, tearoff=0)
        self.runmenu.add_command(label="Execute selected workflow", command=self.run)
        self.runmenu.add_command(label="Execute all", command=self.runAll)
        self.menubar.add_cascade(label="Run", menu=self.runmenu)
        
        ## 5 - View Menu
        self.viewmenu = Menu(self.menubar, tearoff=0)
        self.viewmenu.add_command(label="View selected object", command=self.view)
        self.menubar.add_cascade(label="View", menu=self.viewmenu)
        
        ## 6 - Tools Menu
        self.toolsmenu = Menu(self.menubar, tearoff=0)
        self.toolsmenu.add_command(label="Compare alignments", command=TkCompareCali)
        self.toolsmenu.add_command(label="Compare point clouds", command=TkComparePointCloud)
        self.menubar.add_cascade(label="Tools", menu=self.toolsmenu)
        
        self.config(menu=self.menubar)
    
    def generateCanvas(self):
        
        padx = 20 
        pady = 10
        sizex = 120 
        sizey = 40
        canvas_width = 20 + 10 * padx + 5 * 120
        canvas_height = 800
        
        self.mainFrame = Frame(self, width=canvas_width, height=canvas_height)
        self.mainFrame.grid(row=0, column=0)
        
        self.canvas = CanvasArborescence(self.mainFrame, self, canvas_width, canvas_height, padx, pady, sizex, sizey)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind_all("<MouseWheel>", self.canvas.on_mousewheel)
        
        self.vbar = Scrollbar(self.mainFrame, orient=VERTICAL)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.vbar.set)
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)        

    
    def run(self):
        self.selectedObject.run(self)
    
    def runAll(self):
        for chunk in self.listChunks :
            if not(chunk.done):
                chunk.run(self)
            for pointsLiaisons in chunk.listPointsLiaisons :
                if not(pointsLiaisons.done):
                    pointsLiaisons.run(self)
                for caliEtMEP in pointsLiaisons.listCaliEtMEP :
                    if not(caliEtMEP.done):
                        caliEtMEP.run(self)
                    for nuagePoints in caliEtMEP.listNuagePoints :
                        if not(nuagePoints.done):
                            nuagePoints.run(self)
                        for ortho in nuagePoints.listOrthos :
                            if not(ortho.done):
                                ortho.run(self)
    
    def view(self):
        if isinstance(self.selectedObject, Ortho):
            os.system("\"" + self.selectedObject.nuagePoints.caliEtMEP.pointsLiaisons.chunk.dossier + "/PIMs-ORTHO-"+self.selectedObject.nom + "/Orthophotomosaic.tif\"")
        elif isinstance(self.selectedObject, NuagePoints):
            os.system("\"" + self.selectedObject.caliEtMEP.pointsLiaisons.chunk.dossier + "/"+self.selectedObject.nom+".ply\"")
        elif isinstance(self.selectedObject, CaliEtMEP):
            os.system("\"" + self.selectedObject.pointsLiaisons.chunk.dossier + "/Align-" + self.selectedObject.nom+".ply\"")
        elif isinstance(self.selectedObject, Mesh):
            if self.selectedObject.textured :
                os.system("\"" + self.selectedObject.nuagePoints.caliEtMEP.pointsLiaisons.chunk.dossier + "/" + self.selectedObject.nom + "-textured.ply\"")
            else :
                os.system("\"" + self.selectedObject.nuagePoints.caliEtMEP.pointsLiaisons.chunk.dossier + "/" + self.selectedObject.nom + ".ply\"")

        
    def save(self) :
        
        if self.saveName == "" :
            self.saveAs()
        
        ficSave = open(self.saveName, "w")
        for chunk in self.listChunks :
            ficSave.write(chunk.save())
            for pointsLiaisons in chunk.listPointsLiaisons :
                ficSave.write(pointsLiaisons.save())
                for caliEtMEP in pointsLiaisons.listCaliEtMEP :
                    ficSave.write(caliEtMEP.save())
                    for nuagePoints in caliEtMEP.listNuagePoints :
                        ficSave.write(nuagePoints.save())
                        for ortho in nuagePoints.listOrthos :
                            ficSave.write(ortho.save())
        ficSave.close()
        
        print("\nSauvegarde effectuee")
    
    def saveAs(self) :
        if not("saveInterfaceMicMac" in os.listdir("/")) :
            os.system("md saveInterfaceMicMac")

        self.saveName = asksaveasfilename(initialdir="/saveInterfaceMicMac", title="Select file", filetypes=(("text files", "*.txt"),("all files", "*.*")))
        print(self.saveName)
        self.save()
    
    def load(self) :
        
        if not("saveInterfaceMicMac" in os.listdir("/")) :
            os.system("md saveInterfaceMicMac")
            
        self.reset()
        
        self.saveName = askopenfilename(initialdir="/saveInterfaceMicMac")

    
        ficLoad = open(self.saveName, "r")
    
        for line in ficLoad.readlines() :
            line = line.replace("\n", "").split("\t")
            if line[0] == "Chunk" :
                ## Chargememt d'un chunk
                chunkLoaded = Chunk(line[1], line[2], line[3])
                self.listChunks.append(chunkLoaded)
                self.currentChunk = chunkLoaded
            elif line[0] == "MergedChunk" :
                ## Chargememt d'un chunk issu d'une fusion
                nbreChunk = int(line[4])
                listChunks = []
                for i in range(5, 5 + nbreChunk):
                    nomChunk = line[i]
                    for chunk in self.listChunks :
                        if chunk.nom == nomChunk :
                            listChunks.append(chunk)
                            break
                chunkLoaded = MergedChunk(line[1], line[2], line[3], listChunks)
                self.listChunks.append(chunkLoaded)
                self.currentChunk = chunkLoaded
            elif line[0] == "PointsLiaisons" :
                ## Chargement de points de liaison
                pointsLiaisonsLoaded = PointsLiaisons(line[1], line[2], self.currentChunk)
                if line[4] == "done" :
                    pointsLiaisonsLoaded.done = True
                    pointsLiaisonsLoaded.getNbrePtsLiaisons()
                self.currentChunk.listPointsLiaisons.append(pointsLiaisonsLoaded)
                self.currentPointsLiaisons = pointsLiaisonsLoaded
            elif line[0] == "PointsLiaisonsAll" :
                ## Chargememt de points de liaison mode All
                pointsLiaisonsLoaded = PointsLiaisonsAll(line[1], line[2], self.currentChunk)
                if line[4] == "done" :
                    pointsLiaisonsLoaded.done = True
                    pointsLiaisonsLoaded.getNbrePtsLiaisons()
                self.currentChunk.listPointsLiaisons.append(pointsLiaisonsLoaded)
                self.currentPointsLiaisons = pointsLiaisonsLoaded
            elif line[0] == "PointsLiaisonsGPS" :
                ## Chargememt de points de liaison mode GPS coordinates
                pointsLiaisonsLoaded = PointsLiaisonsGPS(line[1], line[2], line[3], self.currentChunk)
                if line[5] == "done" :
                    pointsLiaisonsLoaded.done = True
                    pointsLiaisonsLoaded.getNbrePtsLiaisons()
                self.currentChunk.listPointsLiaisons.append(pointsLiaisonsLoaded)
                self.currentPointsLiaisons = pointsLiaisonsLoaded
            elif line[0] == "PointsLiaisonsLine" :
                ## Chargememt de points de liaison mode Line
                if line[4] == "Oui" :
                    pointsLiaisonsLoaded = PointsLiaisonsLine(line[1], line[2], self.currentChunk, line[3], True)
                else :
                    pointsLiaisonsLoaded = PointsLiaisonsLine(line[1], line[2], self.currentChunk, line[3], False)
                if line[6] == "done" :
                    pointsLiaisonsLoaded.done = True
                    pointsLiaisonsLoaded.getNbrePtsLiaisons()
                self.currentChunk.listPointsLiaisons.append(pointsLiaisonsLoaded)
                self.currentPointsLiaisons = pointsLiaisonsLoaded
            elif line[0] == "PointsLiaisonsMuscale" :
                ## Chargememt de points de liaison mode Mulscale
                pointsLiaisonsLoaded = PointsLiaisonsMulscale(line[1], line[2], self.currentChunk, line[3])
                if line[5] == "done" :
                    pointsLiaisonsLoaded.done = True
                    pointsLiaisonsLoaded.getNbrePtsLiaisons()
                self.currentChunk.listPointsLiaisons.append(pointsLiaisonsLoaded)
                self.currentPointsLiaisons = pointsLiaisonsLoaded
            elif line[0] == "PointsLiaisonsVide" :
                ## Chargememt de points de liaison vide
                pointsLiaisonsLoaded = PointsLiaisonsVide(line[1], line[2], self.currentChunk)
                self.currentChunk.listPointsLiaisons.append(pointsLiaisonsLoaded)
                self.currentPointsLiaisons = pointsLiaisonsLoaded
            elif line[0] == "CaliEtMEP" :
                ## Chargement d'une calibration et d'une mise en place
                caliEtMEPLoaded = CaliEtMEP(line[1], line[2], self.currentPointsLiaisons)
                if line[4] == "done" :
                    caliEtMEPLoaded.done = True
                    caliEtMEPLoaded.getNbreImageOrientee()
                self.currentPointsLiaisons.listCaliEtMEP.append(caliEtMEPLoaded)
                self.currentCaliEtMEP = caliEtMEPLoaded
            elif line[0] == "CaliEtMEPFigee" :
                ## Chargement d'une calibration utilisant le mode Figee
                caliEtMEPLoaded = CaliEtMEPFigee(line[1], line[2], line[3], self.currentPointsLiaisons)
                if line[5] == "done" :
                    caliEtMEPLoaded.done = True
                    caliEtMEPLoaded.getNbreImageOrientee()
                self.currentPointsLiaisons.listCaliEtMEP.append(caliEtMEPLoaded)
                self.currentCaliEtMEP = caliEtMEPLoaded
            elif line[0] == "CaliEtMEPBasculeGPS" :
                ## Chargement d'une bascule par GPS
                caliEtMEPRelatif = 0
                for caliEtMEP in self.currentPointsLiaisons.listCaliEtMEP :
                    if caliEtMEP.nom == line[4] :
                        caliEtMEPRelatif = caliEtMEP
                caliEtMEPLoaded = CaliEtMEPBasculeGPS(line[1], line[2], line[3], self.currentPointsLiaisons, caliEtMEPRelatif)
                if line[6] == "done" :
                    caliEtMEPLoaded.done = True
                    caliEtMEPLoaded.getNbreImageOrientee()
                self.currentPointsLiaisons.listCaliEtMEP.append(caliEtMEPLoaded)
                self.currentCaliEtMEP = caliEtMEPLoaded
            elif line[0] == "CaliEtMEPBasculeGCP" :
                ## Chargement d'une bascule par GCP
                caliEtMEPRelatif = 0
                for caliEtMEP in self.currentPointsLiaisons.listCaliEtMEP :
                    if caliEtMEP.nom == line[5] :
                        caliEtMEPRelatif = caliEtMEP
                caliEtMEPLoaded = CaliEtMEPBasculeGCP(line[1], line[2], self.currentPointsLiaisons, line[3], line[4], caliEtMEPRelatif)
                if line[7] == "done" :
                    caliEtMEPLoaded.done = True
                    caliEtMEPLoaded.getNbreImageOrientee()
                self.currentPointsLiaisons.listCaliEtMEP.append(caliEtMEPLoaded)
                self.currentCaliEtMEP = caliEtMEPLoaded
            elif line[0] == "CaliEtMEPMerge" :
                ## Chargement d'une calibration et d'une mise en place pour chunk issu d'une fusion de chunks
                nbreCali = int(line[4])
                listCali = []
                listAlign = []
                for i in range(5, 5 + nbreCali):
                    nomCali = line[i]
                    isAlign = line[i+nbreCali]
                    for pointsLiaisons in self.currentChunk.listChunks[len(listCali)].listPointsLiaisons :
                        for cali in pointsLiaisons.listCaliEtMEP :
                            if cali.nom == nomCali :
                                listCali.append(cali)
                                break
                        if len(listCali) > len(listAlign) :
                            break
                    if isAlign == "True" :
                        listAlign.append(True)
                    else :
                        listAlign.append(False)
                caliEtMEPRelatif = 0
                caliEtMEPLoaded = CaliEtMEPMerge(line[1], line[2], listCali, listAlign, self.currentPointsLiaisons)
                if line[5 + 2*nbreCali] == "done" :
                    caliEtMEPLoaded.done = True
                    caliEtMEPLoaded.getNbreImageOrientee()
                self.currentPointsLiaisons.listCaliEtMEP.append(caliEtMEPLoaded)
                self.currentCaliEtMEP = caliEtMEPLoaded
            elif line[0] == "CaliEtMEPMergePC" :
                ## Chargement d'une calibration et d'une mise en place pour chunk issu d'une fusion de nuage de points
                caliEtMEPLoaded = CaliEtMEPMergePC(line[1], line[2], self.currentPointsLiaisons)
                if line[4] == "done" :
                    caliEtMEPLoaded.done = True
                    caliEtMEPLoaded.getNbreImageOrientee()
                self.currentPointsLiaisons.listCaliEtMEP.append(caliEtMEPLoaded)
                self.currentCaliEtMEP = caliEtMEPLoaded
            elif line[0] == "NuagePoints" :
                ## Chargement d'un nuage de points
                nuagePointsLoaded = NuagePoints(line[1], line[2], line[3], self.currentCaliEtMEP)
                if line[5] == "done" :
                    nuagePointsLoaded.done = True
                    nuagePointsLoaded.getNbrePoints()
                self.currentCaliEtMEP.listNuagePoints.append(nuagePointsLoaded)
                self.currentNuagePoints = nuagePointsLoaded
            elif line[0] == "NuagePointsMerge" :
                ## Chargement d'un nuage de points issu d'une fusion
                nameTarget = line[4]
                nameSource = line[5]
                for chunk in self.listChunks :
                    for pointsLiaison in chunk.listPointsLiaisons :
                        for cali in pointsLiaison.listCaliEtMEP :
                            for nuagePoints in cali.listNuagePoints :
                                if nuagePoints.nom == nameTarget :
                                    targetPC = nuagePoints
                                if nuagePoints.nom == nameSource :
                                    sourcePC = nuagePoints
                matrix = np.array([[float(line[6]), float(line[7]), float(line[8]), float(line[9])], [float(line[10]), float(line[11]), float(line[12]), float(line[13])], [float(line[14]), float(line[15]), float(line[16]), float(line[17])], [float(line[18]), float(line[19]), float(line[20]), float(line[21])]])
                nuagePointsLoaded = NuagePointsMerge(line[1], line[2], line[3], targetPC, sourcePC, matrix, float(line[22]), float(line[23]), self.currentCaliEtMEP)
                if line[25] == "done" :
                    nuagePointsLoaded.done = True
                    nuagePointsLoaded.getNbrePoints()
                self.currentCaliEtMEP.listNuagePoints.append(nuagePointsLoaded)
                self.currentNuagePoints = nuagePointsLoaded
            elif line[0] == "Ortho" :
                ## Chargement d'une orthophoto
                if line[3] == "Oui" :
                    orthoLoaded = Ortho(line[1], line[2], True, self.currentNuagePoints)
                else :
                    orthoLoaded = Ortho(line[1], line[2], False, self.currentNuagePoints)
                if line[5] == "done" :
                    orthoLoaded.done = True
                self.currentNuagePoints.listOrthos.append(orthoLoaded)
                self.currentOrtho = orthoLoaded
            elif line[0] == "Mesh" :
                ## Chargement d'un  mesh
                if line[3] == "True" :
                    meshLoaded = Mesh(line[1], line[2], True, self.currentNuagePoints)
                else :
                    meshLoaded = Mesh(line[1], line[2], False, self.currentNuagePoints)
                if line[5] == "done" :
                    meshLoaded.done = True
                    meshLoaded.getNbreFaces()
                self.currentNuagePoints.listOrthos.append(meshLoaded)
                self.currentOrtho = meshLoaded
    
        ficLoad.close()
        
        self.currentChunk = 0
        self.currentPointsLiaisons = 0
        self.currentCaliEtMEP = 0
        self.currentNuagePoints = 0
        self.currentOrtho = 0
        self.selectedObject = 0
        
        self.canvas.draw()
        
    def reset(self) :
        self.currentChunk = 0
        self.currentPointsLiaisons = 0
        self.currentCaliEtMEP = 0
        self.currentNuagePoints = 0
        self.currentOrtho = 0
        self.selectedObject = 0
        self.listChunks = []
        self.canvas.draw()  
        
    def TkCali(self) :
        if isinstance(self.currentChunk, MergedChunk):
            TkCalcCalibMergedChunk()
        else :
            TkCalcCalib()
    
    def getListPointsClouds(self) :
        listPointsClouds = []
        for i in range (len(self.listChunks)) :
            listPointsClouds.append([])
            for pointsLiaison in self.listChunks[i].listPointsLiaisons :
                for calibEtMEP in pointsLiaison.listCaliEtMEP :
                    for nuagePoints in calibEtMEP.listNuagePoints :
                        listPointsClouds[i].append(nuagePoints)
            if len(listPointsClouds[-1]) == 0 :
                listPointsClouds.pop()
        return listPointsClouds
    
    def getListCaliName(self) :
        listCali = []
        for i in range (len(self.listChunks)) :
            for pointsLiaison in self.listChunks[i].listPointsLiaisons :
                for calibEtMEP in pointsLiaison.listCaliEtMEP :
                    listCali.append(calibEtMEP.nom)
        return listCali
    
    def getListPCName(self) :
        listPC = []
        for i in range (len(self.listChunks)) :
            for pointsLiaison in self.listChunks[i].listPointsLiaisons :
                for calibEtMEP in pointsLiaison.listCaliEtMEP :
                    for nuagePoints in calibEtMEP.listNuagePoints :
                        listPC.append(nuagePoints.nom)
        return listPC
           
def getOperation(i):
    n = 1
    for chunk in interface.listChunks:
        if n == i :
            return chunk
        n += 1
        for pointsLiaison in chunk.listPointsLiaisons :
            if not(isinstance(pointsLiaison, PointsLiaisonsVide)) :
                if n == i :
                    return pointsLiaison
                n += 1
            for calibEtMEP in pointsLiaison.listCaliEtMEP :
                if n == i :
                    return calibEtMEP
                n += 1
                for nuagePoints in calibEtMEP.listNuagePoints :
                    if n == i :
                        return nuagePoints
                    n += 1
                    for ortho in nuagePoints.listOrthos :
                        if n == i :
                            return ortho
                        n += 1

interface = TkInterfaceMicMac()
interface.mainloop()
