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
