from PIL import Image, ExifTags
import numpy as np
import matplotlib.pyplot as plt

class histogramEqualizer() :
    def __init__(self, listPhotos, folderName) :
        self.listPhotos = listPhotos
        self.folderName = folderName

    def getListProb(self) :
        
        if self.listProb.shape[0] == 1 :
            
            print(" --- Calcul des probabilités --- ")
            imgpil = Image.open(self.master)
            img = np.array(imgpil)
            
            listProb = np.zeros((3, 256))
            
            for i in range(img.shape[0]) :
                for j in range(img.shape[1]) :
                    value = img[i][j]
                    listProb[0][value[0]] += 1
                    listProb[1][value[1]] += 1
                    listProb[2][value[2]] += 1
            listProb = listProb / (img.shape[0] * img.shape[1])
            self.listProb = listProb
        
        return self.listProb
    
    def getlistTransfom(self) :
        
        if self.listTrans.shape[0] == 1 :
        
            listProb = self.getListProb()
            
            print(" --- Calcul des transformations --- ")
            listTrans = np.zeros((3, 256))
            value0 = 0
            value1 = 0
            value2 = 0
            for i in range (255) :
                value0 += listProb[0][i]
                value1 += listProb[1][i]
                value2 += listProb[2][i]
                listTrans[0][i] = int(value0*255)
                listTrans[1][i] = int(value1*255)
                listTrans[2][i] = int(value2*255)
            
            self.listTrans = listTrans
        
        return self.listTrans
    
    def calcHistoCumul(self, imgName) :
        
        print("   - Computation of cumulative histogram - " + imgName)
        
        imgpil = Image.open(imgName)
        img = np.array(imgpil)
        
        histoCumul = np.zeros((3, 256))
        
        for i in range(img.shape[0]) :
            for j in range(img.shape[1]) :
                value = img[i][j]
                histoCumul[0][value[0]] += 1
                histoCumul[1][value[1]] += 1
                histoCumul[2][value[2]] += 1
                
        histoCumul = histoCumul / (img.shape[0]*img.shape[1])
        
        for i in range(1, 256) :
            histoCumul[0][i] += histoCumul[0][i-1]
            histoCumul[1][i] += histoCumul[1][i-1]
            histoCumul[2][i] += histoCumul[2][i-1]
            
        return histoCumul
    
    def calcContrastFunc(self, listHistoCumul) :
        
        listF = []
        
        for i in range(len(listHistoCumul)) :
            f = np.zeros((3, 256))
            for j in range(len(listHistoCumul)) :
                if i != j :
                    fi = np.zeros((3, 256))
                    for n in range (3) :
                        l = 0
                        for k in range (256) :
                            while listHistoCumul[i][n][k] > listHistoCumul[j][n][l] :
                                if l == 255:
                                    break
                                l += 1
                            fi[n][k] = (k + l) // 2
                    f += fi
            f = f/(len(listHistoCumul)-1)
            f = f.astype(int)
            listF.append(f)
        
        return listF
                    
    
    def equalizeMidway(self) :
        
        print(" --- Midway Equalization --- ")
        
        print(" + Computation of the cumulative histograms")
        
        listHistoCumul = []
        
        for imgName in self.listPhotos :
            listHistoCumul.append(self.calcHistoCumul(imgName))
        
        print(" + Computation of contrast functions")
        
        listF = self.calcContrastFunc(listHistoCumul)
            
        print(" + Equalization of photos")
        
        for i in range(len(self.listPhotos)) :
            self.equalizePhoto(self.listPhotos[i], listF[i])
        
        
    
    def showHistoCumul(self, imgName) :
        
        histoCumul = self.calcHistoCumul(imgName)
        plt.plot(np.arange(0, 256), histoCumul[0], color="red")
        plt.plot(np.arange(0, 256), histoCumul[1], color="green")
        plt.plot(np.arange(0, 256), histoCumul[2], color="blue")
        
    
    def equalizePhoto(self, imgName, listTrans) :
        
        print("   - Equalization of " + imgName)
        imgpil = Image.open(imgName)
        exif = imgpil.info["exif"]
        img = np.array(imgpil)
        
        for i in range(img.shape[0]) :
            for j in range(img.shape[1]) :
                value = img[i][j]
                img[i][j][0] = listTrans[0][value[0]]
                img[i][j][1] = listTrans[1][value[1]]
                img[i][j][2] = listTrans[2][value[2]]
        
        imgpil = Image.fromarray(img)
        imgpil.save(self.folderName + "/" + imgName, exif=exif)
        
        
                
            
if __name__ == "__main__" :
    
    equa = histogramEqualizer(["DJI_0186.JPG", "DJI_0187.JPG", "DJI_0191.JPG", "DJI_0192.JPG", "DSC_0305.JPG", "DSC_0306.JPG", "DSC_0311.JPG"], "test")
    #equa.showHistoCumul("DJI_0186.JPG")
    #equa.showHistoCumul("DSC_0311.JPG")
    equa.equalizeMidway()
        
        