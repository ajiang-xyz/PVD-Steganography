from PIL.PngImagePlugin import PngImageFile, PngInfo
from utils import *
import numpy as np
import itertools
import math
import PIL
import os

def rgbChannels(loadedImage: PIL.PngImagePlugin.PngImageFile, message: str="", quantizationWidths: list=[],
                    traversalOrder: list=[], verbose: bool=False):

    """
    This function takes takes an image of the form
    [
        [<RGB 1>, <RGB 2>, <RGB 3>, ... ],
        [<RGB a>, <RGB a+1>, <RGB a+2>, ... ],
        [<RGB b>, <RGB b+1>, <RGB b+2>, ... ],
        ...
    ]
    where RGB <index> is of the form [R, G, B] (if there is an Alpha channel present, it is ignored)

    And utilizes a modified version Wu and Tsai's algorithm to encode a message into this nested array structure.

    Because this image is RGB, an order of traversal is needed to ensure the correct encoding/retrieval order 
    while traversing the structure.
    
    Define a general pair of RGB pixels as [[R1, G1, B1], [R2, G2, B2]] and flatten it into [R1, G1, B1, R2, G2, B2]
    The traversal order is an array of that maps the corresponding value to a location it should be sorted to. 
    After mapping and sorting the pixel values, pair adjacent pixels 

    For example, a possible traversal order is the standard [1, 3, 5, 2, 4, 6]
    Applying this traversal order concept to the RGB pixel pair 
    [[185, 75, 250], [255, 80, 200]] 
    results in these encodable groups of values:
    [[185, 255], [75, 80], [250, 200]]
    """

    if message == "":
        if verbose:
            print("Verbose message: no message given, assuming retrieval of message")

    quantizationWidths = validateQuantization(quantizationWidths, True)
    traversalOrder = validateTraversal(traversalOrder, True)

    # If there is an Alpha channel present in the image, it is ignored
    pixelPairs = pixelArrayToZigZag(loadedImage, 3, 2)

    # If function is run without message, assume retrieval of message
    if message == "":
        # Retrieval function
        messageBinary = ""

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
                        storableCount = int(math.log(upperBound - lowerBound + 1, 2))
                        
                        # Extract encoded decimal
                        if difference >= 0:
                            retrievedDecimal = difference - lowerBound
                        else:
                            retrievedDecimal = - difference - lowerBound

                        retrievedBinary = bin(retrievedDecimal).replace("0b", "")

                        # Edge case in which embedded data began with 0's
                        if storableCount > len(retrievedBinary):
                            retrievedBinary = "0" * (storableCount-len(retrievedBinary)) + retrievedBinary

                        messageBinary += retrievedBinary

        return messageBinary
    else:
        # Encoding function
        newPixels = []

        # Get binary of message
        messageBinary = "0" + str(bin(int.from_bytes(message.encode(), "big")))[2:]
        currentMessageIndex = 0

        currentPairCounter = 0
        for pixelPair in pixelPairs:
            currentPairCounter += 1
            if len(pixelPair) == 2 and currentMessageIndex < len(messageBinary) - 1:

                # Flatten pixel pair array into un-nested list
                pixelArray = [pixel for pair in pixelPair for pixel in pair]

                # Sort pixel array given traversal order and group into calculation ready pairs
                traversalIndiceDict = list(zip(traversalOrder, [0,1,2,3,4,5]))
                pixelIndicesDict = dict(sorted(dict(zip(traversalIndiceDict, pixelArray)).items()))
                traversedPixelPairs = list(groupImagePixels(list(pixelIndicesDict.values()), 2))

                postEncodingValues = []

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
                        # Append original pixel pair and skip encoding
                        postEncodingValues += traversedPixelPair
                        if verbose:
                            print(f"Verbose message: channel pair number {currentTraversedCounter} in pixel pair number {currentPairCounter} has the possibility of falling off; skipping")
                    else:
                        # Passes the check, continue with encoding
                        # Number of storable bits between two pixels
                        storableCount = int(math.log(upperBound - lowerBound + 1, 2))

                        # Ensure haven't already finished encoding entire message
                        if currentMessageIndex + storableCount <= len(messageBinary):
                            # Encode as normal
                            endIndex = currentMessageIndex+storableCount
                            storableBits = messageBinary[currentMessageIndex:endIndex]
                            currentMessageIndex += storableCount
                        else:
                            if currentMessageIndex == len(messageBinary):
                                # Finished encoding entire message
                                currentMessageIndex = len(messageBinary)
                                postEncodingValues += pixelPair
                                continue
                            else:
                                # Can encode more bits than available, encode what's left
                                storableBits = messageBinary[currentMessageIndex:]

                                # Ensure last bit doesn't get corrupted, fill empty space with 0's
                                storableBits += "0" * (storableCount - len(messageBinary[currentMessageIndex:]))
                                currentMessageIndex = len(messageBinary)

                        # Get value of the chunk of message binary
                        storableBitsValue = int(storableBits, 2)

                        # d' value
                        differencePrime = lowerBound + storableBitsValue if difference >= 0 else -(lowerBound + storableBitsValue)

                        # Calculate new pixel pair
                        newPixelPair = pixelPairEncode(traversedPixelPair, differencePrime, difference)                    
                        postEncodingValues += newPixelPair
                
                # Flatten encoded value pair array into un-nested list
                # pixelArray = [pixel for pair in postEncodingValues for pixel in pair]

                # Un-sort pixel array given traversal order and group into calculation original RGB channels
                # pixelIndicesDict = dict(sorted(dict(zip(traversalIndiceDict, postEncodingValues)).items()))
                pixelIndicesDict = dict(sorted(dict(zip([ key[1] for key in pixelIndicesDict.keys() ], postEncodingValues)).items()))
                reversedPaired = list(groupImagePixels([pixel for pixel in pixelIndicesDict.values()], 3))

                newPixels += reversedPaired

                print(pixelPair)
                print(reversedPaired)
            else:
                # For case in which there's an odd number of pixels; append lone pixel value
                newPixels += pixelPair

        returnValue = True
        if currentMessageIndex != len(messageBinary):
            print(f"Warning: only {len(messageBinary[0:currentMessageIndex])} of {len(messageBinary)} bits encoded")
            print(f"\nOriginal message: {message}")
            returnValue = False

            # Verbose errors
            if verbose == True:
                # Underline section of binary that was encoded
                # Get max printable width in current terminal
                width = os.get_terminal_size()[0]
                
                # Create array groupings of message lines and underlinings
                printableMessageLines = list(groupImagePixels(messageBinary, width))
                printableUnderlinings = list(groupImagePixels("~"*len(messageBinary[0:currentMessageIndex]), width))

                # Zip and print
                print("\nVerbose warning: only encoded underlined section of message:")
                for printableMessageLine, printableUnderlining in itertools.zip_longest(printableMessageLines, printableUnderlinings, fillvalue=""):
                    print(f"{printableMessageLine}")
                    if printableUnderlining:
                        print(f"{printableUnderlining}")

        # Create new image structure, save file
        newPixels = list(groupImagePixels(newPixels, loadedImage.size[0]))
        newPixels = pixelArrayToZigZag(newPixels, 1, loadedImage.size[0], loadedImage.size[0], loadedImage.size[1])
        array = np.array(newPixels, dtype=np.uint8)
        savedImage = PIL.Image.fromarray(array)
        savedImage.save('./IO/outColor.png')

        return returnValue

def singleChannel(loadedImage: PIL.PngImagePlugin.PngImageFile, message: str="", 
                 quantizationWidths: list=[], verbose: bool=False):

    """
    This function takes takes an image of the form
    [
        [<1>, <2>, <3>, ... ],
        [<a>, <a+1>, <a+2>, ... ],
        [<b>, <b+1>, <b+2>, ... ],
        ...
    ]
    And utilizes Wu and Tsai's algorithm to encode a message into this nested array structure.
    """

    if message == "":
        if verbose:
            print("Verbose message: no message given, assuming retrieval of message")

    quantizationWidths = validateQuantization(quantizationWidths, True)

    pixelPairs = pixelArrayToZigZag(loadedImage, 1, 2)

    # If function is run without message, assume retrieval of message
    if message == "":
        # Retrieval function
        messageBinary = ""

        for pixelPair in pixelPairs:
            if len(pixelPair) == 2:
                # d value
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
                        print(f"Verbose message: pixel pair number {pixelPairs.index(pixelPair)} had the possibility of falling off and was skipped during the encoding process")
                else:
                    # Passes the check, continue with decoding
                    # Number of storable bits between two pixels
                    storableCount = int(math.log(upperBound - lowerBound + 1, 2))
                    
                    # Extract encoded decimal
                    if difference >= 0:
                        retrievedDecimal = difference - lowerBound
                    else:
                        retrievedDecimal = - difference - lowerBound

                    retrievedBinary = bin(retrievedDecimal).replace("0b", "")

                    # Edge case in which embedded data began with 0's
                    if storableCount > len(retrievedBinary):
                        retrievedBinary = "0" * (storableCount-len(retrievedBinary)) + retrievedBinary

                    messageBinary += retrievedBinary

        return messageBinary
    else:
        # Encoding function
        newPixels = []

        # Get binary of message
        messageBinary = "0" + str(bin(int.from_bytes(message.encode(), "big")))[2:]
        currentMessageIndex = 0

        for pixelPair in pixelPairs:
            if len(pixelPair) == 2 and currentMessageIndex < len(messageBinary) - 1:
                # d value
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
                    # Append original pixel pair and skip encoding
                    newPixels += pixelPair
                    if verbose:
                        print(f"Verbose message: pixel pair number {pixelPairs.index(pixelPair)} has the possibility of falling off; skipping")
                else:
                    # Passes the check, continue with encoding
                    # Number of storable bits between two pixels
                    storableCount = int(math.log(upperBound - lowerBound + 1, 2))

                    # Ensure haven't already finished encoding entire message
                    if currentMessageIndex + storableCount <= len(messageBinary):
                        # Encode as normal
                        endIndex = currentMessageIndex+storableCount
                        storableBits = messageBinary[currentMessageIndex:endIndex]
                        currentMessageIndex += storableCount
                    else:
                        if currentMessageIndex == len(messageBinary):
                            # Finished encoding entire message
                            currentMessageIndex = len(messageBinary)
                            newPixels += pixelPair
                            continue
                        else:
                            # Can encode more bits than available, encode what's left
                            storableBits = messageBinary[currentMessageIndex:]

                            # Ensure last bit doesn't get corrupted, fill empty space with 0's
                            storableBits += "0" * (storableCount - len(messageBinary[currentMessageIndex:]))
                            currentMessageIndex = len(messageBinary)

                    # Get value of the chunk of message binary
                    storableBitsValue = int(storableBits, 2)

                    # d' value
                    differencePrime = lowerBound + storableBitsValue if difference >= 0 else -(lowerBound + storableBitsValue)

                    # Calculate new pixel pair
                    newPixelPair = pixelPairEncode(pixelPair, differencePrime, difference)                    
                    newPixels += newPixelPair

            else:
                # For case in which there's an odd number of pixels; append lone pixel value
                newPixels += pixelPair

        returnValue = True
        if currentMessageIndex != len(messageBinary):
            print(f"Warning: only {len(messageBinary[0:currentMessageIndex])} of {len(messageBinary)} bits encoded")
            print(f"\nOriginal message: {message}")
            returnValue = False

            # Verbose errors
            if verbose == True:
                # Underline section of binary that was encoded
                # Get max printable width in current terminal
                width = os.get_terminal_size()[0]
                
                # Create array groupings of message lines and underlinings
                printableMessageLines = list(groupImagePixels(messageBinary, width))
                printableUnderlinings = list(groupImagePixels("~"*len(messageBinary[0:currentMessageIndex]), width))

                # Zip and print
                print("\nVerbose warning: only encoded underlined section of message:")
                for printableMessageLine, printableUnderlining in itertools.zip_longest(printableMessageLines, printableUnderlinings, fillvalue=""):
                    print(f"{printableMessageLine}")
                    if printableUnderlining:
                        print(f"{printableUnderlining}")

        # Create new image structure, save file
        newPixels = list(groupImagePixels(newPixels, loadedImage.size[0]))
        newPixels = pixelArrayToZigZag(newPixels, 1, loadedImage.size[0], loadedImage.size[0], loadedImage.size[1])
        array = np.array(newPixels, dtype=np.uint8)
        savedImage = PIL.Image.fromarray(array)
        savedImage.save('./IO/out.png')

        return returnValue

@executionTime
def main():
    print("Beginning execution...")
    imagePath = "./IO/outColor.png"
    loadedImage = PIL.Image.open(imagePath)

    # 24-bit RGB image; ignores Alpha channel
    if "RGB" in loadedImage.mode.upper():
        returnValue = rgbChannels(loadedImage, traversalOrder=[], verbose=True)
    
    # 8-bit Black & White image
    elif loadedImage.mode.upper() == "L":
        returnValue = singleChannel(loadedImage, message="hi", verbose=True)
    else:
        raise Exception(f"The image located at {imagePath} is not in a supported format.")

    # Parse function return
    print()
    if isinstance(returnValue, bool):
        if returnValue == True:
            print("Done.")
        else:
            print("Completed with errors.")
    else:
        print(f"Retrieved binary: {returnValue}")

if __name__ == "__main__":
    main()