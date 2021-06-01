import math
import time

# Split array of pixel values into nested: [[1,2],[3,4],[5,6],[7,8]] --> [[[1,2],[3,4]],[[5,6],[7,8]]]
def groupImagePixels(imagePixels, imageWidth):
    for i in range(0, len(imagePixels), imageWidth): 
        yield imagePixels[i : i + imageWidth]

def pixelArrayToZigZag(loadedImage, channels, groupings, width="", height="") -> list:
    # Horizontally zig-zag through matrix
    # Then, split array of pixel values into nested pairs
    # ex: [[1, 2, 3, 4], [5, 6, 7, 8]] --> [ [[1,2],[3,4]], [[8,7],[6,5]] ]

    # Size of chunk depends on width of image
    if isinstance(loadedImage, list): 
        imagePixels = loadedImage
        if width == "" or height == "":
            raise Exception("When providing an image in nested list form, width and height must be provided") 
    else:
        width = loadedImage.size[0]
        height = loadedImage.size[1]
        imagePixels = list(groupImagePixels(list(loadedImage.getdata()), width))
    zigZaggedPixels = []
    for row in range(height):
        if row % 2 == 0:
            # Even row of pixels, maintain order
            for column in range(width):
                if channels != 1:
                    zigZaggedPixels += [list(imagePixels[row][column])[0:channels]]
                else:
                    zigZaggedPixels += [imagePixels[row][column]]
        else:
            # Odd row of pixels, reverse order
            for column in range(width-1, -1, -1):
                # width-column-1 represents distance from "right edge" of matrix
                if channels != 1:
                    zigZaggedPixels += [list(imagePixels[row][column])[0:channels]]
                else:
                    zigZaggedPixels += [imagePixels[row][column]]

    # Group pixels
    if groupings == 0:
        return zigZaggedPixels
    else:
        pairedPixels = list(groupImagePixels(zigZaggedPixels, groupings))
        return pairedPixels

def pixelPairEncode(pixelPair, differencePrime, difference) -> list:
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

def validateQuantization(quantizationWidths: list=[], verbose: bool=False):
    if quantizationWidths == []:
        quantizationWidths = [
                            [0,1], [2,3], [4,7], [8,11], [12,15], [16,23], [24,31], [32,47], 
                            [48,63], [64,95], [96,127], [128,191], [192,255]
                            ]
        if verbose:
            print("Verbose message: no quantization widths provided, using the default values")

        return quantizationWidths
    else:
        # Check validity of quantization widths argument
        valuesCovered = set()
        for quantizationWidth in quantizationWidths:
            # Ensure each width is of size one less than a power of 2
            log = math.log(quantizationWidth[1] - quantizationWidth[0] + 1, 2)
            if math.ceil(log) != math.floor(log):
                raise Exception(f"Width of each quantization must be one less than a power of 2 (found width of {quantizationWidth[1] - quantizationWidth[0] + 1} instead)")

            # Ensure no widths overlap
            quantizationWidthSet = range(quantizationWidth[0], quantizationWidth[1] + 1)
            if list(set.intersection(valuesCovered, quantizationWidthSet)) == []:
                # Ranges don't overlap, merge with previously covered values
                valuesCovered = set.union(valuesCovered, quantizationWidthSet)
            else:
                # Ranges overlap
                raise Exception("Quantization ranges must not overlap")
            
        # Test to ensure ranges cover all values 0 to 255
        if valuesCovered != set(range(0,256)):
            expectedVals = set(range(0,256))
            missing = list(expectedVals - valuesCovered)
            extra = list(valuesCovered - expectedVals)
            if missing != [] and extra != []:
                builtText = f"(missing items {missing} and found extra items {extra} instead)"
            elif missing == []:
                builtText = f"(found extra items {extra} instead)"
            else:
                builtText = f"(missing items {missing} instead)"
            
            raise Exception(f"Quantization ranges must cover all values from 0 to 255 and no more {builtText}")

    return quantizationWidths

def validateTraversal(traversalOrder: list=[], verbose: bool=False):
    # Check validity of traversal order argument
    if traversalOrder == []:
        traversalOrder = [1,3,5,2,4,6]
        if verbose:
            print("Verbose message: no traversal order provided, using the default value")

        return traversalOrder
    elif len(traversalOrder) != 6:
        raise Exception("Traversal order must be of length 6")
    
    # Check traversal order for non-integer values
    for order in traversalOrder:
        if isinstance(order, int) == False:
            try:
                traversalOrder[traversalOrder.index(order)] = int(order)
            except:
                raise Exception(f"Traversal order must contain integer values (found {type(order)} at index {traversalOrder.index(order)} instead)")

    # Ensure traversal order is a list of consecutive numbers
    if sorted(traversalOrder) == list(range(min(traversalOrder), max(traversalOrder)+1)):
        raise Exception("Traversal order must be comprised of consecutive integers e.g. [1,3,5,2,4,6]")

    return traversalOrder


from PIL.PngImagePlugin import PngImageFile
import PIL

def getMaxStorage(loadedImage: PIL.PngImagePlugin.PngImageFile, quantizationWidths: list=[],
                    traversalOrder: list=[], verbose: bool=False):
    """
    This function calculates the maximum number of storable bits in a an image file, given 
    a traversal order (for RGB images) and quantization widths.
    """
    quantizationWidths = validateQuantization(quantizationWidths, verbose)
    traversalOrder = validateTraversal(traversalOrder, verbose)

    storableCount = 0
    if "RGB" in loadedImage.mode.upper():
        pixelPairs = pixelArrayToZigZag(loadedImage, 3, 2)
        currentPairCounter = 0
        for pixelPair in pixelPairs:
            currentPairCounter += 1
            if len(pixelPair) == 2:
                # Flatten pixel pair array into un-nested list
                pixelArray = [pixel for pair in pixelPair for pixel in pair]

                # Sort pixel array given traversal order and group into calculation ready pairs
                pixelIndicesDict = dict(sorted(dict(zip(traversalOrder, pixelArray)).items()))
                traversedPixelPairs = list(groupImagePixels(list(pixelIndicesDict.values()), 2))

                currentTraversedCounter = 0
                for traversedPixelPair in traversedPixelPairs:
                    currentTraversedCounter += 1
                    # d value
                    difference = traversedPixelPair[1] - traversedPixelPair[0]

                    # Determine number of bits storable between pixels
                    for width in quantizationWidths:
                        if width[0] <= abs(difference) <= width[1]:
                            lowerBound = width[0]
                            upperBound = width[1]
                            break
                    
                    # Falling-off-boundary check; ensure 0 < calculated pixel value < 255
                    testingPair = pixelPairEncode(traversedPixelPair, upperBound, difference)
                    if testingPair[0] < 0 or testingPair[1] < 0 or testingPair[0] > 255 or testingPair[1] > 255:
                        # One of the values "falls-off" the range from 0 to 255 and hence is invalid
                        if verbose == True:
                            print(f"Verbose message: channel pair number {currentTraversedCounter} in pixel pair number {currentPairCounter} has the possibility of falling off; skipping")
                    else:
                        # Passes the check, continue with decoding
                        # Number of storable bits between two pixels
                        storableCount += int(math.log(upperBound - lowerBound + 1, 2))
    elif loadedImage.mode.upper() == "L":
        pixelPairs = pixelArrayToZigZag(loadedImage, 1, 2)

        currentPairCounter = 0
        for pixelPair in pixelPairs:
            currentPairCounter += 1
            if len(pixelPair) == 2:
                difference = pixelPair[1] - pixelPair[0]

                # Determine number of bits storable between pixels
                for width in quantizationWidths:
                    if width[0] <= abs(difference) <= width[1]:
                        lowerBound = width[0]
                        upperBound = width[1]
                        break
                
                # Falling-off-boundary check; ensure 0 < calculated pixel value < 255
                testingPair = pixelPairEncode(pixelPair, upperBound, difference)
                if testingPair[0] < 0 or testingPair[1] < 0 or testingPair[0] > 255 or testingPair[1] > 255:
                    # One of the values "falls-off" the range from 0 to 255 and hence is invalid
                    if verbose == True:
                        print(f"Verbose message: pixel pair number {currentPairCounter} has the possibility of falling off; skipping")
                else:
                    # Passes the check, continue with decoding
                    # Number of storable bits between two pixels
                    storableCount += int(math.log(upperBound - lowerBound + 1, 2))

    power = 1024
    counter = 0
    labels = {0 : "", 1: "kilo", 2: "mega", 3: "giga", 4: "tera", 5:"peta"}
    while storableCount > power:
        storableCount /= power
        counter += 1
    return round(storableCount, 2), labels[counter]+"bits"
