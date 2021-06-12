print("Executing...")

import functools
def wrapper(function):
    print(locals())
    @functools.wraps(function)
    def wrappedFunction(*args, **kwargs):
        print("Locals:")
        print(locals())
        return function(*args, **kwargs)
    return wrappedFunction

@wrapper
def testing1(arg1, arg2):
    print(locals())
    return arg1+arg2

print(testing1(1,5))


from utils import groupImagePixels


# pixelPair = [[25,35,45],[50,60,70]]
# traversalOrder = [1,3,5,2,4,6]



# def rgbChannels(loadedImage: PIL.PngImagePlugin.PngImageFile, message: str="", quantizationWidths: list=[],
#                     traversalOrder: list=[], verbose: bool=False):

#     """
#     This function takes takes an image of the form
#     [
#         [<RGB 1>, <RGB 2>, <RGB 3>, ... ],
#         [<RGB a>, <RGB a+1>, <RGB a+2>, ... ],
#         [<RGB b>, <RGB b+1>, <RGB b+2>, ... ],
#         ...
#     ]
#     where RGB <index> is of the form [R, G, B] (if there is an Alpha channel present, it is ignored)

#     And utilizes a modified version Wu and Tsai's algorithm to encode a message into this nested array structure.

#     Because this image is RGB, an order of traversal is needed to ensure the correct encoding/retrieval order 
#     while traversing the structure.
    
#     Define a general pair of RGB pixels as [[R1, G1, B1], [R2, G2, B2]] and flatten it into [R1, G1, B1, R2, G2, B2]
#     The traversal order is an array of that maps the corresponding value to a location it should be sorted to. 
#     After mapping and sorting the pixel values, pair adjacent pixels 

#     For example, a possible traversal order is the standard [1, 3, 5, 2, 4, 6]
#     Applying this traversal order concept to the RGB pixel pair 
#     [[185, 75, 250], [255, 80, 200]] 
#     results in these encodable groups of values:
#     [[185, 255], [75, 80], [250, 200]]
#     """

#     quantizationWidths = validateQuantization(quantizationWidths, True)
#     traversalOrder = validateTraversal(traversalOrder, True)

#     pixelPairs = pixelArrayToZigZag(loadedImage, 3, 2)

#     # If function is run without message, assume retrieval of message
#     if message == "":
#         # Retrieval function
#         if verbose:
#             print("Verbose message: no message given, assuming retrieval of message")
#         messageBinary = ""

#         for pixelPair in pixelPairs:
#             if len(pixelPair) == 2:

#                 # Flatten pixel pair array into un-nested list
#                 pixelArray = [pixel for pair in pixelPair for pixel in pair]

#                 # Sort pixel array given traversal order and group into calculation ready pairs
#                 pixelIndicesDict = dict(sorted(dict(zip(traversalOrder, pixelArray)).items()))
#                 traversedPixelPairs = groupImagePixels(list(dictionary.values()), 2)

#                 for traversedPixelPair in traversedPixelPairs:
#                     # d value
#                     difference = traversedPixelPair[1] - traversedPixelPair[0]

#                     # Determine number of bits storable between pixels
#                     for width in quantizationWidths:
#                         if width[0] <= difference <= width[1]:
#                             lowerBound = width[0]
#                             upperBound = width[1]
#                             break
                    
#                     # Falling-off-boundary check; ensure 0 < calculated pixel value < 255
#                     testingPair = pixelPairEncode(traversedPixelPair, upperBound, difference)
#                     if testingPair[0] < 0 or testingPair[1] < 0 or testingPair[0] > 255 or testingPair[1] > 255:
#                         # One of the values "falls-off" the range from 0 to 255 and hence is invalid
#                         if verbose == True:
#                             print(f"Verbose warning: pixel pair number {traversedPixelPair.index(ptraversedPixelPairixelPair)} had the possibility of falling off and was skipped during the encoding process")
#                     else:
#                         # Passes the check, continue with decoding
#                         # Number of storable bits between two pixels
#                         storableCount = int(math.log(upperBound - lowerBound + 1, 2))
                        
#                         # Extract encoded decimal
#                         if difference >= 0:
#                             retrievedDecimal = difference - lowerBound
#                         else:
#                             retrievedDecimal = - difference - lowerBound

#                         retrievedBinary = bin(retrievedDecimal).replace("0b", "")

#                         # Edge case in which embedded data began with 0's
#                         if storableCount > len(retrievedBinary):
#                             retrievedBinary = "0" * (storableCount-len(retrievedBinary)) + retrievedBinary

#                         messageBinary += retrievedBinary

#         return messageBinary
#     else:
#         # Encoding function
#         newPixels = []

#         # Get binary of message
#         messageBinary = "0" + str(bin(int.from_bytes(message.encode(), "big")))[2:]
#         currentMessageIndex = 0

#         for pixelPair in pixelPairs:
#             if len(pixelPair) == 2 and currentMessageIndex < len(messageBinary) - 1:

#                 # Flatten pixel pair array into un-nested list
#                 pixelArray = [pixel for pair in pixelPair for pixel in pair]

#                 # Sort pixel array given traversal order and group into calculation ready pairs
#                 pixelIndicesDict = dict(sorted(dict(zip(traversalOrder, pixelArray)).items()))
#                 traversedPixelPairs = groupImagePixels(list(dictionary.values()), 2)

#                 postEncodingValues = []

#                 for traversedPixelPair in traversedPixelPair:
#                     # d value
#                     difference = pixelPair[1] - pixelPair[0]

#                     # Determine number of bits storable between pixels
#                     for width in quantizationWidths:
#                         if width[0] <= difference <= width[1]:
#                             lowerBound = width[0]
#                             upperBound = width[1]
#                             break
                    
#                     # Falling-off-boundary check; ensure 0 < calculated pixel value < 255
#                     testingPair = pixelPairEncode(pixelPair, upperBound, difference)
#                     if testingPair[0] < 0 or testingPair[1] < 0 or testingPair[0] > 255 or testingPair[1] > 255:
#                         # One of the values "falls-off" the range from 0 to 255 and hence is invalid
#                         # Append original pixel pair and skip encoding
#                         postEncodingValues += pixelPair
#                         if verbose:
#                             print(f"Verbose warning: pixel pair number {pixelPairs.index(pixelPair)} has the possibility of falling off; skipping")
#                     else:
#                         # Passes the check, continue with encoding
#                         # Number of storable bits between two pixels
#                         storableCount = int(math.log(upperBound - lowerBound + 1, 2))

#                         # Ensure haven't already finished encoding entire message
#                         if currentMessageIndex + storableCount <= len(messageBinary):
#                             # Encode as normal
#                             endIndex = currentMessageIndex+storableCount
#                             storableBits = messageBinary[currentMessageIndex:endIndex]
#                             currentMessageIndex += storableCount
#                         else:
#                             if currentMessageIndex == len(messageBinary):
#                                 # Finished encoding entire message
#                                 currentMessageIndex = len(messageBinary)
#                                 postEncodingValues += pixelPair
#                                 continue
#                             else:
#                                 # Can encode more bits than available, encode what's left
#                                 storableBits = messageBinary[currentMessageIndex:]

#                                 # Ensure last bit doesn't get corrupted, fill empty space with 0's
#                                 storableBits += "0" * (storableCount - len(messageBinary[currentMessageIndex:]))
#                                 currentMessageIndex = len(messageBinary)

#                         # Get value of the chunk of message binary
#                         storableBitsValue = int(storableBits, 2)

#                         # d' value
#                         differencePrime = lowerBound + storableBitsValue if difference >= 0 else -(lowerBound + storableBitsValue)

#                         # Calculate new pixel pair
#                         newPixelPair = pixelPairEncode(pixelPair, differencePrime, difference)                    
#                         postEncodingValues += newPixelPair
                
#                 # Flatten encoded value pair array into un-nested list
#                 pixelArray = [pixel for pair in pixelPair for pixel in pair]

#                 # Un-sort pixel array given traversal order and group into calculation original RGB channels
#                 reversedPaired = groupImagePixels([pixelIndicesDict[key] for key in traversalOrder], 3)
#                 newPixels += reversedPaired
#             else:
#                 # For case in which there's an odd number of pixels; append lone pixel value
#                 newPixels += pixelPair

#         returnValue = True
#         if currentMessageIndex != len(messageBinary):
#             print(f"Warning: only {len(messageBinary[0:currentMessageIndex])} of {len(messageBinary)} bits encoded")
#             print(f"\nOriginal message: {message}")
#             returnValue = False

#             # Verbose errors
#             if verbose == True:
#                 # Underline section of binary that was encoded
#                 # Get max printable width in current terminal
#                 width = os.get_terminal_size()[0]
                
#                 # Create array groupings of message lines and underlinings
#                 printableMessageLines = list(groupImagePixels(messageBinary, width))
#                 printableUnderlinings = list(groupImagePixels("~"*len(messageBinary[0:currentMessageIndex]), width))

#                 # Zip and print
#                 print("\nVerbose warning: only encoded underlined section of message:")
#                 for printableMessageLine, printableUnderlining in itertools.zip_longest(printableMessageLines, printableUnderlinings, fillvalue=""):
#                     print(f"{printableMessageLine}")
#                     if printableUnderlining:
#                         print(f"{printableUnderlining}")

#         # Create new image structure, save file
#         newPixels = list(groupImagePixels(newPixels, loadedImage.size[0]))
#         newPixels = pixelArrayToZigZag(newPixels, 1, loadedImage.size[0], loadedImage.size[0], loadedImage.size[1])
#         array = np.array(newPixels, dtype=np.uint8)
#         savedImage = PIL.Image.fromarray(array)
#         savedImage.save('./IO/out.png')

#         return returnValue

# # # Sort pixel array given traversal order and group into calculation ready pairs
# # pixelIndicesDict = dict(zip(traversalOrder, pixelArray))
# # traversedPixelPairs = list({key:pixelIndicesDict[key] for key in sorted(pixelIndicesDict.keys())}.values())
# # traversedPixelPairs = groupImagePixels(traversedPixelPairs, 2)

# # # Maps values in array to new array given an ordering array
# # test = [11,12,13,14,15,16,17,18,19]
# # vals = [4, 5, 1, 7, 3, 2, 9, 8, 6]
# # dictionary = dict(sorted(dict(zip(vals, test)).items()))
# # test = list(dictionary.values())

# # dictionary = dict(zip(vals, test))
# # test = list({key:dictionary[key] for key in sorted(dictionary.keys())}.values())



# # # Reversing process
# # # [13, 16, 15, 11, 12, 19, 14, 18, 17]
# # # [4, 5, 1, 7, 3, 2, 9, 8, 6]
# # reversed = [dictionary[key] for key in vals]


# test = [11,12,13,14,15,16,17,18,19]
# vals = [4, 5, 1, 7, 3, 2, 9, 8, 6]
# order = list(zip(vals,[1,2,3,4,5,6,7,8,9]))
# dictionary = dict(sorted(dict(zip(order, test)).items()))
# test = list(dictionary.values())

# test = [item + 1 for item in test]

# dictionary = dict(sorted(dict(zip([ key[1] for key in dictionary.keys() ], test)).items()))
# testing = list(dictionary.values())

# testing



# import hashlib
# import math 

# def rosenburgStrongPairing(argument, reverse=False):
#     """
#     Implementation of the Rosenburg-Strong Pairing Function
#     """
#     if reverse:
#         m = math.floor(math.sqrt(argument))
#         if argument-m**2<m:
#             return [int(argument-m**2), int(m)]
#         return [int(m), int(m**2+2*m-argument)]

#     x, y = argument
#     return (max(x,y))**2+max(x,y)+x-y

# def embedLength(message):
#     """
#     This function zig-zags the bit length of the message into the message hash
#     """

#     originalHash = hashlib.sha256(message.encode()).hexdigest()
#     modifiedHash = originalHash

#     remainingLength = str(len(str(bin(int.from_bytes(message.encode(), "big")))[2:]) + 1)
#     if len(remainingLength) % 2 == 1:
#         modifiedHash = remainingLength[0] + modifiedHash
#         remainingLength = remainingLength[1:]

#     while len(remainingLength) > 0:
#         modifiedHash = remainingLength[0] + modifiedHash + remainingLength[1]
#         remainingLength = remainingLength[2:]

#     return modifiedHash

# def retrieveLength(modifiedHash):
#     """
#     This function retrieves the bit length from hash modified by embedLength()
#     """
#     bitLength = ""
#     while len(modifiedHash) > 65:
#         bitLength += modifiedHash[-1] + modifiedHash[0]
#         modifiedHash = modifiedHash[1:len(modifiedHash)-1]

#     if len(modifiedHash) == 65:
#         bitLength += modifiedHash[0]
#         modifiedHash = modifiedHash[1:]

#     bitLength = bitLength[::-1]
#     return bitLength

# # test = {}
# # test[rosenburgStrongPairing([5,5])] = embedLength("hi")
# # print(test)

# # Code to modify metadata values
# from PIL.PngImagePlugin import PngImageFile, PngInfo

# # Edit PNG metadata to include fingerprint of this PVD algorithm
# modifyMetadata = PngImageFile("./IO/outCopy.png")
# metadata = PngInfo()
# metadata.add_text("png:fingerprint", f"{rosenburgStrongPairing([5,5])}:{embedLength('hi')}")
# modifyMetadata.save("./IO/outCopy.png", pnginfo=metadata)

# testEncoded = PngImageFile("./IO/outCopy.png")
# print(testEncoded.size)
# print(testEncoded.text)



# verificationData: PIL.PngImagePlugin.PngImageFile=False,

# Verify image data
        # if verificationData:
            # verifications = verificationData["png:fingerprint"].split(":")
            # imageWidth, imageHeight = rosenburgStrongPairing(verifications[0])
            # bitLength, messageHash = retrieveLength(verifications[1])

            # if loadedImage.size[0] != imageWidth or loadedImage.size[1] != imageHeight:
            #     raise Exception(f"Image verification failed. Image dimensions don't match encoded verification data.")

# if verificationData:
            # if len(messageBinary) >= bitLength:
            #     messageBinary = messageBinary[:bitLength]
            #     if hashlib.sha256(messageBinary.encode()).hexdigest() == messageHash:
            #         return messageBinary
            #     else:
            #         raise Exception(f"Message verification failed. Hash of retrieved binary doesn't match encoded verification data.")
            # raise Exception("Message verification failed. Length of retrieved message binary doesn't match encoded verification data.")


# import math
# def rosenburgStrongPairing(argument, reverse=False):
#     """
#     Implementation of the Rosenburg-Strong Pairing Function
#     """
#     if reverse:
#         m = math.floor(math.sqrt(argument))
#         if argument-m**2<m:
#             return [int(argument-m**2), int(m)]
#         return [int(m), int(m**2+2*m-argument)]

#     x, y = argument
#     print(argument)
#     return (max(x,y))**2+max(x,y)+x-y

# uniqueID = rosenburgStrongPairing([10000, 15129])
# test = rosenburgStrongPairing(uniqueID, True)
# print(uniqueID)
# print(test)

# import math
# def cantorPairing(argument, reverse=False):
#     if reverse:
#         w = math.floor((math.sqrt(8*argument+1)-1)/2)
#         t = (w**2+w)/2
#         y = argument - t
#         x = w - y
#         return x, y
#     x, y = argument
#     return (x+y+1)(x+y)/2 + y


# # Code to zip message length into hash 
# import hashlib

# def embedLength(bitLength, message):
#     originalHash = hashlib.sha256(message.encode()).hexdigest()
#     modifiedHash = originalHash

#     remainingLength = bitLength
#     if len(remainingLength) % 2 == 1:
#         modifiedHash = remainingLength[0] + modifiedHash
#         remainingLength = remainingLength[1:]

#     while len(remainingLength) > 0:
#         modifiedHash = remainingLength[0] + modifiedHash + remainingLength[1]
#         remainingLength = remainingLength[2:]

#     print(originalHash)
#     print(modifiedHash)

#     return modifiedHash

# def retrieveLength(modifiedHash):
#     message = ""
#     while len(modifiedHash) > 65:
#         message += modifiedHash[-1] + modifiedHash[0]
#         modifiedHash = modifiedHash[1:len(modifiedHash)-1]
#     if len(modifiedHash) == 65:
#         message += modifiedHash[0]
#         modifiedHash = modifiedHash[1:]

#     message = message[::-1]
#     print(message)

# modifiedHash = embedLength("19383", "hi")
# retrieveLength(modifiedHash)
