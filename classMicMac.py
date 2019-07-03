import os
from tkinter import *
import inspect
import ICPPython
import copy
from plyfile import PlyData, PlyElement
import numpy as np

## Classes :

class Chunk :
    def __init__(self, nom, dossier, extension) :
        self.nom = nom
        self.dossier = dossier
        self.extension = extension
        self.listPointsLiaisons = []
        self.done = True
        self.ongoing = False

    def getNbrePhotos(self) :
        nbrePhotos = 0
        listFic = os.listdir(self.dossier)
        for fic in listFic :
            if "." + self.extension in fic :
                nbrePhotos += 1
        return nbrePhotos

#    def afficher(self) :
#        if self == currentChunk :
#            print(" + " + str(self.nom) + " (" + str(self.getNbrePhotos()) + " photos)")
#        else :
#            print(" - " + str(self.nom) + " (" + str(self.getNbrePhotos()) + " photos)")
#        for ptsLiaisons in self.listPointsLiaisons :
#            ptsLiaisons.afficher()
    
    def selected(self, interface, position):
        interface.currentChunk = self
        if position == 0 :
            interface.currentPointsLiaisons = 0
            interface.currentCaliEtMEP = 0
            interface.currentNuagePoints = 0
            interface.currentOrtho = 0
            interface.selectedObject = self 
    
    def delete(self, interface) :
        interface.listChunks.remove(self)
        
            
    def draw(self, canvas, n, nPrec, selected):
        x1 = 10 + canvas.padx
        y1 = 10 + (2*n + 1) * canvas.pady + n * canvas.sizey
        x2 = 10 + canvas.padx + canvas.sizex
        y2 = 10 + (2*n + 1) * canvas.pady + (n+1) * canvas.sizey
        if selected :
            canvas.create_rectangle(x1, y1, x2, y2, outline="cyan", width=8, fill="cyan", tags=str(n))
        canvas.create_rectangle(x1, y1, x2, y2, outline="darkblue", width=2, fill="darkblue", activefill="blue", tags=str(n))
        canvas.create_text((x1+x2)/2, y1 + canvas.sizey/4, text=self.nom, fill="white", tags=str(n))
        canvas.create_text((x1+x2)/2, y1 + 3*canvas.sizey/4, text=str(self.getNbrePhotos()) + " photos", fill="white", tags=str(n))
        if self.done :
            canvas.create_image(x2, y1, image=canvas.imgDone)
        elif self.ongoing :
            canvas.create_image(x2, y1, image=canvas.imgOngoing)
        else :
            canvas.create_image(x2, y1, image=canvas.imgPlanned)

    def save(self) :
        return "Chunk\t" + self.nom + "\t" + self.dossier.replace("\\", "/") + "\t" + self.extension + "\n";
    
class MergedChunk(Chunk) :
    def __init__(self, nom, dossier, extension, listChunks) :
        Chunk.__init__(self, nom, dossier, extension)
        self.listChunks = listChunks
        
    def create(self): 
        #Copy of photos
        print("---- Copy of photos ----\n")
        for chunk in self.listChunks :
            os.system("copy /y \"" + chunk.dossier + "\\*." + chunk.extension + "\" \"" + self.dossier + "\"")

    def save(self) :
        saveText = "MergedChunk\t" + self.nom + "\t" + self.dossier.replace("\\", "/") + "\t" + self.extension + "\t" + str(len(self.listChunks))
        for chunk in self.listChunks :
            saveText += "\t" + chunk.nom
        return saveText + "\n";

class PointsLiaisons :
    def __init__(self, nom, resolution, chunk) :
        self.nom = nom
        self.resolution = resolution
        self.listCaliEtMEP = []
        self.chunk = chunk
        self.nbrePoints = "???"
        self.done = False
        self.ongoing = False

    def run(self, interface) :
        self.ongoing = True
        interface.canvas.draw()
        os.chdir(self.chunk.dossier)
        os.system("mm3d Tapioca " + "All" + " \".*" + self.chunk.extension + "\" " + self.resolution + " PostFix=" + self.nom + "\n")
        self.getNbrePtsLiaisons()
        self.ongoing =False
        self.done = True
        interface.canvas.draw()
        
    def delete(self, interface) :
        self.chunk.listPointsLiaisons.remove(self)
        

    def getNbrePtsLiaisons(self) :
        nbrePtsLiaisons = 0
        for dossier in os.listdir(self.chunk.dossier + "/Pastis") :
            if os.path.isdir(self.chunk.dossier + "/Pastis/" + dossier) :
                for fichier in os.listdir(self.chunk.dossier + "/Pastis/" + dossier) :
                    fd = open(self.chunk.dossier + "/Pastis/" + dossier + "/" + fichier, "r")
                    while fd.readline() :
                        nbrePtsLiaisons += 1
        self.nbrePoints = nbrePtsLiaisons

#    def afficher(self) :
#        if self == currentPointsLiaisons :
#            print("        |-> + " + str(self.nom) + " (" + str(self.getNbrePtsLiaisons()) + " points de liaisons)")
#        else :
#            print("        |-> - " + str(self.nom) + " (" + str(self.getNbrePtsLiaisons()) + " points de liaisons)")
#        print("        |    Res : " + str(self.resolution))
#        for caliEtMEP in self.listCaliEtMEP :
#            caliEtMEP.afficher()
    
    def selected(self, interface, position):
        interface.currentPointsLiaisons = self
        if position == 0 :
            interface.currentCaliEtMEP = 0
            interface.currentNuagePoints = 0
            interface.currentOrtho = 0
            interface.selectedObject = self
        self.chunk.selected(interface, position + 1)
    
    def draw(self, canvas, n, nPrec, selected):
        x1 = 10 + 3 * canvas.padx + canvas.sizex
        y1 = 10 + (2*n + 1) * canvas.pady + n * canvas.sizey
        x2 = 10 + 3 * canvas.padx + 2 * canvas.sizex
        y2 = 10 + (2*n + 1) * canvas.pady + (n+1) * canvas.sizey
        dn = n - nPrec
        x3, y3 = 10 + canvas.padx + canvas.sizex//2, 10 + (2*nPrec + 1) * canvas.pady + (nPrec+1) * canvas.sizey
        x4, y4 = x3, y3 + 2 * dn * canvas.pady + (dn-1) * canvas.sizey + canvas.sizey//2 
        x5, y5 = x4 + canvas.sizex//2 + 2 * canvas.padx, y4
        if selected :
            canvas.create_rectangle(x1, y1, x2, y2, outline="cyan", width=8, fill="cyan", tags=str(n))
            canvas.create_line(x3, y3 + 3, x4, y4 + 3, width=5, fill="cyan")
            canvas.create_line(x4 - 2, y4, x5 - 2, y5, width=5, fill="cyan")
        else :
            canvas.create_line(x3, y3, x4, y4 + 1, width=3)
            canvas.create_line(x4 - 1, y4, x5 - 1, y5, width=3)
        canvas.create_rectangle(x1, y1, x2, y2, outline="darkred", width=2, fill="darkred", activefill="red", tags=str(n))
        canvas.create_text((x1+x2)/2, y1 + canvas.sizey/4, text=self.nom, fill="white", tags=str(n))
        canvas.create_text((x1+x2)/2, y1 + 3*canvas.sizey/4, text=str(self.nbrePoints) + " tie points", fill="white", tags=str(n))
        if self.done:
            canvas.create_image(x2, y1, image=canvas.imgDone)
        elif self.ongoing :
            canvas.create_image(x2, y1, image=canvas.imgOngoing)
        else :
            canvas.create_image(x2, y1, image=canvas.imgPlanned)

    def save(self) :
        if self.done :
            return "PointsLiaisons\t" + self.nom + "\t" + self.resolution + "\t" + self.chunk.nom + "\tdone\n";
        else :
            return "PointsLiaisons\t" + self.nom + "\t" + self.resolution + "\t" + self.chunk.nom + "\tplanned\n";


class PointsLiaisonsAll(PointsLiaisons) :
    def __init__(self, nom, resolution, chunk) :
        PointsLiaisons.__init__(self, nom, resolution, chunk)

    def calculPointsLiaisons(self) :
        os.chdir(self.chunk.dossier)
        os.system("mm3d Tapioca " + "All" + " \".*" + self.chunk.extension + "\" " + self.resolution + " PostFix=" + self.nom + "\n")

#    def afficher(self) :
#        if self == currentPointsLiaisons :
#            print("        |-> + " + str(self.nom) + " <All> (" + str(self.getNbrePtsLiaisons()) + " points de liaisons)")
#        else :
#            print("        |-> - " + str(self.nom) + " <All> (" + str(self.getNbrePtsLiaisons()) + " points de liaisons)")
#        print("        |    Res : " + str(self.resolution))
#        for caliEtMEP in self.listCaliEtMEP :
#            caliEtMEP.afficher()

    def save(self) :
        if self.done :
            return "PointsLiaisonsAll\t" + self.nom + "\t" + self.resolution + "\t" + self.chunk.nom + "\tdone\n";
        else :
            return "PointsLiaisonsAll\t" + self.nom + "\t" + self.resolution + "\t" + self.chunk.nom + "\tplanned\n";
        
class PointsLiaisonsGPS(PointsLiaisons) :
    def __init__(self, nom, resolution, proj4, chunk) :
        PointsLiaisons.__init__(self, nom, resolution, chunk)
        self.proj4 = proj4

    def run(self, interface) :
        self.ongoing = True
        interface.canvas.draw()
        path = os.path.dirname(os.path.abspath(inspect.getfile(lambda:None)))
        os.system("copy /y \"" + path + "\\ressources\\proj.xml\" \"" + self.chunk.dossier.replace("/","\\") + "\"")
        os.chdir(self.chunk.dossier)
        ficProj = open("proj.xml", "r")
        newFic = []
        for line in ficProj.readlines() :
             newFic.append(line.replace("A REMPLACER", self.proj4))
        ficProj.close()
        ficProj = open("proj.xml", "w")
        for line in newFic :
             ficProj.write(line)
        ficProj.close()        
        os.system("mm3d XifGps2Txt " + " \".*" + self.chunk.extension + "\" OutTxtFile=GpsCoordinatesFromExif.txt")
        os.system("mm3d OriConvert \"#F=N_X_Y_Z\" GpsCoordinatesFromExif.txt GPS NameCple=Couples.xml ChSys=DegreeWGS84@proj.xml")
        os.system("mm3d Tapioca File Couples.xml " + str(self.resolution) + " PostFix=" + self.nom)
        self.getNbrePtsLiaisons()
        self.ongoing =False
        self.done = True
        interface.canvas.draw()
                  
    def save(self) :
        if self.done :
            return "PointsLiaisonsGPS\t" + self.nom + "\t" + self.resolution + "\t" + self.proj4 + "\t" + self.chunk.nom + "\tdone\n";
        else :
            return "PointsLiaisonsGPS\t" + self.nom + "\t" + self.resolution + "\t" + self.proj4 + "\t" + self.chunk.nom + "\tplanned\n";

class PointsLiaisonsLine(PointsLiaisons) :
    def __init__(self, nom, resolution, chunk, nbreImage, circulaire) :
        PointsLiaisons.__init__(self, nom, resolution, chunk)
        self.nbreImage = nbreImage
        self.circulaire = circulaire

    def run(self, interface) :
        self.ongoing = True
        interface.canvas.draw()
        os.chdir(self.chunk.dossier)
        if self.circulaire :
            os.system("mm3d Tapioca " + "Line" + " \".*" + self.chunk.extension + "\" " + self.resolution + " " + self.nbreImage + " PostFix=" + self.nom + " Circ=1" + "\n")
        else :
            os.system("mm3d Tapioca " + "Line" + " \".*" + self.chunk.extension + "\" " + self.resolution + " " + self.nbreImage + " PostFix=" + self.nom + "\n")
        self.getNbrePtsLiaisons()
        self.ongoing =False
        self.done = True
        interface.canvas.draw()

#    def afficher(self) :
#        if self == currentPointsLiaisons :
#            print("        |-> + " + str(self.nom) + " <Line> (" + str(self.getNbrePtsLiaisons()) + " points de liaisons)")
#        else :
#            print("        |-> - " + str(self.nom) + " <Line> (" + str(self.getNbrePtsLiaisons()) + " points de liaisons)")
#        if self.circulaire :
#            print("        |    Res : " + str(self.resolution) + "   Nbre d'images : " + self.nbreImage + "   Circulaire : Oui")
#        else :
#            print("        |    Res : " + str(self.resolution) + "   Nbre d'images : " + self.nbreImage + "   Circulaire : Non")
#        for caliEtMEP in self.listCaliEtMEP :
#            caliEtMEP.afficher()

    def save(self) :
        if self.circulaire :
            if self.done :
                return "PointsLiaisonsLine\t" + self.nom + "\t" + self.resolution + "\t" + self.nbreImage + "\t" + "Oui" + "\t" + self.chunk.nom + "\tdone\n";
            else :
                return "PointsLiaisonsLine\t" + self.nom + "\t" + self.resolution + "\t" + self.nbreImage + "\t" + "Oui" + "\t" + self.chunk.nom + "\tplanned\n";
        else :
            if self.done :
                return "PointsLiaisonsLine\t" + self.nom + "\t" + self.resolution + "\t" + self.nbreImage + "\t" + "Non" + "\t" + self.chunk.nom + "\tdone\n";
            else :
                return "PointsLiaisonsLine\t" + self.nom + "\t" + self.resolution + "\t" + self.nbreImage + "\t" + "Non" + "\t" + self.chunk.nom + "\tplanned\n";
            
class PointsLiaisonsMulscale(PointsLiaisons) :
    def __init__(self, nom, resolution, chunk, lowResolution) :
        PointsLiaisons.__init__(self, nom, resolution, chunk)
        self.lowResolution = lowResolution

    def run(self, interface) :
        self.ongoing = True
        interface.canvas.draw()
        os.chdir(self.chunk.dossier)
        os.system("mm3d Tapioca " + "MulScale" + " \".*" + self.chunk.extension + "\" " + self.lowResolution + " " + self.resolution + " PostFix=" + self.nom)
        self.getNbrePtsLiaisons()
        self.ongoing =False
        self.done = True
        interface.canvas.draw()

    def save(self) :
        if self.done :
            return "PointsLiaisonsMuscale\t" + self.nom + "\t" + self.resolution + "\t" + self.lowResolution + "\t" + self.chunk.nom + "\tdone\n";
        else :
            return "PointsLiaisonsMuscale\t" + self.nom + "\t" + self.resolution + "\t" + self.lowResolution + "\t" + self.chunk.nom + "\tplanned\n";
        
class PointsLiaisonsVide(PointsLiaisons) :
    def __init__(self, nom, resolution, chunk) :
        PointsLiaisons.__init__(self, nom, resolution, chunk)
        self.done = True

    def run(self, interface) :
        return
    
    def draw(self, canvas, n, nPrec, selected):
        return

    def save(self) :
        return "PointsLiaisonsVide\t" + self.nom + "\t" + self.resolution + "\t" + self.chunk.nom + "\tdone\n";
        
        
class CaliEtMEP :
    def __init__(self, nom, mode, pointsLiaisons) :
        self.nom = nom
        self.mode = mode
        self.listNuagePoints = []
        self.pointsLiaisons = pointsLiaisons
        self.nbreImgOri = "???"
        self.done = False
        self.ongoing = False

    def run(self, interface) :
        if not(self.pointsLiaisons.done) :
            self.pointsLiaisons.run(interface)
        self.ongoing = True
        interface.canvas.draw()
        os.chdir(self.pointsLiaisons.chunk.dossier)
        os.system("mm3d Tapas " + self.mode + " \".*" + self.pointsLiaisons.chunk.extension + "\" Out=" + self.nom + " SH=" + self.pointsLiaisons.nom + "\n")
        os.system("mm3d Apericloud .*" + self.pointsLiaisons.chunk.extension + " " + self.nom + " SH=" + self.pointsLiaisons.nom + " Out=Align-" + self.nom + ".ply")
        self.getNbreImageOrientee()
        self.ongoing = False
        self.done = True
        interface.canvas.draw()
        
    def delete(self, interface) :
        self.pointsLiaisons.listCaliEtMEP.remove(self)
        
    def getNbreImageOrientee(self):
        nbreOri = 0
        for fic in os.listdir(self.pointsLiaisons.chunk.dossier + "\\Ori-"+self.nom):
            if "Orientation-" in fic :
                nbreOri += 1
        self.nbreImgOri = str(nbreOri)
    
    def selected(self, interface, position):
        interface.currentCaliEtMEP = self
        if position == 0 :
            interface.currentNuagePoints = 0
            interface.currentOrtho = 0
            interface.selectedObject = self
        self.pointsLiaisons.selected(interface, position + 1)
    
    def draw(self, canvas, n, nPrec, selected):
        x1 = 10 + 5 * canvas.padx + 2 * canvas.sizex
        y1 = 10 + (2*n + 1) * canvas.pady + n * canvas.sizey
        x2 = 10 + 5 * canvas.padx + 3 * canvas.sizex
        y2 = 10 + (2*n + 1) * canvas.pady + (n+1) * canvas.sizey
        dn = n - nPrec
        x3, y3 = 10 + 3 * canvas.padx + 3 * canvas.sizex//2, 10 + (2*nPrec + 1) * canvas.pady + (nPrec+1) * canvas.sizey
        x4, y4 = x3, y3 + 2 * dn * canvas.pady + (dn-1) * canvas.sizey + canvas.sizey//2 
        x5, y5 = x4 + canvas.sizex//2 + 2 * canvas.padx, y4
        if selected :
            canvas.create_rectangle(x1, y1, x2, y2, outline="cyan", width=8, fill="cyan", tags=str(n))
            canvas.create_line(x3, y3 + 3, x4, y4 + 3, width=5, fill="cyan")
            canvas.create_line(x4 - 2, y4, x5 - 2, y5, width=5, fill="cyan")
        else :
            canvas.create_line(x3, y3, x4, y4 + 1, width=3)
            canvas.create_line(x4 - 1, y4, x5 - 1, y5, width=3)
        canvas.create_rectangle(x1, y1, x2, y2, outline="darkgreen", width=2, fill="darkgreen", activefill="green", tags=str(n))
        canvas.create_text((x1+x2)/2, y1 + canvas.sizey/4, text=self.nom, fill="white", tags=str(n))
        canvas.create_text((x1+x2)/2, y1 + 3*canvas.sizey/4, text=self.nbreImgOri + "/" + str(self.pointsLiaisons.chunk.getNbrePhotos()) + " aligned photos", fill="white", tags=str(n))
        if self.done :
            canvas.create_image(x2, y1, image=canvas.imgDone)
        elif self.ongoing :
            canvas.create_image(x2, y1, image=canvas.imgOngoing)
        else :
            canvas.create_image(x2, y1, image=canvas.imgPlanned)

    def save(self) :
        if self.done :
            return "CaliEtMEP\t" + self.nom + "\t" + self.mode + "\t" + self.pointsLiaisons.nom + "\tdone\n";
        else :
            return "CaliEtMEP\t" + self.nom + "\t" + self.mode + "\t" + self.pointsLiaisons.nom + "\tplanned\n";
        
class CaliEtMEPMerge(CaliEtMEP) :
    def __init__(self, nom, mode, listCali, listOri, pointsLiaisons) :
        CaliEtMEP.__init__(self, nom, mode, pointsLiaisons)
        self.listCali = listCali
        self.listOri = listOri

    def run(self, interface) :
        for cali in self.listCali :
            if not(cali.done) :
                cali.run(interface)
        if not(self.pointsLiaisons.done) :
            self.pointsLiaisons.run(interface)
        self.ongoing = True
        interface.canvas.draw()
        os.chdir(self.pointsLiaisons.chunk.dossier)
        n = 0
        for fic in os.listdir(self.pointsLiaisons.chunk.dossier) :
            if "Ori-AutoMerge" in fic :
                n += 1
        os.system("md Ori-AutoMerge" + str(n))
        i = 0
        for cali in self.listCali :
            if self.listOri[i] :
                os.system("copy /y \"" + cali.pointsLiaisons.chunk.dossier + "\\Ori-" + cali.nom + "\\*\" \"" + self.pointsLiaisons.chunk.dossier + "\\Ori-AutoMerge" + str(n) + "\"")
            else :
                os.system("copy /y \"" + cali.pointsLiaisons.chunk.dossier + "\\Ori-" + cali.nom + "\\AutoCal_Foc*\" \"" + self.pointsLiaisons.chunk.dossier + "\\Ori-AutoMerge" + str(n) + "\"")
            i += 1
        if True in self.listOri:
            os.system("mm3d Tapas " + self.mode + " \".*" + self.pointsLiaisons.chunk.extension + "\" Out=" + self.nom + " SH=" + self.pointsLiaisons.nom + " InCal=Automerge" + str(n) + " InOri=Automerge" + str(n) + "\n")   
        else :
            os.system("mm3d Tapas " + self.mode + " \".*" + self.pointsLiaisons.chunk.extension + "\" Out=" + self.nom + " SH=" + self.pointsLiaisons.nom + " InCal=Automerge" + str(n) + "\n")
        os.system("mm3d Apericloud .*" + self.pointsLiaisons.chunk.extension + " " + self.nom + " SH=" + self.pointsLiaisons.nom + " Out=Align-" + self.nom + ".ply")
        self.getNbreImageOrientee()
        self.ongoing = False
        self.done = True
        interface.canvas.draw()
    
    def draw(self, canvas, n, nPrec, selected):
        x1 = 10 + 5 * canvas.padx + 2 * canvas.sizex
        y1 = 10 + (2*n + 1) * canvas.pady + n * canvas.sizey
        x2 = 10 + 5 * canvas.padx + 3 * canvas.sizex
        y2 = 10 + (2*n + 1) * canvas.pady + (n+1) * canvas.sizey
        dn = n - nPrec
        x3, y3 = 10 + 3 * canvas.padx + 3 * canvas.sizex//2, 10 + (2*nPrec + 1) * canvas.pady + (nPrec+1) * canvas.sizey
        x4, y4 = x3, y3 + 2 * dn * canvas.pady + (dn-1) * canvas.sizey + canvas.sizey//2 
        x5, y5 = x4 + canvas.sizex//2 + 2 * canvas.padx, y4
        if selected :
            canvas.create_rectangle(x1, y1, x2, y2, outline="cyan", width=8, fill="cyan", tags=str(n))
            canvas.create_line(x3, y3 + 3, x4, y4 + 3, width=5, fill="cyan")
            canvas.create_line(x4 - 2, y4, x5 - 2, y5, width=5, fill="cyan")
        else :
            canvas.create_line(x3, y3, x4, y4 + 1, width=3)
            canvas.create_line(x4 - 1, y4, x5 - 1, y5, width=3)
        canvas.create_rectangle(x1, y1, x2, y2, outline="darkgreen", width=2, fill="darkgreen", activefill="green", tags=str(n))
        canvas.create_text((x1+x2)/2, y1 + canvas.sizey/4, text=self.nom, fill="white", tags=str(n))
        canvas.create_text((x1+x2)/2, y1 + 3*canvas.sizey/4, text=self.nbreImgOri + "/" + str(self.pointsLiaisons.chunk.getNbrePhotos()) + " aligned photos", fill="white", tags=str(n))
        if self.done :
            canvas.create_image(x2, y1, image=canvas.imgDone)
        elif self.ongoing :
            canvas.create_image(x2, y1, image=canvas.imgOngoing)
        else :
            canvas.create_image(x2, y1, image=canvas.imgPlanned)

    def save(self) :
        saveText = "CaliEtMEPMerge\t" + self.nom + "\t" + self.mode + "\t" + self.pointsLiaisons.nom + "\t" + str(len(self.listCali))
        for cali in self.listCali :
            saveText += "\t" + cali.nom
        for ori in self.listOri :
            saveText += "\t" + str(ori)
        if self.done :
            return saveText + "\tdone\n"
        else :
            return saveText + "\tplanned\n"

class CaliEtMEPMergePC(CaliEtMEP) :
    def __init__(self, nom, mode, pointsLiaisons) :
        CaliEtMEP.__init__(self, nom, mode, pointsLiaisons)

    def run(self, interface) :
        if not(self.listNuagePoints[0].done) :
            self.listNuagePoints[0].run(interface)
        self.getNbreImageOrientee()
        self.ongoing = False
        self.done = True
        interface.canvas.draw()
    
    def draw(self, canvas, n, nPrec, selected):
        x1 = 10 + 5 * canvas.padx + 2 * canvas.sizex
        y1 = 10 + (2*n + 1) * canvas.pady + n * canvas.sizey
        x2 = 10 + 5 * canvas.padx + 3 * canvas.sizex
        y2 = 10 + (2*n + 1) * canvas.pady + (n+1) * canvas.sizey
        dn = n - nPrec
        x3, y3 = 10 + canvas.padx + canvas.sizex//2, 10 + (2*nPrec + 1) * canvas.pady + (nPrec+1) * canvas.sizey
        x4, y4 = x3, y3 + 2 * dn * canvas.pady + (dn-1) * canvas.sizey + canvas.sizey//2 
        x5, y5 = x4 + 2 * canvas.padx + 3 * canvas.sizex//2 + 2 * canvas.padx, y4
        if selected :
            canvas.create_rectangle(x1, y1, x2, y2, outline="cyan", width=8, fill="cyan", tags=str(n))
            canvas.create_line(x3, y3 + 3, x4, y4 + 3, width=5, fill="cyan")
            canvas.create_line(x4 - 2, y4, x5 - 2, y5, width=5, fill="cyan")
        else :
            canvas.create_line(x3, y3, x4, y4 + 1, width=3)
            canvas.create_line(x4 - 1, y4, x5 - 1, y5, width=3)
        canvas.create_rectangle(x1, y1, x2, y2, outline="darkgreen", width=2, fill="darkgreen", activefill="green", tags=str(n))
        canvas.create_text((x1+x2)/2, y1 + canvas.sizey/4, text=self.nom, fill="white", tags=str(n))
        canvas.create_text((x1+x2)/2, y1 + 3*canvas.sizey/4, text=self.nbreImgOri + "/" + str(self.pointsLiaisons.chunk.getNbrePhotos()) + " aligned photos", fill="white", tags=str(n))
        if self.done :
            canvas.create_image(x2, y1, image=canvas.imgDone)
        elif self.ongoing :
            canvas.create_image(x2, y1, image=canvas.imgOngoing)
        else :
            canvas.create_image(x2, y1, image=canvas.imgPlanned)

    def save(self) :
        saveText = "CaliEtMEPMergePC\t" + self.nom + "\t" + self.mode + "\t" + self.pointsLiaisons.nom
        if self.done :
            return saveText + "\tdone\n";
        else :
            return saveText + "\tplanned\n";


class CaliEtMEPFigee(CaliEtMEP) :
    def __init__(self, nom, mode, calibration, pointsLiaisons) :
        CaliEtMEP.__init__(self, nom, mode, pointsLiaisons)
        self.calibration = calibration
        
    def run(self, interface) :
        if not(self.pointsLiaisons.done) :
            self.pointsLiaisons.run(interface)
        self.ongoing = True
        interface.canvas.draw()
        os.chdir(self.pointsLiaisons.chunk.dossier)       
        os.system("mm3d Tapas " + self.mode + " \".*" + self.pointsLiaisons.chunk.extension + "\" Out=" + self.nom +  " InCal=" + self.calibration + " SH=" + self.pointsLiaisons.nom + "\n")
        os.system("mm3d Apericloud .*" + self.pointsLiaisons.chunk.extension + " " + self.nom + " SH=" + self.pointsLiaisons.nom + " Out=Align-" + self.nom + ".ply")
        self.getNbreImageOrientee()
        self.ongoing = False
        self.done = True
        interface.canvas.draw()

    def save(self) :
        if self.done :
            return "CaliEtMEPFigee\t" + self.nom + "\t" + self.mode + "\t" + self.calibration + self.pointsLiaisons.nom + "\tdone\n";
        else :
            return "CaliEtMEPFigee\t" + self.nom + "\t" + self.mode + "\t" + self.calibration + self.pointsLiaisons.nom + "\tplanned\n";

class CaliEtMEPBasculeGPS(CaliEtMEP) :
    def __init__(self, nom, mode, proj4, pointsLiaisons, MEPRelatif) :
        CaliEtMEP.__init__(self, nom, mode, pointsLiaisons)
        self.proj4 = proj4
        self.MEPRelatif = MEPRelatif
        
    def run(self, interface) :
        if not(self.MEPRelatif.done) :
            self.MEPRelatif.run(interface)
        self.ongoing = True
        interface.canvas.draw()
        path = os.path.dirname(os.path.abspath(inspect.getfile(lambda:None)))
        os.system("copy /y \"" + path + "\\ressources\\proj.xml\" \"" + self.pointsLiaisons.chunk.dossier.replace("/","\\") + "\"")
        os.chdir(self.pointsLiaisons.chunk.dossier)
        ficProj = open("proj.xml", "r")
        newFic = []
        for line in ficProj.readlines() :
             newFic.append(line.replace("A REMPLACER", self.proj4))
        ficProj.close()
        ficProj = open("proj.xml", "w")
        for line in newFic :
             ficProj.write(line)
        ficProj.close()        
        os.system("mm3d XifGps2Txt " + " \".*" + self.pointsLiaisons.chunk.extension + "\"")
        os.system("mm3d OriConvert \"#F=N_X_Y_Z\" GpsCoordinatesFromExif.txt GPS ChSys=DegreeWGS84@proj.xml")
        os.system("mm3d CenterBascule " + " \".*" + self.pointsLiaisons.chunk.extension + "\" " + self.MEPRelatif.nom + " GPS " + self.nom)
        os.system("mm3d Apericloud .*" + self.pointsLiaisons.chunk.extension + " " + self.nom + " SH=" + self.pointsLiaisons.nom + " Out=Align-" + self.nom + ".ply")
        self.getNbreImageOrientee()
        self.ongoing = False
        self.done = True
        interface.canvas.draw()

    def save(self) :
        if self.done :
            return "CaliEtMEPBasculeGPS\t" + self.nom + "\t" + self.mode + "\t" + self.proj4 + "\t" + self.MEPRelatif.nom + "\t" + self.pointsLiaisons.nom + "\tdone\n";
        else :
            return "CaliEtMEPBasculeGPS\t" + self.nom + "\t" + self.mode + "\t" + self.proj4 + "\t" + self.MEPRelatif.nom + "\t" + self.pointsLiaisons.nom + "\tplanned\n";

class CaliEtMEPBasculeGCP(CaliEtMEP) :
    def __init__(self, nom, mode, pointsLiaisons, ficGCP, ficMarker, MEPRelatif) :
        CaliEtMEP.__init__(self, nom, mode, pointsLiaisons)
        self.ficGCP = ficGCP.replace("/","\\")
        self.ficMarker = ficMarker
        self.MEPRelatif = MEPRelatif
        
    def run(self, interface) :
        if not(self.MEPRelatif.done) :
            self.MEPRelatif.run(interface)
        self.ongoing = True
        interface.canvas.draw()
        os.chdir(self.pointsLiaisons.chunk.dossier)
        os.system("mm3d GCPConvert #F=N_X_Y_Z \"" + self.ficGCP + "\"")
        os.system("copy /y \"" + self.ficGCP.replace("txt", "xml") + "\" \"" + self.pointsLiaisons.chunk.dossier.replace("/","\\") + "\"")
        self.ficGCP = os.path.basename(self.ficGCP).replace("txt", "xml")
        print(self.ficGCP)
        listFic = os.listdir(self.pointsLiaisons.chunk.dossier)
        if self.ficMarker != "0" :
#            listFicMarker = []
#            for fic in listFic :
#                if "-S2D.xml" in fic and "GCP-" in fic :
#                    listFicMarker.append(fic)
#            print(" + Nom du calcul :")
#            i = 0
#            for calcul in listFicMarker :
#                print("    - " + str(i) + " " + calcul[4:].replace("-S2D.xml", ""))
#                i += 1
#            calculChoisi = str(input(""))
#            if len(calculChoisi) < 3 :
#                calculChoisi = listFicMarker[int(calculChoisi)][4:].replace("-S2D.xml", "")
            os.system("mm3d GCPBascule " +  " \".*" + self.pointsLiaisons.chunk.extension + "\" " + self.MEPRelatif.nom + " " + self.nom + " \"" + self.ficGCP + "\" \"" + self.ficMarker + "\"")         
        else :
            for fic in listFic :
                if "." + self.pointsLiaisons.chunk.extension in fic :
                    os.system("mm3d SaisieAppuisInitQT " + fic + " " + self.MEPRelatif.nom + " \"" + self.ficGCP + "\" GCP-" + self.nom + ".xml")
            os.system("mm3d GCPBascule " +  " \".*" + self.pointsLiaisons.chunk.extension + "\" " + self.MEPRelatif.nom + " " + self.nom + " \"" + self.ficGCP + "\" GCP-" + self.nom + "-S2D.xml")
            self.ficMarker = "GCP-" + self.nom + "-S2D.xml"
        os.system("mm3d Apericloud .*" + self.pointsLiaisons.chunk.extension + " " + self.nom + " SH=" + self.pointsLiaisons.nom + " Out=Align-" + self.nom + ".ply")
        self.getNbreImageOrientee()
        self.ongoing = False
        self.done = True
        interface.canvas.draw()

    def save(self) :
        if self.done :
            return "CaliEtMEPBasculeGCP\t" + self.nom + "\t" + self.mode + "\t" + self.ficGCP + "\t" + self.ficMarker + "\t" + self.MEPRelatif.nom + "\t" + self.pointsLiaisons.nom + "\tdone\n";
        else :
            return "CaliEtMEPBasculeGCP\t" + self.nom + "\t" + self.mode + "\t" + self.ficGCP + "\t" + self.ficMarker + "\t" + self.MEPRelatif.nom + "\t" + self.pointsLiaisons.nom + "\tplanned\n";



class NuagePoints() :
    def __init__(self, nom, rendu, offset, caliEtMEP) :
        self.nom = nom
        self.rendu = rendu
        self.offset = offset
        self.listOrthos = []
        self.caliEtMEP = caliEtMEP
        self.nbrePoints = "???"
        self.done = False
        self.ongoing = False
    
    def getNbrePoints(self) :
        plydata = PlyData.read(self.caliEtMEP.pointsLiaisons.chunk.dossier + "/" + self.nom + ".ply")
        self.nbrePoints = str(plydata.elements[0].count)

    def run(self, interface) :
        if not(self.caliEtMEP.done) :
            self.caliEtMEP.run(interface)
        self.ongoing = True
        interface.canvas.draw()
        os.chdir(self.caliEtMEP.pointsLiaisons.chunk.dossier)
        os.system("ren Homol" + self.caliEtMEP.pointsLiaisons.nom + " Homol")
        if self.rendu == "Medium" :
            os.system("mm3d C3DC QuickMac \".*" + self.caliEtMEP.pointsLiaisons.chunk.extension + "\" " + self.caliEtMEP.nom + " OffsetPly=" + self.offset + " Out=" + self.nom + ".ply\n")
            os.system("ren PIMs-QuickMac PIMs-QuickMac-" + self.nom)
        elif self.rendu == "Good" :
            os.system("mm3d C3DC MicMac \".*" + self.caliEtMEP.pointsLiaisons.chunk.extension + "\" " + self.caliEtMEP.nom + " OffsetPly=" + self.offset + " Out=" + self.nom + ".ply\n")
            os.system("ren PIMs-MicMac PIMs-MicMac-" + self.nom)
        elif self.rendu == "Excellent" :
            os.system("mm3d C3DC BigMac \".*" + self.caliEtMEP.pointsLiaisons.chunk.extension + "\" " + self.caliEtMEP.nom + " OffsetPly=" + self.offset + " Out=" + self.nom + ".ply\n")
            os.system("ren PIMs-BigMac PIMs-BigMac-" + self.nom)
        elif self.rendu == "Highest" :
            os.system("mm3d C3DC Statue \".*" + self.caliEtMEP.pointsLiaisons.chunk.extension + "\" " + self.caliEtMEP.nom + " OffsetPly=" + self.offset + " Out=" + self.nom + ".ply\n")
            os.system("ren PIMs-Statue PIMs-Statue-" + self.nom)
        os.system("ren Homol Homol" + self.caliEtMEP.pointsLiaisons.nom)
        self.getNbrePoints()
        self.ongoing = False
        self.done = True
        interface.canvas.draw()
        
    def delete(self, interface) :
        self.caliEtMEP.listNuagePoints.remove(self)


    def selected(self, interface, position):
        interface.currentNuagePoints = self
        if position == 0 :
            interface.currentOrtho = 0
            interface.selectedObject = self
        self.caliEtMEP.selected(interface, position + 1)
    
    def draw(self, canvas, n, nPrec, selected):
        x1 = 10 + 7 * canvas.padx + 3 * canvas.sizex
        y1 = 10 + (2*n + 1) * canvas.pady + n * canvas.sizey
        x2 = 10 + 7 * canvas.padx + 4 * canvas.sizex
        y2 = 10 + (2*n + 1) * canvas.pady + (n+1) * canvas.sizey
        dn = n - nPrec
        x3, y3 = 10 + 5 * canvas.padx + 5 * canvas.sizex//2, 10 + (2*nPrec + 1) * canvas.pady + (nPrec+1) * canvas.sizey
        x4, y4 = x3, y3 + 2 * dn * canvas.pady + (dn-1) * canvas.sizey + canvas.sizey//2 
        x5, y5 = x4 + canvas.sizex//2 + 2 * canvas.padx, y4
        if selected :
            canvas.create_rectangle(x1, y1, x2, y2, outline="cyan", width=8, fill="cyan", tags=str(n))
            canvas.create_line(x3, y3 + 3, x4, y4 + 3, width=5, fill="cyan")
            canvas.create_line(x4 - 2, y4, x5 - 2, y5, width=5, fill="cyan")
        else :
            canvas.create_line(x3, y3, x4, y4 + 1, width=3)
            canvas.create_line(x4 - 1, y4, x5 - 1, y5, width=3)
        canvas.create_rectangle(x1, y1, x2, y2, outline="darkviolet", width=2, fill="darkviolet", activefill="violet", tags=str(n))
        canvas.create_text((x1+x2)/2, y1 + canvas.sizey/4, text=self.nom, fill="white", tags=str(n))
        canvas.create_text((x1+x2)/2, y1 + 3*canvas.sizey/4, text=str(self.nbrePoints) + " points", fill="white", tags=str(n))
        if self.done :
            canvas.create_image(x2, y1, image=canvas.imgDone)
        elif self.ongoing :
            canvas.create_image(x2, y1, image=canvas.imgOngoing)
        else :
            canvas.create_image(x2, y1, image=canvas.imgPlanned)

    def save(self) :
        if self.done :
            return "NuagePoints\t" + self.nom + "\t" + self.rendu + "\t" + self.offset + "\t" + self.caliEtMEP.nom + "\tdone\n";
        else :
            return "NuagePoints\t" + self.nom + "\t" + self.rendu + "\t" + self.offset + "\t" + self.caliEtMEP.nom + "\tplanned\n";

class NuagePointsMerge(NuagePoints) :
    def __init__(self, nom, rendu, offset, targetPC, sourcePC, matrix, maxIteration, sampling, caliEtMEP) :
        NuagePoints.__init__(self, nom, rendu, offset, caliEtMEP)
        self.targetPC = targetPC
        self.sourcePC = sourcePC
        self.matrix = matrix
        self.maxIteration = maxIteration
        self.sampling = sampling

    def run(self, interface) :
        if not(self.targetPC.done) :
            self.targetPC.run(interface)
        if not(self.sourcePC.done) :
            self.sourcePC.run(interface)
        self.ongoing = True
        interface.canvas.draw()
        os.chdir(self.caliEtMEP.pointsLiaisons.chunk.dossier)
        os.system("mkdir Ori-" + self.caliEtMEP.nom)
        
        #Copy of tie points
        print("---- Copy of tie points ----\n")
        os.system("mkdir Homol" + self.caliEtMEP.pointsLiaisons.nom)
        os.system("mkdir Pastis")
        
        os.system("xcopy /y \"" + self.sourcePC.caliEtMEP.pointsLiaisons.chunk.dossier + "/Homol" + self.sourcePC.caliEtMEP.pointsLiaisons.nom + "\*\" \"" + self.caliEtMEP.pointsLiaisons.chunk.dossier + "/Homol" + self.caliEtMEP.pointsLiaisons.nom + "\" /s")
        os.system("xcopy /y \"" + self.targetPC.caliEtMEP.pointsLiaisons.chunk.dossier + "/Homol" + self.targetPC.caliEtMEP.pointsLiaisons.nom + "\*\" \"" + self.caliEtMEP.pointsLiaisons.chunk.dossier + "/Homol" + self.caliEtMEP.pointsLiaisons.nom + "\" /s")
        
        os.system("xcopy /y \"" + self.sourcePC.caliEtMEP.pointsLiaisons.chunk.dossier + "/Pastis\*\" \"" + self.caliEtMEP.pointsLiaisons.chunk.dossier + "/Pastis\" /s")
        os.system("xcopy /y \"" + self.targetPC.caliEtMEP.pointsLiaisons.chunk.dossier + "/Pastis\*\" \"" + self.caliEtMEP.pointsLiaisons.chunk.dossier + "/Pastis\" /s")
        
        #ICP
        ficSource = self.sourcePC.caliEtMEP.pointsLiaisons.chunk.dossier + "/" + self.sourcePC.nom + ".ply"
        ficTarget = self.targetPC.caliEtMEP.pointsLiaisons.chunk.dossier + "/" + self.targetPC.nom + ".ply"
        if (self.maxIteration > 0) :
            icp = ICPPython.IterativeClosestPointTransform(ficSource, ficTarget, self.maxIteration, self.sampling, self.matrix)
            icp.PerformICP()
            self.matrix = icp.matrix
            print(icp.Matrix)
            
        #Merge clouds
        print("---- Merge clouds ----\n")
                
        plydataTarget = PlyData.read(ficTarget)
        plydataSource = PlyData.read(ficSource)
        
        nuageTarget = np.array((plydataTarget['vertex'].data['x'], plydataTarget['vertex'].data['y'], plydataTarget['vertex'].data['z'], plydataTarget['vertex'].data['red'], plydataTarget['vertex'].data['green'], plydataTarget['vertex'].data['blue'])).T 
        nuageSourcePoints = np.array((plydataSource['vertex'].data['x'], plydataSource['vertex'].data['y'], plydataSource['vertex'].data['z'])).T
        nuageSourceColors = np.array((plydataSource['vertex'].data['red'], plydataSource['vertex'].data['green'], plydataSource['vertex'].data['blue'])).T
        
        nuageSourcePoints = TransformPointsWithMatrix(nuageSourcePoints, self.matrix)
        
        nuageSource = np.concatenate((nuageSourcePoints, nuageSourceColors), axis=1)
        nuageMerge =  np.concatenate((nuageTarget, nuageSource), axis=0)
        
        vertexNuage = [tuple(x) for x in nuageMerge.tolist()]
        vertex = np.array(vertexNuage, dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('red', 'u1'), ('green', 'u1'), ('blue', 'u1')])
        el = PlyElement.describe(vertex, 'vertex')
        PlyData([el]).write(self.caliEtMEP.pointsLiaisons.chunk.dossier + "/" + self.nom + ".ply")
        
        #Transform orientation
        print("---- Transform orientation ----\n")
        self.transformOri(self.targetPC, self.sourcePC, self.matrix)
        self.getNbrePoints()
        self.ongoing = False
        self.done = True
        os.system("mm3d Apericloud .*" + self.caliEtMEP.pointsLiaisons.chunk.extension + " " + self.caliEtMEP.nom + " SH=" + self.caliEtMEP.pointsLiaisons.nom + " Out=Align-" + self.caliEtMEP.nom + ".ply")
        self.caliEtMEP.done = True
        self.caliEtMEP.getNbreImageOrientee()
        
        interface.canvas.draw()
    
    def transformOri(self, master, nuage, matrix) :
        os.system("copy /y \"" + nuage.caliEtMEP.pointsLiaisons.chunk.dossier + "\\Ori-" + nuage.caliEtMEP.nom + "\\*\" \"" + self.caliEtMEP.pointsLiaisons.chunk.dossier + "\\Ori-" + self.caliEtMEP.nom + "\"")
        os.system("copy /y \"" + master.caliEtMEP.pointsLiaisons.chunk.dossier + "\\Ori-" + master.caliEtMEP.nom + "\\*\" \"" + self.caliEtMEP.pointsLiaisons.chunk.dossier + "\\Ori-" + self.caliEtMEP.nom + "\"")
        offsetMaster = np.array([[float(master.offset.split(",")[0][1:]), float(master.offset.split(",")[1]), float(master.offset.split(",")[2][:-1]), 0]])
        offsetNuage  = np.array([[float(nuage.offset.split(",")[0][1:]), float(nuage.offset.split(",")[1]), float(nuage.offset.split(",")[2][:-1]), 0]])
        for file in os.listdir(nuage.caliEtMEP.pointsLiaisons.chunk.dossier) :
            if ("." + nuage.caliEtMEP.pointsLiaisons.chunk.extension) in file :
                newFile = []
                fileOriName = self.caliEtMEP.pointsLiaisons.chunk.dossier + "/Ori-" + self.caliEtMEP.nom + "/Orientation-" + file + ".xml"
                print(" + " + fileOriName)
                fileOri = open(fileOriName, "r")
                for line in fileOri.readlines() :
                    if "<Centre>" in line :
                        debut = line.index("<Centre>") + 8
                        fin   = line.index("</Centre>")
                        coordinates = line[debut:fin].split(" ")
                        vector = np.array([[float(coordinates[0]), float(coordinates[1]), float(coordinates[2]), 1]]) - offsetNuage
                        newVector = np.dot(matrix, vector.T).T + offsetMaster 
                        newVector = newVector[0,:3]
                        newLine = line[:debut] + str(newVector[0]) + " " + str(newVector[1]) + " " + str(newVector[2]) + line[fin:]
                        newFile.append(newLine)
                    elif "<L1>" in line :
                        debut = line.index("<L1>") + 4
                        fin   = line.index("</L1>")
                        coordinates = line[debut:fin].split(" ")
                        L1 = np.array([float(coordinates[0]), float(coordinates[1]), float(coordinates[2])])
                    elif "<L2>" in line :
                        debut = line.index("<L2>") + 4
                        fin   = line.index("</L2>")
                        coordinates = line[debut:fin].split(" ")
                        L2 = np.array([float(coordinates[0]), float(coordinates[1]), float(coordinates[2])])
                    elif "<L3>" in line :
                        debut = line.index("<L3>") + 4
                        fin   = line.index("</L3>")
                        coordinates = line[debut:fin].split(" ")
                        L3 = np.array([float(coordinates[0]), float(coordinates[1]), float(coordinates[2])])
                        matrixRot = np.array([L1, L2, L3])
                        matrixRot = np.dot(matrix[:3,:3], matrixRot)
                        newLine1 = line[:debut-4] + "<L1>" + str(matrixRot[0][0]) + " " + str(matrixRot[0][1]) + " " + str(matrixRot[0][2]) + "</L1>\n"
                        newLine2 = line[:debut-4] + "<L2>" + str(matrixRot[1][0]) + " " + str(matrixRot[1][1]) + " " + str(matrixRot[1][2]) + "</L2>\n"
                        newLine3 = line[:debut-4] + "<L3>" + str(matrixRot[2][0]) + " " + str(matrixRot[2][1]) + " " + str(matrixRot[2][2]) + "</L3>\n"
                        newFile.append(newLine1)
                        newFile.append(newLine2)
                        newFile.append(newLine3)
                    else :
                        newFile.append(line)
                fileOri.close()
                fileOri = open(fileOriName, "w")
                for line in newFile :
                    fileOri.write(line)
                fileOri.close()

            
        

    def save(self) :
        saveText = "NuagePointsMerge\t" + self.nom + "\t" + self.rendu + "\t" + self.offset + "\t" + self.targetPC.nom + "\t" + self.sourcePC.nom
        for i in range (4) :
            for j in range (4) :
                saveText += "\t" + str(self.matrix[i][j])
        if self.done :
            return saveText + "\t" + str(self.maxIteration) + "\t" + str(self.sampling) + "\t" + self.caliEtMEP.nom  + "\tdone\n";
        else :
            return saveText + "\t" + str(self.maxIteration) + "\t" + str(self.sampling) + "\t" + self.caliEtMEP.nom + "\tplanned\n";
        
        
class Ortho() :
    def __init__(self, nom, mode, egalisation, nuagePoints) :
        self.nom = nom
        self.mode = mode
        self.egalisation = egalisation
        self.nuagePoints = nuagePoints
        self.done = False
        self.ongoing = False

    def run(self, interface) :
        
        if not(self.nuagePoints.done) :
            self.nuagePoints.run(interface)
            
        self.ongoing = True
        interface.canvas.draw()
        os.chdir(self.nuagePoints.caliEtMEP.pointsLiaisons.chunk.dossier)
        
        if self.nuagePoints.rendu == "Medium" :
            os.system("ren PIMs-QuickMac-" + self.nuagePoints.nom + " PIMs-MicMac")
        elif self.nuagePoints.rendu == "Good" :
            os.system("ren PIMs-MicMac-" + self.nuagePoints.nom + " PIMs-MicMac")
        elif self.nuagePoints.rendu == "Excellent" :
            os.system("ren PIMs-BigMac-" + self.nuagePoints.nom + " PIMs-MicMac")
        elif self.nuagePoints.rendu == "Highest" :
            os.system("ren PIMs-Statue-" + self.nuagePoints.nom + " PIMs-MicMac")
            
        if self.mode == "Parallel to the ground" :
            os.system("mm3d Pims2MNT MicMac DoOrtho=1\n")
            if self.egalisation :
                os.system("mm3d Tawny PIMs-ORTHO/ DEq=1")
            else :
                os.system("mm3d Tawny PIMs-ORTHO/ DEq=0")
            ## Directories name modification
            os.system("ren PIMs-ORTHO PIMs-ORTHO-" + self.nom)
            os.system("ren PIMs-TmpBasc PIMs-TmpBasc-" + self.nom)
            os.system("ren PIMs-TmpMnt PIMs-TmpMnt-" + self.nom)
            os.system("ren PIMs-TmpMntOrtho PIMs-TmpMntOrtho-" + self.nom)
            os.system("ren Pyram Pyram-" + self.nom)
        
        if self.nuagePoints.rendu == "Medium" :
            os.system("ren PIMs-MicMac PIMs-QuickMac-" + self.nuagePoints.nom)
        elif self.nuagePoints.rendu == "Good" :
            os.system("ren PIMs-MicMac PIMs-MicMac-" + self.nuagePoints.nom)
        elif self.nuagePoints.rendu == "Excellent" :
            os.system("ren PIMs-MicMac PIMs-BigMac-" + self.nuagePoints.nom)
        elif self.nuagePoints.rendu == "Highest" :
            os.system("ren PIMs-MicMac PIMs-Statue-" + self.nuagePoints.nom)
        
        self.ongoing = False
        self.done = True
        interface.canvas.draw()
    
    def delete(self, interface) :
        self.nuagePoints.listOrthos.remove(self)
    
    def selected(self, interface, position):
        interface.currentOrtho = self
        if position == 0 :
            interface.selectedObject = self
        self.nuagePoints.selected(interface, position + 1)
        
    def draw(self, canvas, n, nPrec, selected):
        x1 = 10 + 9 * canvas.padx + 4 * canvas.sizex
        y1 = 10 + (2*n + 1) * canvas.pady + n * canvas.sizey
        x2 = 10 + 9 * canvas.padx + 5 * canvas.sizex
        y2 = 10 + (2*n + 1) * canvas.pady + (n+1) * canvas.sizey
        dn = n - nPrec
        x3, y3 = 10 + 7 * canvas.padx + 7 * canvas.sizex//2, 10 + (2*nPrec + 1) * canvas.pady + (nPrec+1) * canvas.sizey
        x4, y4 = x3, y3 + 2 * dn * canvas.pady + (dn-1) * canvas.sizey + canvas.sizey//2 
        x5, y5 = x4 + canvas.sizex//2 + 2 * canvas.padx, y4
        if selected :
            canvas.create_rectangle(x1, y1, x2, y2, outline="cyan", width=8, fill="cyan", tags=str(n))
            canvas.create_line(x3, y3 + 3, x4, y4 + 3, width=5, fill="cyan")
            canvas.create_line(x4 - 2, y4, x5 - 2, y5, width=5, fill="cyan")
        else :
            canvas.create_line(x3, y3, x4, y4 + 1, width=3)
            canvas.create_line(x4 - 1, y4, x5 - 1, y5, width=3)
        canvas.create_rectangle(x1, y1, x2, y2, outline="DarkGoldenrod3", width=2, fill="DarkGoldenrod3", activefill="DarkGoldenrod2", tags=str(n))
        canvas.create_text((x1+x2)/2, y1 + canvas.sizey/4, text=self.nom, fill="white", tags=str(n))
        #canvas.create_text((x1+x2)/2, y1 + 3*canvas.sizey/4, text=str(self.nbrePoints) + " points", fill="white", tags=str(n))
        if self.done :
            canvas.create_image(x2, y1, image=canvas.imgDone)
        elif self.ongoing :
            canvas.create_image(x2, y1, image=canvas.imgOngoing)
        else :
            canvas.create_image(x2, y1, image=canvas.imgPlanned)
            
        
#
#    def afficher(self) :
#        print("                                                          |-> + " + self.nom + " <" + self.mode + ">")
#        if self.egalisation :
#            print("                                                          |  Egalisation radiometrique : Oui")
#        else :
#            print("                                                          |  Egalisation radiometrique : Non")

    def save(self) :
        if self.egalisation :
            if self.done :
                return "Ortho\t" + self.nom + "\t" + self.mode + "\t" + "Oui" + "\t" + self.nuagePoints.nom + "\tdone\n";
            else :
                return "Ortho\t" + self.nom + "\t" + self.mode + "\t" + "Oui" + "\t" + self.nuagePoints.nom + "\tplanned\n";
        else :
            if self.done :
                return "Ortho\t" + self.nom + "\t" + self.mode + "\t" + "Non" + "\t" + self.nuagePoints.nom + "\tdone\n";
            else :
                return "Ortho\t" + self.nom + "\t" + self.mode + "\t" + "Non" + "\t" + self.nuagePoints.nom + "\tplanned\n";
            
            
class Mesh() :
    def __init__(self, nom, depth, textured, nuagePoints) :
        self.nom = nom
        self.depth = depth
        self.textured = textured
        self.nuagePoints = nuagePoints
        self.nbreFaces = "???"
        self.done = False
        self.ongoing = False

    def run(self, interface) :
        
        if not(self.nuagePoints.done) :
            self.nuagePoints.run(interface)
            
        self.ongoing = True
        interface.canvas.draw()
        os.chdir(self.nuagePoints.caliEtMEP.pointsLiaisons.chunk.dossier)
        
        if self.nuagePoints.rendu == "Medium" :
            os.system("ren PIMs-QuickMac-" + self.nuagePoints.nom + " PIMs-Statue")
        elif self.nuagePoints.rendu == "Good" :
            os.system("ren PIMs-MicMac-" + self.nuagePoints.nom + " PIMs-Statue")
        elif self.nuagePoints.rendu == "Excellent" :
            os.system("ren PIMs-BigMac-" + self.nuagePoints.nom + " PIMs-Statue")
        elif self.nuagePoints.rendu == "Highest" :
            os.system("ren PIMs-Statue-" + self.nuagePoints.nom + " PIMs-Statue")
            
        os.system("mm3d TiPunch " + self.nuagePoints.nom + ".ply Filter=true Out=" + self.nom + ".ply Pattern=.*" + self.nuagePoints.caliEtMEP.pointsLiaisons.chunk.extension + " Depth=" + str(self.depth))
        if self.textured :
            os.system("mm3d Tequila .*" + self.nuagePoints.caliEtMEP.pointsLiaisons.chunk.extension + " " + self.nuagePoints.caliEtMEP.nom + " " + self.nom + ".ply " + " Mode=Basic Out=" + self.nom + "-textured.ply")
        
        if self.nuagePoints.rendu == "Medium" :
            os.system("ren PIMs-Statue PIMs-QuickMac-" + self.nuagePoints.nom)
        elif self.nuagePoints.rendu == "Good" :
            os.system("ren PIMs-Statue PIMs-MicMac-" + self.nuagePoints.nom)
        elif self.nuagePoints.rendu == "Excellent" :
            os.system("ren PIMs-Statue PIMs-BigMac-" + self.nuagePoints.nom)
        elif self.nuagePoints.rendu == "Highest" :
            os.system("ren PIMs-Statue PIMs-Statue-" + self.nuagePoints.nom)
        
        self.ongoing = False
        self.done = True
        interface.canvas.draw()
        
    def getNbreFaces(self) :
        plydata = PlyData.read(self.nuagePoints.caliEtMEP.pointsLiaisons.chunk.dossier + "/" + self.nom + ".ply")
        self.nbreFaces = str(plydata.elements[1].count)
    
    def delete(self, interface) :
        self.nuagePoints.listOrthos.remove(self)
    
    def selected(self, interface, position):
        interface.currentOrtho = self
        if position == 0 :
            interface.selectedObject = self
        self.nuagePoints.selected(interface, position + 1)
        
    def draw(self, canvas, n, nPrec, selected):
        x1 = 10 + 9 * canvas.padx + 4 * canvas.sizex
        y1 = 10 + (2*n + 1) * canvas.pady + n * canvas.sizey
        x2 = 10 + 9 * canvas.padx + 5 * canvas.sizex
        y2 = 10 + (2*n + 1) * canvas.pady + (n+1) * canvas.sizey
        dn = n - nPrec
        x3, y3 = 10 + 7 * canvas.padx + 7 * canvas.sizex//2, 10 + (2*nPrec + 1) * canvas.pady + (nPrec+1) * canvas.sizey
        x4, y4 = x3, y3 + 2 * dn * canvas.pady + (dn-1) * canvas.sizey + canvas.sizey//2 
        x5, y5 = x4 + canvas.sizex//2 + 2 * canvas.padx, y4
        if selected :
            canvas.create_rectangle(x1, y1, x2, y2, outline="cyan", width=8, fill="cyan", tags=str(n))
            canvas.create_line(x3, y3 + 3, x4, y4 + 3, width=5, fill="cyan")
            canvas.create_line(x4 - 2, y4, x5 - 2, y5, width=5, fill="cyan")
        else :
            canvas.create_line(x3, y3, x4, y4 + 1, width=3)
            canvas.create_line(x4 - 1, y4, x5 - 1, y5, width=3)
        canvas.create_rectangle(x1, y1, x2, y2, outline="DarkGoldenrod3", width=2, fill="DarkGoldenrod3", activefill="DarkGoldenrod2", tags=str(n))
        canvas.create_text((x1+x2)/2, y1 + canvas.sizey/4, text=self.nom, fill="white", tags=str(n))
        canvas.create_text((x1+x2)/2, y1 + 3*canvas.sizey/4, text=str(self.nbreFaces) + " faces", fill="white", tags=str(n))
        if self.done :
            canvas.create_image(x2, y1, image=canvas.imgDone)
        elif self.ongoing :
            canvas.create_image(x2, y1, image=canvas.imgOngoing)
        else :
            canvas.create_image(x2, y1, image=canvas.imgPlanned)

    def save(self) :
        if self.done :
            return "Mesh\t" + self.nom + "\t" + str(self.depth) + "\t" + str(self.textured) + "\t" + self.nuagePoints.nom + "\tdone\n"
        else :
            return "Mesh\t" + self.nom + "\t" + str(self.depth) + "\t" + str(self.textured) + "\t" + self.nuagePoints.nom + "\tplanned\n"

def TransformPointsWithMatrix(points, matrix) :
    result = np.ones((points.shape[0],4))
    result[:,0:3] = np.copy(points)
    result = np.dot(matrix, result.T).T[:,:3]
    return result
        
        



    

    

    

