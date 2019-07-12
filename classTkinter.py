from tkinter import *
from tkinter.filedialog import *
import numpy as np

class SaisieString(Entry) :
    def __init__(self,conteneur,title):
        self.label = Label(conteneur,text=title,anchor=W,width=30)
        self.label.pack()
        super().__init__(conteneur, justify='right', width=30)
        self.pack()
        
    def pack(self):
        self.label.pack()
        super().pack()
    
    def pack_forget(self):
        self.label.pack_forget()
        super().pack_forget()
        
class SaisieInt(Entry):
    def __init__(self,conteneur,title,value):
        self.label = Label(conteneur,text=title,anchor=W,width=30)
        self.label.pack()
        super().__init__(conteneur, textvariable=IntVar(conteneur, value), justify='right', width=30)
        self.pack()
        
    def pack(self):
        self.label.pack()
        super().pack()
    
    def pack_forget(self) :
        self.label.pack_forget()
        super().pack_forget()
        
class SaisieCoord(Entry):
    def __init__(self,conteneur,title,value1, value2, value3):
        self.label = Label(conteneur,text=title,anchor=W,width=30)
        self.frame = Frame(conteneur)
        self.coord1 = Entry(self.frame, textvariable=IntVar(conteneur, value1), justify='right', width=9)
        self.coord2 = Entry(self.frame, textvariable=IntVar(conteneur, value2), justify='right', width=9)
        self.coord3 = Entry(self.frame, textvariable=IntVar(conteneur, value3), justify='right', width=9)
        self.pack()
        
        
    def pack(self):
        self.label.pack()
        self.frame.pack()
        self.coord1.grid(row=0, column=0)
        self.coord2.grid(row=0, column=1)
        self.coord3.grid(row=0, column=2)
    
    def pack_forget(self) :
        self.label.pack_forget()
        self.frame.pack_forget
        self.coord1.pack_forget()
        self.coord2.pack_forget()
        self.coord3.pack_forget()
        
    def get(self) :
        return "[" + self.coord1.get() + "," + self.coord2.get() + "," +self.coord3.get() + "]"
    
class SaisieMatrix(Entry):
    def __init__(self,conteneur,title):
        self.label = Label(conteneur,text=title,anchor=W,width=30)
        self.frame = Frame(conteneur)
        #Line 1
        self.L11 = Entry(self.frame, textvariable=DoubleVar(conteneur, 1), justify='right', width=6)
        self.L12 = Entry(self.frame, textvariable=DoubleVar(conteneur, 0), justify='right', width=6)
        self.L13 = Entry(self.frame, textvariable=DoubleVar(conteneur, 0), justify='right', width=6)
        self.L14 = Entry(self.frame, textvariable=DoubleVar(conteneur, 0), justify='right', width=6)
        #Line 2
        self.L21 = Entry(self.frame, textvariable=DoubleVar(conteneur, 0), justify='right', width=6)
        self.L22 = Entry(self.frame, textvariable=DoubleVar(conteneur, 1), justify='right', width=6)
        self.L23 = Entry(self.frame, textvariable=DoubleVar(conteneur, 0), justify='right', width=6)
        self.L24 = Entry(self.frame, textvariable=DoubleVar(conteneur, 0), justify='right', width=6)
        #Line 3
        self.L31 = Entry(self.frame, textvariable=DoubleVar(conteneur, 0), justify='right', width=6)
        self.L32 = Entry(self.frame, textvariable=DoubleVar(conteneur, 0), justify='right', width=6)
        self.L33 = Entry(self.frame, textvariable=DoubleVar(conteneur, 1), justify='right', width=6)
        self.L34 = Entry(self.frame, textvariable=DoubleVar(conteneur, 0), justify='right', width=6)
        #Line 4
        self.L41 = Entry(self.frame, textvariable=DoubleVar(conteneur, 0), justify='right', width=6)
        self.L42 = Entry(self.frame, textvariable=DoubleVar(conteneur, 0), justify='right', width=6)
        self.L43 = Entry(self.frame, textvariable=DoubleVar(conteneur, 0), justify='right', width=6)
        self.L44 = Entry(self.frame, textvariable=DoubleVar(conteneur, 1), justify='right', width=6)
        self.pack()
        
        
    def pack(self):
        self.label.pack()
        self.frame.pack()
        #Line 1
        self.L11.grid(row=1, column=1)
        self.L12.grid(row=1, column=2)
        self.L13.grid(row=1, column=3)
        self.L14.grid(row=1, column=4)
        #Line 2
        self.L21.grid(row=2, column=1)
        self.L22.grid(row=2, column=2)
        self.L23.grid(row=2, column=3)
        self.L24.grid(row=2, column=4)
        #Line 3
        self.L31.grid(row=3, column=1)
        self.L32.grid(row=3, column=2)
        self.L33.grid(row=3, column=3)
        self.L34.grid(row=3, column=4)
        #Line 4
        self.L41.grid(row=4, column=1)
        self.L42.grid(row=4, column=2)
        self.L43.grid(row=4, column=3)
        self.L44.grid(row=4, column=4)

    
    def activate(self):
         #Line 1
        self.L11.config(state="normal")
        self.L12.config(state="normal")
        self.L13.config(state="normal")
        self.L14.config(state="normal")
        #Line 2
        self.L21.config(state="normal")
        self.L22.config(state="normal")
        self.L23.config(state="normal")
        self.L24.config(state="normal")
        #Line 3
        self.L31.config(state="normal")
        self.L32.config(state="normal")
        self.L33.config(state="normal")
        self.L34.config(state="normal")
        #Line 4
        self.L41.config(state="normal")
        self.L42.config(state="normal")
        self.L43.config(state="normal")
        self.L44.config(state="normal")
        
    def desactivate(self):
        #Line 1
        self.L11.config(state="disabled")
        self.L12.config(state="disabled")
        self.L13.config(state="disabled")
        self.L14.config(state="disabled")
        #Line 2
        self.L21.config(state="disabled")
        self.L22.config(state="disabled")
        self.L23.config(state="disabled")
        self.L24.config(state="disabled")
        #Line 3
        self.L31.config(state="disabled")
        self.L32.config(state="disabled")
        self.L33.config(state="disabled")
        self.L34.config(state="disabled")
        #Line 4
        self.L41.config(state="disabled")
        self.L42.config(state="disabled")
        self.L43.config(state="disabled")
        self.L44.config(state="disabled")
        
    def get(self) :
        return np.array([[float(self.L11.get()), float(self.L12.get()), float(self.L13.get()), float(self.L14.get())], [float(self.L21.get()), float(self.L22.get()), float(self.L23.get()), float(self.L24.get())], [float(self.L31.get()), float(self.L32.get()), float(self.L33.get()), float(self.L34.get())], [float(self.L41.get()), float(self.L42.get()), float(self.L43.get()), float(self.L44.get())]])
        
class SaisieNomFichier(Entry):
    def __init__(self,conteneur,title):
        self.fileName = StringVar(conteneur,"")
        self.label = Label(conteneur,text=title,anchor=W,width=30)
        self.label.pack()
        self.frame = Frame(conteneur, width=40)
        self.frame.pack()
        super().__init__(self.frame, textvariable=self.fileName, justify='right', width=19)
        super().pack(side=LEFT)
        self.buttonOpen = Button(self.frame, text="Open", command=self.openGCPFile, width=6)
        self.buttonOpen.pack(side=RIGHT)
    
    def openGCPFile(self):
        self.fileName.set(askopenfilename())
    
    def pack(self):
        self.label.pack()
        self.frame.pack()
        super().pack(side=LEFT)
        self.buttonOpen.pack(side=RIGHT)
    
    def pack_forget(self):
        self.label.pack_forget()
        self.frame.pack_forget()
        super().pack_forget()
        self.buttonOpen.pack_forget()
        
class SaisieNomDossier(Entry):
    def __init__(self,conteneur,title):
        self.fileName = StringVar(conteneur,"")
        self.label = Label(conteneur,text=title,anchor=W,width=30)
        self.label.pack()
        self.frame = Frame(conteneur, width=40)
        self.frame.pack()
        super().__init__(self.frame, textvariable=self.fileName, justify='right', width=19)
        super().pack(side=LEFT)
        self.buttonOpen = Button(self.frame, text="Open", command=self.openDirectory, width=6)
        self.buttonOpen.pack(side=RIGHT)
    
    def openDirectory(self):
        self.fileName.set(askdirectory())
    
    def pack(self):
        self.label.pack()
        self.frame.pack()
        super().pack(side=LEFT)
        self.buttonOpen.pack(side=RIGHT)
    
    def pack_forget(self):
        self.label.pack_forget()
        self.frame.pack_forget()
        super().pack_forget()
        self.buttonOpen.pack_forget()
        
class SaisieChoixMultiples(Entry):
    def __init__(self, conteneur, title, listValeurs):
        self.label = Label(conteneur,text=title,anchor=W,width=30)
        self.frame = Frame(conteneur, bg="white", relief=SUNKEN, borderwidth=2, width=30)
        self.listValeurs = listValeurs
        self.listObjets = []
        self.listVar = []
        for objet in listValeurs :
            self.listVar.append(BooleanVar())
            self.listVar[-1].set(False)
            self.listObjets.append(Checkbutton(self.frame, text=objet.nom, var=self.listVar[-1], width=22,anchor=W))
        self.pack()
    
    def pack(self):
        self.label.pack()
        self.frame.pack()
        for objet in self.listObjets:
            objet.pack()
            
    def pack_forget(self):
        self.label.pack_forget()
        self.frame.pack_forget()
        self.pack_forget()
        for objet in self.listObjet:
            objet.pack_forget()
    
    def get(self):
        listSelectedValues = []
        for i in range(len(self.listValeurs)):
            if self.listVar[i].get():
                listSelectedValues.append(self.listValeurs[i])
        return listSelectedValues

class SaisieChoixMultiplesClasses(Entry):
    def __init__(self, conteneur, title, listValeurs, listClasses):
        self.label = Label(conteneur,text=title,anchor=W,width=30)
        self.frame = Frame(conteneur, bg="white", relief=SUNKEN, borderwidth=2, width=30)
        self.listValeurs = listValeurs
        self.listObjets = []
        self.listVar = []
        for i in range (len(self.listValeurs)) :
            self.listObjets.append(Label(self.frame,text=listClasses[i].nom+":",anchor=W,width=25))
            for objet in listValeurs[i] :
                self.listVar.append(BooleanVar())
                self.listVar[-1].set(False)
                self.listObjets.append(Checkbutton(self.frame, text=objet.nom, var=self.listVar[-1], width=22,anchor=W, command=conteneur.CallbackMaster))
        self.pack()
    
    def pack(self):
        self.label.pack()
        self.frame.pack()
        for objet in self.listObjets:
            objet.pack()
            
    def pack_forget(self):
        self.label.pack_forget()
        self.frame.pack_forget()
        self.pack_forget()
        for objet in self.listObjet:
            objet.pack_forget()
    
    def get(self):
        listSelectedValues = []
        n = 0
        for listValeursParClasse in self.listValeurs:
            for objet in listValeursParClasse :
                if self.listVar[n].get():
                    listSelectedValues.append(objet)
                n += 1
        return listSelectedValues
    
    

    
    