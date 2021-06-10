from PIL.PngImagePlugin import PngImageFile, PngInfo
from utils import *
import numpy as np
import itertools
import PIL
import os

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

    print()

    if message == "":
        if verbose:
            print("Verbose message: no message given, assuming retrieval of message")

    quantizationWidths = validateQuantization(quantizationWidths, verbose)

    print()

    pixelPairs = pixelArrayToZigZag(loadedImage, 1, 2)

    # If function is run without message, assume retrieval of message
    if message == "":
        print(f"Retrieving binary from file \"{loadedImage.filename}\"")
        print()

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
        print(f"Encoding binary \"{message}\" into file \"{loadedImage.filename}\"")
        print()

        # Encoding function
        newPixels = []

        # Get binary of message
        messageBinary = "0" + str(bin(int.from_bytes(message.encode(), "big")))[2:]
        currentMessageIndex = 0

        for pixelPair in pixelPairs:
            if len(pixelPair) == 2 and currentMessageIndex < len(messageBinary):
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
            print(f"Warning: only encoded {len(messageBinary[0:currentMessageIndex])} of {len(messageBinary)} bits ({round(100*len(messageBinary[0:currentMessageIndex])/len(messageBinary), 2)}%)")
            print(f"Original message: {message}")
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