import sys

dat_file = []

class decisionnode():
    def __init__(self,col=-1,value=None,results=None,tb=None,fb=None):
        self.col = col
        self.value = value
        self.results = results
        self.tb = tb
        self.fb = fb

    def isLeaf(self):
        return self.results != None


def read(file_name):
    lista = []
    with open(file_name) as f:
        for line in f:
            line = line.replace(' ','\t')
            line = line.replace(',','\t')
            row = line.split('\t',)
            for i in range(len(row)):
                if row[i].isdigit(): row[i] = int(row[i])
            lista.append(row)
    return lista

def unique_counts(part):
    #Counts the number of prototypes of a given class in a partition part.
    if len(part)==0: return {}
    results = {}

    for i in part:  
        elm = i[-1].split('\n')[0]
        if elm in results: results[elm]+=1
        else: results[elm]=1
    
    return results

def gini_impurity(part):
    total = len(part)
    results = unique_counts(part)
    imp = 0
    prob = []
    for i in results:
        prob.append(results[i]/sum(results.values()))
    for j in prob:
        imp+=j**2
    imp = 1 - imp    
    
    return(imp)

def entropy(part):
    from math import log
    log2 = lambda x: log(x)/log(2)

    results = unique_counts(part)
    imp = 0.0
    total = float(len(part))

    probs = (v / total for v in results.values())

    return -sum((p * log2(p) for p in probs))


def divideset(part,column,value):
    split_function = None
    set1, set2 = [], []

    #We separate in two functions, one for categorical values and another for digits.
    if value == type(int) or value == type(float):
        split_function =  lambda prot: prot[column]<=value
    else:
        split_function =  lambda prot: prot[column]==value


    for elem in part:
        if split_function(elem):
            set1.append(elem)
        else:
            set2.append(elem)

    return(set1,set2)   


def buildtree(part,scoref=entropy,beta=0):

    if len(part)==0: return decisionnode()
    
    #Goodness of a partition: Decrease of impurity achived -> i(t) - pl*i(tl) - pr*(tr)
    #We choose the best impirity decrease.
    t = scoref(part) 
    best_gain = 0 #Impurity decrement, it has to be max.
    best_criteria = (None,None) #(col,value)
    best_sets = (None,None) #(set1,set2)

    for column in part:
        for index in range(0,len(column)-1):
            sets = divideset(part,index,column[index])
            tl = scoref(sets[0])
            tr = scoref(sets[1])
            current_score = t - (len(sets[0])/len(part)*tl) - (len(sets[1])/len(part)*tr)
            
            if current_score > best_gain:
                best_gain = current_score
                best_criteria = (index,column[index])
                best_sets = sets

    if best_gain > beta:
        bt = buildtree(best_sets[0], scoref=scoref, beta=beta) 
        bf = buildtree(best_sets[1], scoref=scoref, beta=beta)
        return decisionnode(col=best_criteria[0],value=best_criteria[1],tb=bt,fb=bf)
    else:  #Hoja  
        return decisionnode(results=unique_counts(part))

def classify(tree, newdata):

    if tree.value == type(int) or tree.value == type(float):
        split_function =  lambda prot: prot[tree.col]<=tree.value
    else:
        split_function =  lambda prot: prot[tree.col]==tree.value

    while not tree.isLeaf():
        if split_function(newdata):
            tree = tree.tb
        else:
            tree = tree.fb

    return tree.results

def printtree(tree,indent=''):
    # Is this a leaf node?
    if tree.results!=None:
        print(str(tree.results))
    else:
        # Print the criteria
        print(str(tree.col)+':'+str(tree.value)+'?')
        # Print the branches
        print(indent+'T->',)
        printtree(tree.tb,indent+' ')
        print(indent+'F->',)
        printtree(tree.fb,indent+' ')

if __name__ == "__main__":
    dat_file = read(sys.argv[1])
    tree = buildtree(dat_file) #Pequeño fallo a veces en el final del arbol, testear.
    print(classify(tree,['red','short','no','rough']))
    printtree(tree)