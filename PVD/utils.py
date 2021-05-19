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

import math
import time

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

# Split array of pixel values into nested: [[1,2],[3,4],[5,6],[7,8]] --> [[[1,2],[3,4]],[[5,6],[7,8]]]
def groupImagePixels(imagePixels, pixelMatrixWidth):
    for i in range(0, len(imagePixels), pixelMatrixWidth): 
        yield imagePixels[i : i + pixelMatrixWidth]

# Note: this function is only for dev atm
def pixelArrayToMatrix(loadedImage, pixelMatrix, channels):
    # # Dev code for printing original, un-zig-zagged array of pixel values

    # imagePixels = list(loadedImage.getdata())
    # index = 0
    # for i in range(pixelMatrix.height):
    #     for j in range(pixelMatrix.width):
    #         pixelMatrix[i][j] = list(imagePixels[index])[0:3]
    #         index += 1
    # printMatrix(pixelMatrix)
    # print()


    # Horizontally zig-zag through matrix
    # Split array of pixel values into nested: [[1,2],[3,4],[5,6],[7,8]] --> [[[1,2],[3,4]],[[5,6],[7,8]]]
    # Size of chunk depends on width of image

    imagePixels = list(groupImagePixels(list(loadedImage.getdata()), pixelMatrix.width))
    for row in range(pixelMatrix.height):
        if row % 2 == 0:
            # Even row of pixels, maintain order
            for column in range(pixelMatrix.width):
                pixelMatrix[row][column] = list(imagePixels[row][column])[0:channels]
        else:
            # Odd row of pixels, reverse order
            for column in range(pixelMatrix.width-1, -1, -1):
                # pixelMatrix.width-column-1 represents distance from "right edge" of matrix
                pixelMatrix[row][pixelMatrix.width-column-1] = list(imagePixels[row][column])[0:channels]

    return pixelMatrix

def pixelArrayToZigZag(loadedImage, pixelMatrix, channels, groupings):
    # Horizontally zig-zag through matrix
    # Then, split array of pixel values into nested pairs
    # ex: [[1, 2, 3, 4], [5, 6, 7, 8]] --> [ [[1,2],[3,4]], [[8,7],[6,5]] ]

    # Size of chunk depends on width of image
    if isinstance(loadedImage, list): 
        imagePixels = loadedImage
    else:
        imagePixels = list(groupImagePixels(list(loadedImage.getdata()), pixelMatrix.width))
    zigZaggedPixels = []
    for row in range(pixelMatrix.height):
        if row % 2 == 0:
            # Even row of pixels, maintain order
            for column in range(pixelMatrix.width):
                if channels != 1:
                    zigZaggedPixels += [list(imagePixels[row][column])[0:channels]]
                else:
                    zigZaggedPixels += [imagePixels[row][column]]
        else:
            # Odd row of pixels, reverse order
            for column in range(pixelMatrix.width-1, -1, -1):
                # pixelMatrix.width-column-1 represents distance from "right edge" of matrix
                if channels != 1:
                    zigZaggedPixels += [list(imagePixels[row][column])[0:channels]]
                else:
                    zigZaggedPixels += [imagePixels[row][column]]

    # Pair pixels
    if groupings == 0:
        return zigZaggedPixels
    else:
        pairedPixels = list(groupImagePixels(zigZaggedPixels, groupings))
        return pairedPixels

def pixelPairEncode(pixelPair, differencePrime, difference):
    m = differencePrime - difference
    if difference % 2 == 0:
        newPixelPair = [pixelPair[0] - math.ceil(m/2),  pixelPair[1] + math.floor(m/2)]
    else:
        newPixelPair = [pixelPair[0] - math.floor(m/2),  pixelPair[1] + math.ceil(m/2)]
    return newPixelPair

def executionTime(function):
	def timedFunction(*args):
		preTime = int(round(time.time() * 1000))
		function(*args)
		postTime = int(round(time.time() * 1000))
		print(f"Time elapsed: {postTime - preTime} ms", end="\n\n")
	return timedFunction