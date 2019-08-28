"""
Created on Fri Aug 16 09:47:57 2019

@author: brad.crump

Script converts and crops data, in future, add the option to not crop data.

Assumes that the input image contains "RGB" and "png".

Still from a naive approach, but has potential to be further generalized.
Use case:
    If data has a substantial black background, this script can lessen the black 
    background. It also writes out a test and train map file for the images.


 Folder structure:
 present working directory
 |_THIS_SCRIPT
 |
 |_class1
 |	|_FolderOfData1
 |	|_FolderOfData2
 |_class2
 |  |_FolderOfData1
 |	|_FolderOfData2
 |_class3
  
 Will convert data out to classes1_classes2_..._classesN-DayAndTime
 ie: PonderosaPine_SprucePine_2019-8-15-1356
 
"""
import os
import cv2
import time
import argparse

def ConvertAndCrop(cropMargin, testPercent):
    global CROP_MARGIN
    global TEST_SAMPLES
    CROP_MARGIN = cropMargin
    TEST_SAMPLES = testPercent
    ### Generate the new folders where we will write the cropped image data 
    # get the path to the new folder for the data we will convert
    convertedDataFolder = makeDirectoryForConvertedData()
    print("Folder created: " + convertedDataFolder)
    completeMap = open(convertedDataFolder + "\\CompleteMap.RGB.txt", 'w')
    
    # create the subdirectories for each classes
    makeClassDirectories(convertedDataFolder)
    
    print("New Classes directories created")
    print("Converting Has Started...")
    
    convertData(getCurrentDirectory(), convertedDataFolder, completeMap)
    
    completeMap.close()
    
    splitTrainAndTestData(convertedDataFolder, completeMap)
    
    print("Done")
# returns the working directories path
def getCurrentDirectory():
    return os.path.dirname(os.path.realpath(__file__))

"""
    Returns a list of png images with RGB in the name of the image
"""
def getPngs(directory):
    images = []
    # walk the folder
    for root, dirs, files in os.walk(directory, topdown=False):
        # for each file
        for file in files:
            # if the file contains the expected strings
            if ".png" in file and "RGB" in file:
                images.append(root + "\\" +file)
    print("Images retrieved")
    return images
       

"""
    Create a list of all the Classes in this conversion
"""
def getClassList():
    classes = []
    
    # walk the current directory
    for root, dirs, files in os.walk(getCurrentDirectory(), topdown=False):
        
        # Don't store the current directory, only the subdirectories
        if dirs == getCurrentDirectory() or dirs == []:
            continue
        
        # store the directory
        classes.append(dirs)
        
        # Currently doing more work than needed:
        # os.walk inspects all the subdirectories as well, so we are just
        # returning the last index, which is the pwd children
    return classes[len(classes)-1]


"""
    Creates a directory and returns the path
"""
def makeDirectoryForConvertedData():
    # init empty folder name
    folderName = ""
    
    # get the Classes and append them to a string
    for aClass in getClassList():
        folderName = folderName + aClass + "_"
        
    # get the current date and time and append it to the string
    year, month, day, hour, minute = map(int, time.strftime("%Y %m %d %H %M").split())
    now = str(year) + "-" + str(month) + "-" + str(day) + "-" + str(hour) + "" + '{:02d}'.format(minute)
    folderName = folderName + now
    
    # Hard code the location of the new folder in conversions
    path = "C:\\Conversions\\" + folderName
    
    # if the path doesn't exist, write it
    if not os.path.exists(path):
        os.makedirs(path)
    return path

"""
    Create a directory for each class in this conversion
"""
def makeClassDirectories(folder):
    # loop through each class
    for aClass in getClassList():    
        # create a new path for the class
        newDir = folder + "\\" + aClass 
        # if the path doesn't exist, write it
        if not os.path.exists(newDir):
            os.makedirs(newDir)

"""
Converts data 
"""
def convertData(currentDir, convertDir, mapFile):
    
    classMap = 0    
    # Loop through each folder
    for aClass in getClassList():
        
        # create the paths to be used
        currentPath = currentDir + "\\" + aClass
        convertPath = convertDir + "\\" + aClass
        
        # retrieve all the images to be converted
        oldImages = getPngs(currentPath)
        
        # crop and write the images
        cropWriteMapImages(oldImages, convertPath, aClass, mapFile, classMap)
        classMap = classMap + 1
        
        
"""
    Crops and writes the image to the convertPath
"""
def cropWriteMapImages(oldImages, convertPath, aClass, mapFile, classMap):
    # for each old image
    print("Cropping and Writing " + aClass)
    print("This may take some time.")
    i = 0
    for image in oldImages:
        croppedImage = cropImage(image)
        writeImageAndMap(croppedImage, convertPath, aClass, i, mapFile, classMap)
        i = i + 1
    print(aClass + " images have been written and cropped")

"""
    Crops an image, defaults the margin to 5 pixels
"""
def cropImage(image):
    image = cv2.imread(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
    # find the contours of the image (boundary)
    x, contours, hierarchy = cv2.findContours(gray,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
    
    # find the largest contour (outer boundary)
    largestCntArea = 0
    i = 0
    for c in contours:
        # Find the largest contour
        if cv2.contourArea(c) > largestCntArea:
            largestCntArea = cv2.contourArea(c)
            largestCntIndex = i
        i = i + 1
        
    largestContour = contours[largestCntIndex]
    
    # Bounding box for the largest contour
    x, y, w, h = cv2.boundingRect(largestContour)
    
    # add margin (and center)
    h = h + CROP_MARGIN
    w = w + CROP_MARGIN
    x = x - int(CROP_MARGIN/2)
    y = y - int(CROP_MARGIN/2)
    
    # create crop img using the bounding box 
    return image[y:y+h, x:x+w]


"""
    Writes a cropped image to the specified directory
"""
def writeImageAndMap(image, path, aClass, name, mapFile, classMap):
    # build the image name
    imageName = "\\" + aClass + "_" + str(name) + ".RGB.png"
    pathToImage = path + imageName
    cv2.imwrite(pathToImage, image)
    writeCompleteMap(mapFile, aClass, imageName, classMap)

def writeCompleteMap(file, aClass, imageName, classMap):
    file.write("...\\" + aClass + imageName + "\t" + str(classMap) + "\n")

def splitTrainAndTestData(folder, file):
    print("Mapping Test and Train data")
    
    test = open(folder + "\\ValidationMap.RGB.txt", 'w')
    train = open(folder + "\\TrainMap.RGB.txt", 'w')
    testIndex = int(100/TEST_SAMPLES)

    i = 0
    
    with open(str(file.name), 'r') as f:
        for line in f:
            if i % testIndex == 0:
                test.write(line)
            else:
                train.write(line)
            i = i + 1
    print("Closing Files")
    f.close()
    test.close()
    train.close()