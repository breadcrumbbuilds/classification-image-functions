"""
Created by: brad.crump 

Used to create a subset of classes for a classification problem.
Writes a map file that balances instances of classes in a 
classification context.
"""


import random
import datetime as dt
"""
Define the name of the map File
"""
MAPFILE = "CompleteMap.RGB.txt"


"""
Assumes mapfile structure "somePath\ToImage\<class>\n"
Returns the class of a file
"""
def getClass(line):
    return str(line[len(line) - 2])


"""
Creates a list of unique classes in the mapFile
"""
def createUniqueClasses(mapFile):
    listOfUniqueClasses = []
    for line in mapFile:
        classInstance = getClass(line)
        
        # If we have already come across this class, continue
        if classInstance in listOfUniqueClasses:
            continue
        
        # If not, add it to the unique classes list
        else:
            listOfUniqueClasses.append(classInstance)
  
    listOfUniqueClasses.sort()
    return listOfUniqueClasses

"""
Create the structure to store the classes, returns empty structure (List of List)
"""
def createClassInstanceList(list):
    newList = []
    for i in list:    
        newList.append([])
    return newList

"""
Returns the populated list of a list 
"""
def populateInstanceLists(lists, file):
    # start the file from beginning again
    file.seek(0)
    for line in file:
        classInstance = getClass(line)
        i = 0
        # find which class the line belongs in
        # put the class in the appropriate index
        # ie, class 0 == index 0
        while i < len(lists):
            if classInstance == str(i):
                lists[i].append(line)
            i += 1
    return lists
    
"""
Returns a list of the count of instances in
each class
"""
def countClassInstances(classes):
    result = []
    print("Class Counts:")
    for index, aClass in enumerate(classes):
        result.append(len(aClass))
        print("\tClass: ", index, len(aClass))
    return result

"""
Returns the index and count of the smallest class
"""
def getIndexOfSmallestClass(list):
    minimumCount = min(list)
    for index, count in enumerate(list):
        if count == minimumCount:
            print("\nMinimum Count Class:\n","\tCount: ", count, "\n\tIndex: ", index)
            return index, count

"""
For every class larger than the smallest class,
create a random subset where that subsets size
is equal to the size of the smallest class.
Returns the list of lists of each subset
""" 
def getSubsetLists(list, instances, index):
    random.seed(dt.datetime.now)
    # get the size of the new lists we need to create
    sizeOfNewLists = len(list[index])
    
    # create list of a list to store all the sublist values
    subLists = createClassInstanceList(instances)
    
    # loop through each sublist (initially empty)
    for index, subList in enumerate(subLists):
        # while the subList is not sufficiently large
        while len(subList) < sizeOfNewLists:
            # if the original list we are pulling 
            # values from is empty, continue
            if len(list[index]) < 1:
                continue                
            # otherwise, retrieve a random sample 
            else:
                randIndex = random.randint(0, len(list[index]) - 1)
                randomSample = list[index].pop(randIndex)
                subList.append(randomSample)
    return subLists
"""
Write a new map file with subsets complete
"""
def writeNewMap(lists):
    with open("NewMap.RGB.txt", 'w') as file:
        for list in lists:
            for item in list:
                file.write(item)
    print("\nMap File written")

if __name__ == '__main__':
    
    # Open file for reading
    with open(MAPFILE, 'r') as mapFile:
        
        # create an empty list based on the number of classes in the file
        instanceList = createClassInstanceList(createUniqueClasses(mapFile))
        
        # Seperate each class into their own list. The index of this list 
        # corresponds to the class. ie at classesSeperated[1] is a list
        # of all the maps to the images of class 1
        classesSeperatedList = populateInstanceLists(instanceList, mapFile)
        
        # display the count of each image
        countOfInstancesOfEachClass = countClassInstances(classesSeperatedList)
        
        # get the index of the smallest class
        idx, count = getIndexOfSmallestClass(countOfInstancesOfEachClass)
        # create the subsets
        subLists = getSubsetLists(classesSeperatedList, instanceList, idx)
        
        # write the new file
        writeNewMap(subLists)
    
    