#!/usr/bin/python
# -*- coding: utf-8 -*-

#kaitai

#python 3.5.2


#Random Swap Implementation With K-Means



import copy 
import random 
import sys
import os


#------------------------ K-MEANS ------------------------
    
def k_means(data_set,centroids,k=0,partition=None):
    """

    K-Means implementation for Python.

    Does clustering for given dataset and centroids
    
    Parameters
    ----------
    data_set : N*V dimensional array with N datapoints
        The actual coordinates of the datapoints

    centroids : V dimensional array with C datapoints
        Predefined coordinates of centroids (the length(C) tells how many centroids there are)

    k : int
        If given, stops k-means after k iterations passing 0 or no argument
        will cause the algorithm to continue until there is no improvement in K-means

    partition : scalar array with N datapoints
        Information about which datapoint belongs to which centroid

    """

   
    data_set=copy.deepcopy(data_set)
    centroids=copy.deepcopy(centroids)
    k=copy.deepcopy(k)
    partition=copy.deepcopy(partition)
    
    if k: #k != 0 and k!=None
        if k < 1:
            k=1

    else:
        k=0 #undefined

    if not partition:
        partition = [None]*len(data_set)
        #partition - in which cluster (index) the data point is assigned to
    centroids_prev = None
    

    while (centroids != centroids_prev and (((not k) or k >=1)) ):#[1...k]
        
        #K-Means stops when no improvement happens
        #and there is k which is less than 1 (or non-zero or None)
        if not k:
            pass #block the other cases if k is not given
        elif k==1:
            k-= 2 #avoid 0 which is common default for "undefined"
        else:
            k -= 1


        centroids_prev = copy.deepcopy(centroids)

                
        #update partition
        partition=update_partition(data_set,centroids,partition)#[1...N]*[1...C]
        
        #update centroids
        centroids=update_centroids(data_set,centroids,partition)#[1...N]*[1...V]

                    
    return centroids, partition        


def update_partition(data_set,centroids,partition):
    """

    Updates the partition for each data point to the closest centroid.
    
    Parameters
    ----------
    data_set : N*V dimensional array with N datapoints
        The actual coordinates of the datapoints

    centroids : V dimensional array with C datapoints
        Predefined coordinates of centroids (the length(C) tells how many centroids there are)

    partition : scalar array with N datapoints
        Information about which datapoint belongs to which centroid

    """

    i=0#[1...N]
    for data_point in data_set:
        #[1...C]*[1...V]
        partition[i] = findNearest(data_point,centroids)
        i += 1
    return partition


def update_centroids(data_set,centroids,partition):
    """

    Moves the centroids to the mean point of its datapoints according to the partition.
    
    Parameters
    ----------
    data_set : N*V dimensional array with N datapoints
        The actual coordinates of the datapoints

    centroids : V dimensional array with C datapoints
        Predefined coordinates of centroids (the length(C) tells how many centroids there are)

    partition : scalar array with N datapoints
        Information about which datapoint belongs to which centroid

    """
    
    #IDEA: a centroid is an average of the sum vector of its data points
    
    points_in_c = [0,]*len(centroids)#tracks the amount of data points per cluster
    coords=[[0,]*len(data_set[0]),]*len(partition) #sum vectors

    #"total coordinates" (e.g. (x1+x2+...+xZ),(y1+...+yZ),...)
    p=0#[1...N]
    for part in partition: #part == CI for current data point
        if (points_in_c[part] == 0): #no previous point for this cluster
            coords[part] = data_set[p][:]
            #copy the coords from the first data point
        else:
            q=0#[1..V]
            for xyz in coords[part]:
                #xyz -the coordinate in certain direction
                coords[part][q] = xyz + data_set[p][q]
                q+=1
                
        points_in_c[part] += 1 #count the number of datapoints in every centroid
        

        p += 1

    #move the centroids to new average points
    centroids=move_to_coords(centroids,coords,points_in_c)#[1...C]*[1...V]
    return centroids


def findNearest(data_point,data_points):
    """

    For given data point, returns the index of the closest data point in a list of data points.
    
    Parameters
    ----------
    data_point : 

    data_points : A list of data points

    """

    dist = float('inf') #positive infinity

    closest = None #the index of the closest data point in the array
    i=0#[1...C] (in k-means)
    for p in data_points:
        new_dist=eucl_dist(data_point,p)#[1...V]
        if new_dist<dist:
            dist=new_dist
            closest = i
        i += 1
    return closest #(the index of the closest item in data_points)


def eucl_dist(A,B):
    """

    Calculates and returns euclidean distance between points A and B.
    
    Parameters
    ----------
    A : 

    B : 

    """
    sumAB=0
    i=0
    while i<len(min(A,B)):#square sums
        sumAB += pow(abs(A[i]-B[i]),2)
        i += 1

    return pow(sumAB,0.5)#return sqrt of the square sums

def square_sums(A,B):
    """

    Calculates and returns the square sums of given lists A and B.
    
    Parameters
    ----------
    A : 

    B : 

    """
    sumAB=0
    i=0
    while i<len(min(A,B)):#square sums
        sumAB += pow(abs(A[i]-B[i]),2)
        i += 1

    return sumAB #return the square sums

def move_to_coords(movable,coords,scaling=1): #actually this is a scaling function
    """

    Changes the coordinates according to scaling factor.

    For this case, moves centroids to desired coords.
    The case scaling = 0 will skip the scaling operation for the data point in question.
    
    Parameters
    ----------
    movable : List of scalable data points

    coords : List of current coordinates

    scaling : List of Scaling factors

    """
    a=0#[1...C]
    for c in movable:
        b=0#[1...V]
        for coord in coords[a]:
            if scaling[a] != 0:#avoid zero-division --> scaling 0 or 1 does not do anything
                c[b]= coord/scaling[a] #setting c to the scaled (avg in kmeans) coordinates

            b +=1 


        a += 1

    return movable

#------------------------ RANDOM SWAP ------------------------

def random_swap(data_set,iterations=30,cl_count=0,k=2,centroids=None):
    """

    Performs Random Swap -algorithm for given parameters.

    Uses the k_means function implemented in the file.

    Parameters
    ----------
    data_set : N*V dimensional array with N datapoints
        The actual coordinates of the datapoints

    iterations : int
        If given, stops random swap after the amount of iterations

    cl_count : int
        If given, initializes random_swap with given amount of clusters
        If not given, the cluster amount is definded randomly (between 1...sqrt(N))
        
    k : int
        If given, stops k-means after k iterations passing 0 or no argument
        will cause the algorithm to continue until there is no improvement in K-means

    centroids : V dimensional array with C datapoints
        Predefined coordinates of centroids

    """

    #initialization
    if not centroids:
        print("No centroids predefined")
        print("Predefined centroid count: "+str(cl_count))
        if not cl_count:#no predefined amount for centroids
            cl_count=define_amount(len(data_set))
            print("no set amount for clusters! Randoming cluster amount:", cl_count)

        if cl_count==0:
            print("Error: No data points in the data set!")
            return (centroids,None)

        centroids=get_random_points(data_set,cl_count)

        if (len(centroids)<cl_count):
            print("Error: Not enough data points for all the centroids!")
            return (centroids,None)
        

    partition = [None]*len(data_set)
    partition = update_partition(data_set,centroids,partition)

    #test using deep copies:
    data_set= copy.deepcopy(data_set)
    centroids= copy.deepcopy(centroids)
    partition= copy.deepcopy(partition)

    #swapping
    centroids, partition=swap(data_set,centroids,partition,iterations,k)
            
    return (centroids,partition)


def swap(data_set,centroids,partition,iterations=30,k=2):
    """

    Performs the swapping part of RS-algorithm.

    Parameters
    ----------
    data_set : N*V dimensional array with N datapoints
        The actual coordinates of the datapoints

    centroids : V dimensional array with C datapoints
        Predefined coordinates of centroids

    partition : scalar array with N datapoints
        Information about which datapoint belongs to which centroid
        
    iterations : int
        If given, stops random swap after the amount of iterations    

    k : int
        If given, stops k-means after k iterations passing 0 or no argument
        will cause the algorithm to continue until there is no improvement in K-means

    """
    
    print("Initial TSE:")
    print(calc_tse(data_set,centroids,partition))
    for i in range(iterations):
        if (i% (max(iterations/10,1)) == 0):
            print("iteration: ",i+1)
        centroids_prev = copy.deepcopy(centroids)
        partition_prev = copy.deepcopy(partition)

        #swap centroid to one point of the data set
        swap_item(centroids,data_set)
        
        #using k-means
        centroids,partition = k_means(data_set,centroids,k,partition)

        #if no improvement --> revert the changes
        if (calc_tse(data_set,centroids,partition) \
            >= calc_tse(data_set,centroids_prev,partition_prev)):
            centroids=centroids_prev
            partition=partition_prev

##        else: #only for testing -prints all the results which improve tse
##            print(calc_tse(data_set,centroids,partition))

    print("Final TSE:")
    print(calc_tse(data_set,centroids,partition))

    return centroids, partition


def define_amount(number):
    """

    If not given, randomly assigns the amount of cluster for RS.

    Parameters
    ----------
    number : int
        The number of data points (N)
        
    """
    if number<10: #a "random" way for less than 10 data points
        amount= random.uniform(min(2,(number+1)/2),min((5,(number+1)/2)))
    else:#amount= [sqrt(#data_points)/2...sqrt(#data_points)] (just a way to get some (random amount of) centroids)
        amount = random.uniform(pow(number,0.5)/2,pow(number,0.5))

    return int(amount)


def get_random_points(data,amount):
    """

    Randomly assigns the centroids to the data.

    Selects a data point randomly and places centroid there.
    The function will assign the centroids in separate data points.

    Parameters
    ----------
    data : N*V dimensional array with N datapoints
        The actual coordinates of the datapoints

    amount : int
        The count of centroids (C)
        
    """
    
    _data= list(data)
    randomed = list()
    while (len(randomed)<min(len(data),amount) and len(_data)>0 ):#len data shouldnt be needed
        a=random.choice(_data)
        _data.remove(a)
        randomed.append(copy.deepcopy(a))

    return randomed

def swap_item(item_list,choices):
    """

    Swaps a random item from item_list into one in the choices.

    In this case, resets the item's coords with the coors of the chosen data point.

    Parameters
    ----------
    item_list : List of the items to choose from

    choices : List of the items to swap into
        
    """
    pivot = random.choice(range(len(item_list)))
    item_list[pivot] = copy.deepcopy(random.choice(choices))
    
#------------------------ ERROR CALCULATIONS ------------------------

def calc_tse(data,centroids,partition):
    """

    Calculates total squared error (TSE) for given data, centroids and partition.

    Parameters
    ----------
    data : N*V dimensional array with N datapoints
        The actual coordinates of the datapoints

    centroids : V dimensional array with C datapoints
        Predefined coordinates of centroids

    partition : scalar array with N datapoints
        Information about which datapoint belongs to which centroid
        
    """

    total_error = 0
    i = 0
    #for each data point calc the distance to preferred cluster
    #(partition[i] is the preferred cluster index for data[i]
    for p in partition:
        total_error += square_sums(data[i],centroids[p])
        #total_error += eucl_dist(data[i],centroids[p])

        i += 1

    return total_error

def calc_mse(data,centroids,partition):
    """

    Calculates mean squared error (MSE) for given data, centroids and partition.

    Actually calculates nMSE (TSE/(N*V)).
    
    Parameters
    ----------
    data : N*V dimensional array with N datapoints
        The actual coordinates of the datapoints

    centroids : V dimensional array with C datapoints
        Predefined coordinates of centroids

    partition : scalar array with N datapoints
        Information about which datapoint belongs to which centroid
        
    """
    return ((calc_tse(data,centroids,partition))/(len(data[0])*len(data)))#tse/(d*n)


#Centroid Index
#TODO: CI and CD not finished yet
def CI(solution1,solution2):
    """

    Calculates centroid index (CI) between two solutions.

    Returns 0 for similar solutions and >0 for different solutions
        
    Parameters
    ----------
    solution1 : Centroid locations for the first solution

    solution1 : Centroid locations for the second solution
        
    """
    
    pos=centroid_difference(solution1,solution2)
    neg=centroid_difference(solution2,solution1)

    #solution 2 better --> positive result
    #solution 1 better --> negative result
    #equally good solutions --> 0
    #the number tells CI difference between solutions
    pivot=max(pos,neg)
##    if pos == neg:
##        ""
##    elif abs(pos) > abs(neg):
##        pivot = pos
##    else:
##        pivot = -neg
    return pivot

def centroid_difference(solution,ground):
    """

    Calculates centroid difference between a suggested solution and ground truth.

    Returns 0 for similar solutions and >0 for different solutions
        
    Parameters
    ----------
    solution : Centroid locations for the solution

    ground : Centroid locations for the ground truth
        
    """
    array=[0]*len(solution)
    for c in solution:
        index=findNearest(c,ground)
        array[index] += 1

##    print(array)
    amount=0
    for i in array:
        if not i:
            amount += 1
    
    return amount


#____________________________________________________________________
#read_file.py
#IO-functions

#kaitai

#python 3.5.2


#read-func my own solution from even earlier
    
def read(path):
    """

    Reads a txt-file for given path
        
    Parameters
    ----------
    path : file path
        
    """
    try:
        tiedosto=open((path),"r")
        data=tiedosto.readlines()
        tiedosto.close()
    except IOError:
        print("Error when trying to read the file.")
        data=[]
    finally:
        if "tiedosto" in locals():
            tiedosto.close()
            

    indeksi=0
    #remove line breaks from the end of the lines
    while indeksi<len(data):
        data[indeksi]=data[indeksi].rstrip("\n")
        indeksi+=1

    return data

    #convert rows as coordinates in order to use them
    #in k-means function

def write(path,data):
    """

    Writes a txt-file for given path.

    The data uses the same format which is required for the data samples.
    Converts the coordinates into integers as well.
        
    Parameters
    ----------
    path : file path

    data : The coordinates of the data points
        
    """
    try:
        file=open((path),"w")
        stream=data_to_str(data)
        file.write(stream)
        stream= ""
        
    except IOError:
        print("Error when trying to write the file.")
    finally:
        if "file" in locals():
            file.close()

def data_to_str(data):
    """

    Converts data back to the format required in files.

    The data uses the same format which is required for the data samples.
    Converts the coordinates into integers as well.

        
    Parameters
    ----------
    data : The coordinates of the data points
        
    """
    stream=""
    
    for point in data:
        line=""
        for coord in point:
            line += '\t'+str(int(coord))

        stream += line+'\n'

    stream.strip()
    
    return stream

def suit_kmeans(data):
    """

    Modifies data so it can be run with random_swap and k_means -functions.
        
    Parameters
    ----------
    data : Data read from text file
        
    """
    suitable=[[0,],]*len(data)
    i=0
    for data_row in data:
        new_row =(data_row.split())
        j=0
        suitable[i]= [0]*len(new_row)
        for compound in new_row:
            suitable[i][j]=int(compound)
            j += 1
        i += 1

    return suitable
        

    
def get_data(path):
    """

    Gives the data in proper form for given file path.

    The data in the file has to be in certain form (an example):

    SOF
        664159    550946
        665845    557965
        597173    575538
        618600    551446
        635690    608046
    EOF

    Can be used with more dimensions as long as the coordinates (XYZ...) are tabulated
    and data points are separated from each other with line breaks.
        
    Parameters
    ----------
    data : Data read from text file
        
    """
    return suit_kmeans(read(path))


#____________________________ MAIN ____________________________

def main():
    """

    The function to be called when used as a srcipt.
        
    """
    real_out=sys.stdout #real_out is variable to handle printing

    data_f,iterations,clusters,k,suppress, write_f =set_params(sys.argv)
    if suppress:
        real_out=stop_out_print(real_out,True)
        
    solution,part= random_swap(data_f,iterations,clusters,k)

    if suppress:
        real_out=stop_out_print(real_out,False)
    if write_f:
        write(write_f,solution)
    else:
        if not suppress:
            print("\nClustering Results:\n")
            print(data_to_str(solution))
            print("\n")


    error= calc_mse(data_f,solution,part)
    print("error (MSE): "+str(error))
    #sys.exit() 
    
def print_help(args):
    """

    Prints help texts on the command line.
        
    Parameters
    ----------
    args : system arguments
        
    """
    print("")
    print("USAGE: \"function dataset.txt [iterations clusters k suppress write_file]\"")
    print("") #following line: splitting twice, because '/' or '\' may be used in paths depending on the environment
    print("\t where \t'function' \t= module name such as \t\t\t'"+args[0].split(sep='\\')[-1].split(sep='/')[-1]+"' ")
    print("\t where \t'dataset.txt' \t= .txt filename such as \t\t's1.txt' ")
    print("\t where \t'iterations' \t= number of swaps such as \t\t'100' ")
    print("\t where \t'clusters' \t= number of clusters such as \t\t'15' ")
    print("\t where \t'k' \t\t= number of k-means iterations such as \t'2' ")
    print("\t where \t'suppress' \t= integer: 0 prints all, !0 results only'0' ")
    print("\t where \t'write_file' \t= output .txt file (coords) such as \t'results.txt' ")
    print("")
    print("NOTES: The arguments have to be in the specified order.")
    

def set_params(args):
    """

    Assigns the parameters to user specified ones or defaults

    Also checks there is enough parameters and some simple user errors.
        
    Parameters
    ----------
    args : system arguments
        
    """

    if (len(args)<2): #No arguments given by user
        print_help(args)
        sys.exit()
        
    params=args[1:]
    data_f=get_data(params[0])
    if len(data_f)<1: #Data File Reading Failed
        sys.exit()
    suppress=0
    iterations,clusters,k, write_f = 100,15,2,None #default settings
    if len(params)<2:
        print("NOTE: Using defaults: iterations = "+str(iterations)+", clusters = "+str(clusters)+", k = "+str(k)+"\n")
    
    try:
        if len(params)>1:
            iterations=int(params[1])
        if len(params)>2:
            clusters=int(params[2])
        if len(params)>3:
            k=int(params[3])
        if len(params)>4:
            suppress=int(params[4])
        if len(params)>5:
            write_f=params[5] 
    except ValueError:
        print("ERROR: Could not handle the input properly (Conversion from str to int failed)")
        print_help(args)
        sys.exit()

    return data_f,iterations,clusters,k,suppress, write_f


#____________________________ UTILS ____________________________

def stop_out_print(actual,out=False):
    """

    If out, stops printing - If !out allows printing.

    Remember to store 'actual' in order to allow print again.
    It should be passed every time to the function.
    The function also returns it every time it is run.
        
    Parameters
    ----------
    actual : sys.stdout (the original outputfile object)

    out : bool
        True or False, depending on if the output is to be suppressed or enabled.
        
    """
    
    #idea from stackoverflow
    if out:
        sys.stdout.flush() #it was on before this --> output everything
        sys.stdout = open(os.devnull,'w')

    else: #it was off--> use the actual stdout
        sys.stdout = actual
        
    return actual

if __name__ == "__main__":
    main()
    # execute only if run as a script




