import numpy as np 

def CalculatePointsShiftedByCentroid(a, centroid) :
    #shift    
    b = a - centroid
    return b;

def CalculateCorrelationMatrix(b, a) :
    #consists of elementx 
    #axbx axby axbz
    #aybx ayby aybz
    #azbx azby azbz
    H = np.zeros((3,3));
    
    for i in range(a.shape[0]) :
        
        H[0, 0] += b[i][0] * a[i][0]
        H[0, 1] += b[i][0] * a[i][1]
        H[0, 2] += b[i][0] * a[i][2]

        H[1, 0] += b[i][1] * a[i][0]
        H[1, 1] += b[i][1] * a[i][1]
        H[1, 2] += b[i][1] * a[i][2]

        H[2, 0] += b[i][2] * a[i][0]
        H[2, 1] += b[i][2] * a[i][1]
        H[2, 2] += b[i][2] * a[i][2]

    H = H / b.shape[0]
    return H