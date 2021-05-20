from PIL.PngImagePlugin import PngImageFile, PngInfo
from loguru import logger
from PIL import Image
from utils import *
import numpy as np
import itertools
import imghdr

import math
import os

# PVD algorithm variant on images with RGB channels (ignores Alpha channel if present) 
def rgbChannels(loadedImage, message="", variant=""):
    if message == "":
        # Decoding function here
        pass
    else:
        # Encoding function
        pixelPairs = pixelArrayToZigZagPairs(loadedImage, 3)
        print(pixelPairs)

# PVD algorithm on images with 8-bit B&W channel
def singleChannel(loadedImage, message="", verbose=False):
    quantizationWidths = [
                        [0,1], [2,3], [4,7], [8,11], [12,15], [16,23], [24,31], [32,47], 
                        [48,63], [64,95], [96,127], [128,191], [192,255]
                        ]
    pixelPairs = pixelArrayToZigZag(loadedImage, 1, 2)

    # If function is run without message, assume retrieval of message
    if message == "":
        # Retrieval function
        print("Beginning retrieval...")
        messageBinary = ""

        for pixelPair in pixelPairs:
            if len(pixelPair) == 2:
                # d value
                difference = pixelPair[1] - pixelPair[0]

                # Determine number of bits storable between pixels
                for width in quantizationWidths:
                    if width[0] <= difference <= width[1]:
                        lowerBound = width[0]
                        upperBound = width[1]
                        break
                
                # Falling-off-boundary check; ensure 0 < calculated pixel value < 255
                testingPair = pixelPairEncode(pixelPair, upperBound, difference)
                if testingPair[0] < 0 or testingPair[1] < 0 or testingPair[0] > 255 or testingPair[1] > 255:
                    # One of the values "falls-off" the range from 0 to 255 and hence is invalid
                    if verbose == True:
                        print(f"Notice: pixel pair number {pixelPairs.index(pixelPair)} had the possibility of falling off and was skipped during the encoding process")
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
        print("Beginning encoding...")
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
                    if width[0] <= difference <= width[1]:
                        lowerBound = width[0]
                        upperBound = width[1]
                        break
                
                # Falling-off-boundary check; ensure 0 < calculated pixel value < 255
                testingPair = pixelPairEncode(pixelPair, upperBound, difference)
                if testingPair[0] < 0 or testingPair[1] < 0 or testingPair[0] > 255 or testingPair[1] > 255:
                    # One of the values "falls-off" the range from 0 to 255 and hence is invalid
                    # Append original pixel pair and skip encoding
                    print(f"Warning: pixel pair number {pixelPairs.index(pixelPair)} has the possibility of falling off; skipping")
                    newPixels += pixelPair
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
                print("\nWarning: only encoded underlined section of message:")
                for printableMessageLine, printableUnderlining in itertools.zip_longest(printableMessageLines, printableUnderlinings, fillvalue=""):
                    print(f"{printableMessageLine}")
                    if printableUnderlining:
                        print(f"{printableUnderlining}")

        # Create new image structure, save file
        newPixels = list(groupImagePixels(newPixels, loadedImage.size[0]))
        newPixels = pixelArrayToZigZag(newPixels, 1, loadedImage.size[0], loadedImage.size[0], loadedImage.size[1])
        array = np.array(newPixels, dtype=np.uint8)
        savedImage = Image.fromarray(array)
        savedImage.save('./IO/out.png')

        return returnValue

# # Function to help user select file
# @logger.catch
# def promptPath():
#     # Array of types of supported images
#     imageTypes = ["png"]

#     # Get all files and directores in CWD
#     currentWorkingDirectory = os.getcwd()
#     files = [file for file in os.listdir(currentWorkingDirectory) if os.path.isfile(os.path.join(currentWorkingDirectory, file))]
#     directories = [folder for folder in os.listdir(currentWorkingDirectory) if os.path.isdir(os.path.join(currentWorkingDirectory, folder))]
    
#     # Include files only if they're images
#     imageFiles = []
#     for file in files:
#         if imghdr.what(file) in imageTypes:
#             imageFiles.append(file)

#     # Include directories only if they're readable
#     readableDirectories = []
#     for directory in directories:
#         if os.access(directory, os.R_OK) == True:
#             readableDirectories.append(directory)

#     # Display neatly
#     print(f"Supported images in current directory \"{currentWorkingDirectory}\":")
#     for imageFile in imageFiles:
#         print(imageFile)
#     print()

#     return False

# Driver function
@executionTime
def main():
    loadedImage = Image.open("./IO/in.png")

    # 24-bit RGB image; ignores Alpha channel
    if "RGB" in loadedImage.mode.upper():
        rgbChannels(loadedImage)
    
    # 8-bit Black & White image
    if loadedImage.mode.upper() == "L":
        returnValue = singleChannel(loadedImage, message="hi", verbose=True)
        print()

        # Parse function return
        if isinstance(returnValue, bool):
            if returnValue == True:
                print("Done.")
            else:
                print("Completed with errors.")
        else:
            print(f"Retrieved binary: {returnValue}")

if __name__ == "__main__":
    main()