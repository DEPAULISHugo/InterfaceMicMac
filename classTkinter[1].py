from tkinter import *
from tkinter.filedialog import *

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
    
    
    
    

    
    