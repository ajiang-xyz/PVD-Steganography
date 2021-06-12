from PIL.PngImagePlugin import PngImageFile, PngInfo
from utils import *
import numpy as np
import itertools
import PIL
import os

def rgbChannels(loadedImage: PIL.PngImagePlugin.PngImageFile, message: str="", quantizationWidths: list=[],
                    traversalOrder: list=[], verify: bool=False, verbose: bool=False):

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

    # Verify image data
    if verify:
        print("Beginning verification...")
        if message == "":
            verificationData = loadedImage.text["png:fingerprint"].split(":")
            imageWidth, imageHeight = rosenburgStrongPairing(int(verificationData[0]), reverse=True)
            bitLength, messageHash = retrieveLength(verificationData[1])

            # Image dimensions are incorrect
            if loadedImage.size[0] != imageWidth or loadedImage.size[1] != imageHeight:
                raise Exception(f"Image verification failed. Image dimensions don't match encoded verification data.")

            # Execute function without verifying data option
            retrievedBinary = rgbChannels(loadedImage, message, quantizationWidths, traversalOrder, verbose=verbose)
            
            # Ensure entire message was encoded
            if len(retrievedBinary) >= bitLength:
                retrievedBinary = retrievedBinary[:bitLength]

                # Ensure hashes match
                if hashlib.sha256(retrievedBinary.encode()).hexdigest() == messageHash:
                    print("\nVerified.")
                    return retrievedBinary
                else:
                    raise Exception(f"Message verification failed. Hash of retrieved binary doesn't match encoded verification data.")
            raise Exception("Message verification failed. Length of retrieved message binary doesn't match encoded verification data.")
        else:
            # Get binary of message
            if sorted(set(message)) == ["0", "1"]:
                messageBinary = message
            else:
                messageBinary = "0" + str(bin(int.from_bytes(message.encode(), "big")))[2:]
                
            returnValue = rgbChannels(loadedImage, messageBinary, quantizationWidths, traversalOrder, verbose=verbose)

            # Build verification data to place in loaded image properties
            verificationBuilder = ""
            verificationBuilder += f"{str(rosenburgStrongPairing([loadedImage.size[0], loadedImage.size[1]]))}:"
            verificationBuilder += f"{embedLength(str(len(messageBinary)), messageBinary)}"

            # Edit PNG metadata to include fingerprint of this PVD algorithm
            modifyMetadata = PngImageFile("./IO/outColor.png")
            metadata = PngInfo()
            metadata.add_text("png:fingerprint", f"{verificationBuilder}")
            modifyMetadata.save("./IO/outColor.png", pnginfo=metadata)

            print("\nVerified.")
            return returnValue

    print()

    if message == "":
        if verbose:
            print("Verbose message: no message given, assuming retrieval of message")
    else:
        # Get binary of message
        if sorted(set(message)) == ["0", "1"]:
            messageBinary = message
            if verbose:
                print("Verbose message: message contains only binary values, assuming binary message")
        else:
            messageBinary = "0" + str(bin(int.from_bytes(message.encode(), "big")))[2:]
            if verbose:
                print("Verbose message: message contains non-binary values, assuming ascii message")

    quantizationWidths = validateQuantization(quantizationWidths, verbose)
    traversalOrder = validateTraversal(traversalOrder, verbose)

    print()

    # If there is an Alpha channel present in the image, it is ignored
    pixelPairs = pixelArrayToZigZag(loadedImage, 3, 2)

    # If function is run without message, assume retrieval of message
    if message == "":
        print(f"Retrieving binary from file \"{loadedImage.filename}\"")
        print()

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
                            print(f"Verbose message: channel pair number {currentTraversedCounter} in pixel pair number {currentPairCounter} has the possibility of falling off, skipping")
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
        print(f"Encoding binary \"{messageBinary}\" into file \"{loadedImage.filename}\"")
        print()

        # Encoding function
        newPixels = []

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
                            print(f"Verbose message: channel pair number {currentTraversedCounter} in pixel pair number {currentPairCounter} has the possibility of falling off, skipping")
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
                                postEncodingValues += traversedPixelPair
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

                # Un-sort pixel array given traversal order and group into calculation original RGB channels
                pixelIndicesDict = dict(sorted(dict(zip([ key[1] for key in pixelIndicesDict.keys() ], postEncodingValues)).items()))
                reversedPaired = list(groupImagePixels([pixel for pixel in pixelIndicesDict.values()], 3))

                newPixels += reversedPaired
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
        savedImage.save('./IO/outColor.png')

        return returnValue