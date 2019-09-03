from sklearn.neighbors import NearestNeighbors
import numpy as np
import TransformPointsUtils
import copy
from plyfile import PlyData, PlyElement
import ICPSolution
#import open3d as o3d

class IterativeClosestPointTransform() :

    def __init__(self, sourceFile, targetFile, maxIteration, sample, matrix) :
        self.NumberPointsSolution = 100
        self.NormalsSource = None
        self.NormalsTarget = None
        
        self.mode = "inhomogeneous scale"
        
        self.MaxNumberSolutions = 10
        self.NumberOfStartTrialPoints = 100000
    
        self.SimulatedAnnealing = False
        self.NormalsCheck = False
        self.FixedTestPoints = False
        self.MaximumNumberOfIterations = maxIteration
        self.ResetVertexToOrigin = True
        self.DistanceOptimization = False
        
        self.Matrix = matrix
        self.NumberOfIterations = 0
        self.pointsTransformed = 0

        self.MeanDistance = 0

        self.MaximumMeanDistance = 1.0E-3
        self.ThresholdOutlier = 10


        self.LandmarkTransform = None
        self.solutionList = [] # List<ICPSolution> solutionList
    
        self.sourceFile = sourceFile
        self.targetFile = targetFile
        
        plydataA = PlyData.read(sourceFile)
        plydataB = PlyData.read(targetFile)
        
        self.PSource = np.array((plydataA['vertex'].data['x'], plydataA['vertex'].data['y'], plydataA['vertex'].data['z'])).T #public List<Vertex> PSource;
        self.PTarget = np.array((plydataB['vertex'].data['x'], plydataB['vertex'].data['y'], plydataB['vertex'].data['z'])).T #public List<Vertex> PTarget;
        
        self.PSource = TransformPointsWithMatrix(self.PSource, self.Matrix)
        
        if sample < 1 :
                   
            idSource = np.random.randint(self.PSource.shape[0], size=int(self.PSource.shape[0]*sample)) 
            self.PSource = self.PSource[idSource, :]
            
#        idTarget = np.random.randint(self.PTarget.shape[0], size=int(self.PTarget.shape[0]*0.5)) 
#        self.PTarget = self.PTarget[idTarget, :]
        
        self.pointsSource = np.copy(self.PSource)
        self.pointsTarget = np.copy(self.PTarget)

    def Reset(self) :
        self.SimulatedAnnealing = False
        self.NormalsCheck = False
        self.FixedTestPoints = False
        self.MaximumNumberOfIterations = 100
        self.ResetVertexToOrigin = True
        self.DistanceOptimization = False

    def PerformICP1(self, myPointsTarget, mypointsSource) :

        self.PTarget = myPointsTarget
        self.PSource = mypointsSource
        
        #if (ICPVersion == ICP_VersionUsed.UsingStitchData)
        #    return PerformICP_Stitching();
        #else if (ICPVersion == ICP_VersionUsed.RandomPoints)
        #    return PerformICP();
        #else
        #    return PerformICP();

    def Inverse(self) :
        tmp1 = self.PSource
        self.PSource = self.PTarget
        self.PTarget = tmp1

    def Helper_CreateTree(self, pointsTarget) :
        kdtree = NearestNeighbors(n_neighbors=1)
        kdtree.fit(pointsTarget)
        return kdtree

    def Helper_FindNeighbours(self, kdTree, keepOnlyPoints, myTrial=None) :
        
        if (not(self.FixedTestPoints)) :
            
            #pointsTarget = kdTree.FindNearest_BruteForce(pointsSource, pointsTarget);
            if myTrial == None :
                self.pointsTarget = FindNearest(self.pointsSource, self.pointsTarget, kdTree)     
            else :
                myTrial.pointsTarget = FindNearest(myTrial.pointsSource, myTrial.pointsTarget, kdTree)

            if(self.NormalsCheck) :

                #adjust normals - because of Search, the number of PointTarget my be different

                pointsRemoved = 0;
#                for i in range (pointsTarget.shape[0]) :
#                    indexVec = i #int indexVec = pointsTarget[i].IndexInModel;
#                    vTNormal = self.NormalsTarget[indexVec]
#                    vSNormal = self.NormalsSource[i]
#                    
#                    angle = np.arccos(np.dot(vTNormal, vSNormal) / (np.linalg.norm(vTNormal) * np.linalg.norm(vSNormal)))
#                    
#                    if abs(angle * 180 / np.pi) > 30 :
#                        pointsTarget = np.delete(pointsTarget, (i), axis=0)
#                        pointsTarget = np.delete(pointsTarget, (i), axis=0)
#                        pointsRemoved += 1
                
                print("--NormalCheck: Removed a total of: " + str(pointsRemoved))
            if myTrial == None :
                if self.pointsTarget.shape[0] != self.pointsSource.shape[0] :
                    print("Error finding neighbours, found " + str(self.pointsTarget.shape[0]) + " out of " + str(self.pointsSource.shape[0]))
                    return False
            else :
                if myTrial.pointsTarget.shape[0] != myTrial.pointsSource.shape[0] :
                    print("Error finding neighbours, found " + str(self.pointsTarget.shape[0]) + " out of " + str(self.pointsSource.shape[0]))
                    return False
        
        else :
            
            #adjust number of points - for the case if there are outliers
            print("Oups!")
            intmin = self.pointsSource.shape[0]
            if (self.pointsTarget.shape[0] < intmin) :
                intmin = self.pointsTarget.shape[0]
                self.pointsSource = self.pointsSource[:intmin]
            else :
                self.pointsTarget = self.pointsTarget[:intmin]
        return True;

    def TransformPoints(self, pointsTarget, pointsSource, myMatrix, kdtree) :
        myPointsTransformed = TransformPointsWithMatrix(pointsSource, myMatrix)
        pointsTarget = FindNearest(myPointsTransformed, pointsTarget, kdtree)
        totaldist = CalculateTotalDistance(pointsTarget, myPointsTransformed)
        meanDistance = totaldist / pointsTarget.shape[0]
        return meanDistance

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
        
        #calulate scale 
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

    def Helper_SetNewInterationSets(self, PT, PS) :
        myPointsTransformed = TransformPointsWithMatrix(PS, self.Matrix)
        self.pointsSource = myPointsTransformed
        self.pointsTarget = copy.deepcopy(PT)

    def Helper_ICP_Iteration(self, PT, PS, kdTree, keepOnlyPoints, myTrial=None) :
            
        print("      - Check neighbours")
        if (not(self.Helper_FindNeighbours(kdTree, keepOnlyPoints, myTrial))) :
            return True
        print("      - Calculate transformation matrix")
        if myTrial == None :
            myMatrix = self.Helper_FindTransformationMatrix()
            myPointsTransformed = TransformPointsWithMatrix(self.pointsSource, myMatrix)
        else :
            myMatrix = myTrial.Helper_FindTransformationMatrix()
            myPointsTransformed = TransformPointsWithMatrix(myTrial.pointsSource, myMatrix)
            

        if (self.SimulatedAnnealing) :

            self.Matrix = myMatrix
            totaldist = CalculateTotalDistance(myTrial.pointsTarget, myPointsTransformed)
            self.MeanDistance = totaldist / self.pointsTarget.shape[0]
            
            #new set:
            myTrial.pointsSource = myPointsTransformed
            myTrial.pointsTarget = copy.deepcopy(PT)

        else :
            self.Matrix = np.dot(myMatrix, self.Matrix)
            print(self.Matrix)
            totaldist = CalculateTotalDistance(self.pointsTarget, myPointsTransformed)
            newMeanDistance = totaldist / self.pointsTarget.shape[0]
            self.MeanDistance = newMeanDistance
            #Debug.WriteLine("--------------Iteration: " + iter.ToString() + " : Mean Distance: " + MeanDistance.ToString("0.00000000000"));

            if self.MeanDistance < self.MaximumMeanDistance :
                return True

            self.Helper_SetNewInterationSets(PT, PS)
            
        return False;

    
    def Helper_ICP_Iteration_SA(self, PT, PS, kdTree, keepOnlyPoints) :
        
        #first iteration
        if (len(self.solutionList) == 0) :
            self.NumberOfStartTrialPoints = int(PS.shape[0] * 20/100)
            if (self.NumberOfStartTrialPoints < 3) :
                self.NumberOfStartTrialPoints = 3
            
            self.GenerateSolution(PS, PT)
                    
        for myTrial in self.solutionList :
            self.Helper_ICP_Iteration(PT, PS, kdTree, keepOnlyPoints, myTrial)
            myTrial.Matrix = np.dot(myTrial.Matrix, self.Matrix)
            myTrial.MeanDistanceSubset = self.MeanDistance
            myTrial.MeanDistance = self.TransformPoints(PT, PS, myTrial.Matrix, kdTree)
            
        if len(self.solutionList) > 0 :
            for s in self.solutionList :
                print(s.MeanDistance)
            print("ok")
            self.solutionList.sort(key=lambda v: v.MeanDistance)
            for s in self.solutionList :
                print(s.MeanDistance)
            self.Matrix = self.solutionList[0].Matrix
            self.MeanDistance = self.solutionList[0].MeanDistance
            self.pointsSource = TransformPointsWithMatrix(self.pointsSource, self.Matrix)
            print(self.Matrix)
            if self.solutionList[0].MeanDistance < self.MaximumMeanDistance :
                return True
            self.solutionList = []
            self.SimulatedAnnealing = False
#
#    def CalculateNormals(self, pointsSourceFile, pointsTargetFile) :
#        
#        myModelTarget = o3d.io.read_point_cloud(pointsTargetFile)
#        myModelTarget.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.5, max_nn=30))
#        self.NormalsTarget = np.asarray(myModelTarget.normals)
#
#        myModelSource = o3d.io.read_point_cloud(pointsSourceFile)
#        myModelSource.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.5, max_nn=30))
#        self.NormalsSource = np.asarray(myModelSource.normals)
#            
            
    def PerformICP(self) :
        
        print("--------Start ICP--------")

        PT = copy.deepcopy(self.PTarget)
        PS = copy.deepcopy(self.PSource)
        
#        pSOrigin = None
#        pTOrigin = None
#
#        if self.ResetVertexToOrigin :
#            pTOrigin = Vertices.ResetVertexToOrigin(PT);
#            pSOrigin = Vertices.ResetVertexToOrigin(PS);

        keepOnlyPoints = 0;
        
        if self.DistanceOptimization :
            keepOnlyPoints = 3;
        
        if not(self.CheckSourceTarget(PT, PS)) :
            return None
                
        kdTree = self.Helper_CreateTree(PT)
        
        print(" + Start iterations")
        
        for iteration in range (self.MaximumNumberOfIterations) :
            if self.NormalsCheck :
                self.CalculateNormals(PS, PT)
            if self.SimulatedAnnealing :
                print("   - Start simulated annealing iteration", iteration)
                if self.Helper_ICP_Iteration_SA(PT, PS, kdTree, keepOnlyPoints) :
                    break
            else :
                print("   - Start normal iteration", iteration)
                if self.Helper_ICP_Iteration(PT, PS, kdTree, keepOnlyPoints) :
                    break
            self.CreatePlyTransformed("TESTMERGE-" + str(iteration) + ".ply")
            
            print("--------------Iteration: " + str(iteration) + " : Mean Distance: " + str(self.MeanDistance))
        
        print("--------****** Solution of ICP after : " + str(iteration) + " iterations, and Mean Distance: " +str(self.MeanDistance))
        
        PTransformed = TransformPointsWithMatrix(PS, self.Matrix)
        
        return PTransformed
                              
    def CheckSourceTarget(self, myPointsTarget, mypointsSource) :

        # Check source, target
        if (mypointsSource.shape[0] == 0) :
            print("Source point set is empty")
            print("Can't execute with null or empty input")
            return False

        if (myPointsTarget.shape[0] == 0) :
            print("Target point set is empty")
            print("Can't execute with null or empty target")
            return False
        return True
    
    def CreatePlyTransformed(self, fileName) :
        
        sourceFilePly = PlyData.read(self.sourceFile)
        source = np.array((sourceFilePly['vertex'].data['x'], sourceFilePly['vertex'].data['y'], sourceFilePly['vertex'].data['z'])).T
        transformedSource = TransformPointsWithMatrix(source, self.Matrix)
        listTuple = [tuple(x) for x in transformedSource.tolist()]
        vertex = np.array(listTuple, dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4')])
        el = PlyElement.describe(vertex, 'vertex')
        PlyData([el]).write(fileName)
        
    def GenerateSolution (self, PS, PT) :
        newList = []
        for i in range (4) :
            for j in range (4) :
                for k in range (4) :
                    if (i != 0 and j != 0 and k != 0) or (self.Matrix[0,0] == 1 and self.Matrix[1,1] == 1 and self.Matrix[2,2] == 1):
                        myTrial = ICPSolution.SetRandomIndices(self.NumberOfStartTrialPoints, PS.shape[0], self.solutionList)
                        if (myTrial != None) :
                            myTrial.pointsSource = copy.deepcopy(PS[myTrial.RandomIndices,:])
                            myTrial.pointsTarget = copy.deepcopy(PT)
                        alpha = i * np.pi / 4
                        betta = j * np.pi / 4
                        delta = k * np.pi / 4
                        Mz = np.array([[np.cos(alpha), -np.sin(alpha), 0], [np.sin(alpha), np.cos(alpha), 0], [0, 0, 1]])
                        My = np.array([[np.cos(betta), 0, np.sin(betta)], [0, 1, 0], [-np.sin(betta), 0, np.cos(betta)]])
                        Mx = np.array([[1, 0, 0], [0, np.cos(delta), -np.sin(delta)], [0, np.sin(delta), np.cos(delta)]])
                        myTrial.Matrix[:3, :3] = np.dot(Mz, np.dot(My,np.dot(Mx,myTrial.Matrix[:3, :3])))
                        myTrial.pointsSource = TransformPointsWithMatrix(myTrial.pointsSource, myTrial.Matrix)
                        newList.append(myTrial)
        self.solutionList = newList
                        
              
def CalculateRotationBySingularValueDecomposition(H, pointsSourceShift) :
    
    U, W, VT = np.linalg.svd(H)
    
    R = np.dot(U, VT)

    return R, W

def FindNearest(source, target, kdtree) :
    
#    result = np.zeros(source.shape)
#    tempTarget = copy.deepcopy(target)
#    
#    percent = 0
#    
#    print("               + " + str(percent * 5)  + " %")
#    
#    for i in range (source.shape[0]) :
#        kdTree = KDTree(tempTarget)
#        dist, ind = kdTree.query(source, k=1)
#        indexNearest = ind[0]
#        result[i] = target[indexNearest]
#        tempTarget = np.delete(tempTarget, (indexNearest), axis=0)
#        if (percent + 1) * 5 / 100 < i / source.shape[0] :
#            percent += 1
#            print("               + " + str(percent * 5)  + " %")
    indices = kdtree.kneighbors(source, return_distance=False).ravel()
    
    return target[indices,:]

def CalculateTotalDistance(a, b) :
    totaldist = np.sum(np.sqrt(np.sum((a-b)**2, axis=1)))
    return totaldist

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

if __name__ == "__main__" :
    
    matrix = np.array([[-0.022, 0.041, 0.999, 0.215],[0.007, 0.999, -0.040, -0.155],[-1, 0.006, -0.023, 0.091], [0, 0, 0, 1]])
    
    icp = IterativeClosestPointTransform("data_bunny.ply", "model_bunny.ply", 20, 1, matrix)
    icp.PerformICP()
    print(icp.Matrix)
    icp.CreatePlyTransformed("TESTMERGE.ply")
    
    
        
    


        
        
    
    

