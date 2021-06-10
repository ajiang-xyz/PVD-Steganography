##################################################################################################################
##################################################################################################################
##################################################################################################################

# This file is for keeping any deprecated functions / chunks of code / explanations / etc
# that I might reuse in the future.

##################################################################################################################
##################################################################################################################
##################################################################################################################

# (50, 65) <-- gray values of a pixel pair

# d is the absolute value of their difference:

# d = abs(50-65) = 15

# determine which range it falls into:
# [0,7], [8,15], [16,31], [32,63], [64,127], [128,255] (more noticeable, more data)
# or
# [0,2], [3,5], [6,10], [11,15], [16,20], [21,29], [30,38], [39,53], [54,60], [61,93], [94,126], [127,191], [192,255] (less noticeable, less data)

# l is the lower bound of this range and u is the upper bound

# determine number of bits this range corresponds to (log base 2 of the width of the range),
# then pull that many bits from the stream of secret message

# binary value is given the decimal value of these bits

# d prime is given by
# { lower bound + binary value     for d >= 0
# { -(lower bound + binary value)  for d <0

# calculating the values of the pixels after inverted differencing:

# { (pixeli - ceiling(d prime - d ), pixel(i+1) + floor(d prime - d))  if d is odd
# { (pixeli - floor(d prime - d ), pixel(i+1) + ceiling(d prime - d))  if d is even

##################################################################################################################
##################################################################################################################
##################################################################################################################

# Matrix object that stores structures in a nested list format
class Matrix(object):
    def __init__(self, height, width=None, default=0):
        self.height = height
        self.width = height if width == None else width
        self.matrix = []
        for i in range(self.height):
            self.matrix.append([default for j in range(self.width)])

    def __getitem__(self, index):
        return self.matrix[index]

    # Copy function that returns a new, equal object of original 
    def copy(self):
        copyMatrix = Matrix(self.height, self.width)
        for i in range(self.height):
            for j in range(self.width):
                copyMatrix[i][j] = self.matrix[i][j]
        return copyMatrix

def printMatrix(matrix):
    for row in range(matrix.height):
        for column in range(matrix.width):
            print(matrix[row][column], end=" ")
        print("")

# from PIL.PngImagePlugin import PngImageFile, PngInfo
from loguru import logger
import imghdr
import os

# Function to help user select file
@logger.catch
def promptPath():
    # Array of types of supported images
    imageTypes = ["png"]

    # Get all files and directores in CWD
    currentWorkingDirectory = os.getcwd()
    files = [file for file in os.listdir(currentWorkingDirectory) if os.path.isfile(os.path.join(currentWorkingDirectory, file))]
    directories = [folder for folder in os.listdir(currentWorkingDirectory) if os.path.isdir(os.path.join(currentWorkingDirectory, folder))]
    
    # Include files only if they're images
    imageFiles = []
    for file in files:
        if imghdr.what(file) in imageTypes:
            imageFiles.append(file)

    # Include directories only if they're readable
    readableDirectories = []
    for directory in directories:
        if os.access(directory, os.R_OK) == True:
            readableDirectories.append(directory)

    # Display neatly
    print(f"Supported images in current directory \"{currentWorkingDirectory}\":")
    for imageFile in imageFiles:
        print(imageFile)
    print()

    return False

from PIL.PngImagePlugin import PngImageFile, PngInfo

# Edit PNG metadata to include fingerprint of this PVD algorithm
modifyMetadata = PngImageFile("outCopy.png")
metadata = PngInfo()
metadata.add_text("46", "209")
modifyMetadata.save("outCopy.png", pnginfo=metadata)

testEncoded = PngImageFile("./outCopy.png")
print(testEncoded.text)