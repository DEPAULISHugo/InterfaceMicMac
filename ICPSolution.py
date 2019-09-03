import numpy as np
import random
import TransformPointsUtils

class ICPSolution() :
    
    def __init__(self) :
        self.RandomIndices = []
        self.Matrix = np.identity(4)
        self.MeanDistanceSubset = 0
        self.MeanDistance = 0
        
        self.mode = "homogeneous scale"

        self.pointsTarget = None
        self.pointsSource = None
        self.PointsTransformed = None
        
    def Helper_FindTransformationMatrix(self) :

        #shift points to the center of mass (centroid)
        centroidReference = np.mean(self.pointsTarget, axis=0)
        pointsTargetShift = TransformPointsUtils.CalculatePointsShiftedByCentroid(self.pointsTarget, centroidReference)

        centroidToBeMatched = np.mean(self.pointsSource, axis=0)
        pointsSourceShift = TransformPointsUtils.CalculatePointsShiftedByCentroid(self.pointsSource, centroidToBeMatched)
        
        #calculate correlation Matrix H
        print("         - calculate correlation Matrix H")
        H = TransformPointsUtils.CalculateCorrelationMatrix(pointsTargetShift, pointsSourceShift)
        
        #calulate rotation Matrix R
        print("         - calculate rotation Matrix R")
        R, W = CalculateRotationBySingularValueDecomposition(H, pointsSourceShift)
        
        #calulate scale Matrix C
        print("         - calculate scale")
        if self.mode == "inhomogeneous scale" :
            C = CalculateScale_Du(pointsSourceShift, pointsTargetShift, R)
            R = np.dot(R, C)
        elif self.mode == "homogeneous scale" :
            scale = CalculateScale_Umeyama(pointsSourceShift, W)
            R = R * scale
        
        #calulate translation Matrix T
        T = centroidReference - np.dot(centroidToBeMatched, R)
        
        myMatrix = np.identity(4)
        myMatrix[0:3, 0:3] = R
        myMatrix[0:3, 3] = T

        return myMatrix
    
    def RandomMovements(self) :
        for i in range (3) :
            self.Matrix[0,3] += random.random() - 0.5
            self.Matrix[1,3] += random.random() - 0.5
            self.Matrix[2,3] += random.random() - 0.5
        alpha = random.random() * np.pi - np.pi/2
        betta = random.random() * np.pi - np.pi/2
        delta = random.random() * np.pi - np.pi/2
        Mz = np.array([[np.cos(alpha), -np.sin(alpha), 0], [np.sin(alpha), np.cos(alpha), 0], [0, 0, 1]])
        My = np.array([[np.cos(betta), 0, np.sin(betta)], [0, 1, 0], [-np.sin(betta), 0, np.cos(betta)]])
        Mx = np.array([[1, 0, 0], [0, np.cos(delta), -np.sin(delta)], [0, np.sin(delta), np.cos(delta)]])
        self.Matrix[:3, :3] = np.dot(Mz, np.dot(My,np.dot(Mx,self.Matrix[:3, :3])))
        self.pointsSource = TransformPointsWithMatrix(self.pointsSource, self.Matrix)
        
        
def IndicesAreNew(newIndices, solutionsList) :
    
    if (len(solutionsList) == 0) :
            return True
    
    for i in range (len(solutionsList)) :
        indicesOfList = solutionsList[i].RandomIndices
        
        if newIndices == indicesOfList :
            return False
    
    return True

def GetRandomIndices(maxNumber, myNumberPoints) :      
    randomIndices = random.sample(range(maxNumber), myNumberPoints)
    randomIndices.sort()
    return randomIndices

def SetRandomIndices(myNumberPoints, maxNumber, solutionList) :
    for i in range (1000) :
        randomIndices = GetRandomIndices(maxNumber, myNumberPoints)
        if IndicesAreNew(randomIndices, solutionList) :
            res = ICPSolution()
            res.RandomIndices = randomIndices
            return res
    return None
        
        
def CalculateRotationBySingularValueDecomposition(H, pointsSourceShift) :
    
    U, W, VT = np.linalg.svd(H)
    
    R = np.dot(U, VT)

    return R, W

def CalculateScale_Du(pointsSourceShift, pointsTargetShift, R) :
    
    S = np.identity(3)
    K = np.identity(3)
    for i in range(3) :
        K[i, i] = 0
    for i in range(3) :
        K[i, i] = 1
        sum1 = 0
        sum2 = 0
        for j in range(pointsSourceShift.shape[0]) :
            vKumultiplied = np.dot(K, pointsSourceShift[j])
            v = R.dot(vKumultiplied)
            sum1 += pointsTargetShift[j][0] * v[0] + pointsTargetShift[j][1] * v[1] + pointsTargetShift[j][2] * v[2] 
            sum2 += pointsSourceShift[j][0] * vKumultiplied[0] + pointsSourceShift[j][1] * vKumultiplied[1] + pointsSourceShift[j][2] * vKumultiplied[2]     
        K[i, i] = 0
        S[i, i] = sum1 / sum2
        
    return S

def CalculateScale_Umeyama(pointsSourceShift, eigenvalues) :
    sigmaSquared = np.mean(np.linalg.norm(pointsSourceShift, axis = 1))
    print("Shape", eigenvalues.shape)
    c = np.sum(eigenvalues)
    c = c / sigmaSquared
    return c

def TransformPointsWithMatrix(points, matrix) :
    result = np.ones((points.shape[0],4))
    result[:,0:3] = np.copy(points)
    result = np.dot(matrix, result.T).T[:,:3]
    return result
            
        
        
    