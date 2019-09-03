import numpy as np
from plyfile import PlyData, PlyElement
import os
from sklearn.neighbors import NearestNeighbors

def getCoordinatesFromFile(fileName) :
    file = open(fileName, "r")
    for line in file.readlines():
        if "<Centre>" in line :
            debut = line.index("<Centre>") + 8
            fin   = line.index("</Centre>")
            coordinates = line[debut:fin].split(" ")
            vector = np.array([float(coordinates[0]), float(coordinates[1]), float(coordinates[2])])
            return vector

def getMatrixFromFile(fileName) :
    file = open(fileName, "r")
    for line in file.readlines():
        if "<L1>" in line :
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
            return matrixRot

def getAngleFromMatrix(matrix):
    if matrix[0][1] < 1 :
        if matrix[0][1] > -1 :
            thetaX = np.arctan2(matrix[2][1], matrix[1][1])
            thetaY = np.arctan2(matrix[0][2], matrix[0][0])
            thetaZ = np.arcsin(-matrix[0][1])
        else :
            thetaX = - np.arctan2(-matrix[2][0], matrix[2][2])
            thetaY = 0
            thetaZ = np.pi / 2
    else :
        thetaX = np.arctan2(-matrix[2][0], matrix[2][2])
        thetaY = 0
        thetaZ = - np.pi / 2
             
    return thetaX * 180/np.pi, thetaY * 180/np.pi, thetaZ * 180/np.pi

def getCloudFromFile(fileName) :
    plydata = PlyData.read(fileName)
    cloud = np.array((plydata['vertex'].data['x'], plydata['vertex'].data['y'], plydata['vertex'].data['z'])).T
    return cloud

def comparePosiCali(cali1, cali2) :
    folderCali1 = cali1.pointsLiaisons.chunk.dossier + "/Ori-" + cali1.nom
    folderCali2 = cali2.pointsLiaisons.chunk.dossier + "/Ori-" + cali2.nom
    listDistance = []
    listDX = []
    listDY = []
    listDZ = []
    listPhotos   = []
    for fileName1 in os.listdir(folderCali1):
        if "Orientation-" in fileName1 :
            for fileName2 in os.listdir(folderCali2):
                if fileName1 == fileName2 :
                    coordinates1 = getCoordinatesFromFile(folderCali1+"/"+fileName1)
                    coordinates2 = getCoordinatesFromFile(folderCali2+"/"+fileName2)
                    dist = np.linalg.norm(coordinates1 - coordinates2)
                    dX = coordinates1[0] - coordinates2[0]
                    dY = coordinates1[1] - coordinates2[1]
                    dZ = coordinates1[2] - coordinates2[2]
                    listDistance.append(dist)
                    listDX.append(dX)
                    listDY.append(dY)
                    listDZ.append(dZ)
                    listPhotos.append(fileName1[12:-4])
    return listDistance, listDX, listDY, listDZ, listPhotos


def compareAngleCali(cali1, cali2) :
    folderCali1 = cali1.pointsLiaisons.chunk.dossier + "/Ori-" + cali1.nom
    folderCali2 = cali2.pointsLiaisons.chunk.dossier + "/Ori-" + cali2.nom
    listDThetaX = []
    listDThetaY = []
    listDThetaZ = []
    listPhotos   = []
    for fileName1 in os.listdir(folderCali1):
        if "Orientation-" in fileName1 :
            for fileName2 in os.listdir(folderCali2):
                if fileName1 == fileName2 :
                     matrix1 = getMatrixFromFile(folderCali1+"/"+fileName1)
                     matrix2 = getMatrixFromFile(folderCali2+"/"+fileName2)
                     thetaX1, thetaY1, thetaZ1 = getAngleFromMatrix(matrix1)
                     thetaX2, thetaY2, thetaZ2 = getAngleFromMatrix(matrix2)
                     listDThetaX.append(thetaX2 - thetaX1)
                     listDThetaY.append(thetaY2 - thetaY1)
                     listDThetaZ.append(thetaZ2 - thetaZ1)
                     listPhotos.append(fileName1[12:-4])
    return listDThetaX, listDThetaY, listDThetaZ, listPhotos

def comparePosiPC(PC1, PC2) :
    fileName1 = PC1.caliEtMEP.pointsLiaisons.chunk.dossier + "/" + PC1.nom + ".ply"
    fileName2 = PC2.caliEtMEP.pointsLiaisons.chunk.dossier + "/" + PC2.nom + ".ply"
    cloud1 = getCloudFromFile(fileName1)
    cloud2 = getCloudFromFile(fileName2)
    kdtree = NearestNeighbors(n_neighbors=1)
    kdtree.fit(cloud2)
    distances, indices = kdtree.kneighbors(cloud1)
    print(distances)
    return distances
    
