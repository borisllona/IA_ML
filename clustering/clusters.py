from math import sqrt
from math import fabs
import sys
import dendrogram

class bicluster:
    def __init__(self,vec,left=None,right=None,dist=0.0,id=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = dist


def readfile(filename):
    with open(filename) as filen:
        lines=[line for line in filen]
        # First line is the column titles
        colnames=lines[0].strip().split('\t')[1:]
        rownames=[]
        data=[]
        for line in lines[1:]:
            p=line.strip().split('\t')
            # First column in each row is the rowname
            rownames.append(p[0])
            # The data for this row is the remainder of the row
            data.append([float(x) for x in p[1:]])
    
    return rownames,colnames,data

def euclidean(v1,v2):
    return sqrt(euclideansqr(v1,v2))

def euclideansqr(v1,v2):
    return sum(map(lambda x: (x[0]-x[1])**2,zip(v1,v2)))

def manhattan(v1,v2):
    return sum(map(lambda x: fabs(x[0]-x[1]),zip(v1,v2)))

def pearson(v1,v2):
    sum1 = sum(v1)
    sum2 = sum(v2)
    #Sum of the squares    
    sum1Sq = sum([pow(v,2) for v in v1])
    sum2Sq = sum([pow(v,2) for v in v2])
    #Sum of products
    pSum = sum([v1[i] * v2[i] for i in range(len(v1))])
    #Calculate r (Person score)
    num = pSum-(sum1*sum2/len(v1))
    den = sqrt((sum1Sq-pow(sum1,2)/len(v1))*(sum2Sq-pow(sum2,2)/len(v1)))
    if den == 0: return 0
    return 1.0 - num/den

def hcluster(rows,distance=pearson):
    distances={} # stores the distances for efficiency
    currentclustid=-1 # all except the original items have a negative id
    # Clusters are initially just the rows
    clust = [bicluster(rows[i],id=i) for i in range(len(rows))]
    while len(clust)>1: #stop when there is only one cluster left
        lowestpair = (0,1)
        closest = distance(clust[0].vec,clust[1].vec)
        # loop through every pair looking for the smallest distance
        for i in range(len(clust)):
            for j in range(i+1,len(clust)):
                # distances is the cache of distance calculations
                if (clust[i].id,clust[j].id) not in distances:
                    distances[(clust[i].id,clust[j].id)] = distance(clust[i].vec,clust[j].vec)
                
                d = distances[(clust[i].id,clust[j].id)]
                if d < closest:
                    closest = d
                    lowestpair = (i,j)
                # calculate the average of the two clusters
        mergevec=[
        (clust[lowestpair[0]].vec[i]+clust[lowestpair[1]].vec[i])/2.0
        for i in range(len(clust[0].vec))]
        # create the new cluster
        newcluster=bicluster(mergevec,left=clust[lowestpair[0]],
                            right=clust[lowestpair[1]],
                            dist=closest,id=currentclustid)
        # cluster ids that weren’t in the original set are negative
        currentclustid-=1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)
        
    return clust[0]

def printclust(clust,labels=None,n=0):
    # indent to make a hierarchy layout
    for i in range(n): print(' '),
    if clust.id<0:
        # negative id means that this is branch
        print('-')
    else:
        # positive id means that this is an endpoint
        if labels==None: print(clust.id)
        else: print(labels[clust.id])

    # now print the right and left branches
    if clust.left!=None:
        printclust(clust.left,labels=labels,n=n+1)
    if clust.right!=None:
        printclust(clust.right,labels=labels,n=n+1)


def transposeMatrix(data):
    return [list(elem) for elem in zip(*data)]

if __name__ == "__main__":
    rownames,colnames,data = readfile(sys.argv[1])
    clust = hcluster(data)
    dendrogram.drawdendrogram(clust,rownames)