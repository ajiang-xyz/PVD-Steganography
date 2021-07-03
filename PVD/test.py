print("Executing...")

from typing import List
from utils import *

def getMaxStorage(loadedImage: PIL.PngImagePlugin.PngImageFile, quantizationWidths: list=[],
                    traversalOrder: list=[], verbose: bool=False):
    """
    Calculates the maximum number of storable bits in a an image file, given a traversal order (for RGB images) 
    and quantization widths.
    """

    print()

    quantizationWidths = validateQuantization(quantizationWidths, verbose)
    traversalOrder = validateTraversal(traversalOrder, verbose)

    print()

    storable = []
    occurances = {}
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
                        maxValue = int(math.log(upperBound - lowerBound + 1, 2))
                        occurances[maxValue] = occurances[maxValue] + 1 if occurances.setdefault(maxValue, False) else 1
                        storable.append(maxValue)
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
                    maxValue = int(math.log(upperBound - lowerBound + 1, 2))
                    occurances[maxValue] = occurances[maxValue] + 1 if occurances.setdefault(maxValue, False) else 1
                    storable.append(maxValue)

    storableCount = sum(storable)

    power = 1024
    counter = 0
    labels = {0 : "", 1: "kilo", 2: "mega", 3: "giga", 4: "tera", 5:"peta"}
    while storableCount > power:
        storableCount /= power
        counter += 1
    return round(storableCount, 2), labels[counter]+"bits", storable, occurances


def occuranceCount(array):
    """
    Returns dict of form <element in array>:<appearance count in array>
    """
    occurances = {}
    for value in array:
        occurances[value] = occurances[value] + 1 if occurances.setdefault(value, False) else 1
    return occurances

def mid(array, bias=True):
    """
    Returns biased middle value of array
    True bias means biased towards end of array
    False biase means biased towards beginning of array
    """
    if bias:
        biasFunction = math.ceil
    else:
        biasFunction = math.floor

    return array[biasFunction((len(array)-1)/2)]

def getIndexes(array, keyword):
    """
    Returns array of indices search term appears in input array
    """
    indexes = []
    for i in range(len(array)):
        if array[i] == keyword:
            indexes.append(i)
    return indexes

import random
def seededTraversal(differences, messageBitLength, occurances, seed=69420):
    random.seed(seed)

    # occurances = occuranceCount(differences)
    # print("finished counting occurances")
    occurances = {item[0]:item[1] for item in sorted(occurances.items())}

    keys = list(occurances.keys())
    # counts = list(occurances.values())

    maxStorable = sum([key * occurances[key] for key in occurances])
    traversed = []

    while sum(traversed) < messageBitLength:
        keyStorableValues = [key * occurances[key] for key in occurances]
        weights = [round((math.sqrt(item))/(maxStorable),9) for item in keyStorableValues]
        # print(occurances)
        # print(f"weights: {weights}")
        choice = random.choices(keys, weights=weights)[0]
        occurances[choice] -= 1
        traversed.append(choice)

    occurances = occuranceCount(differences)
    occurances = {item[0]:item[1] for item in sorted(occurances.items())}

    traversedOccurances = occuranceCount(traversed)
    traversedOccurances = {item[0]:item[1] for item in sorted(traversedOccurances.items())}

    # print()
    # print(f"image data: {differences}")
    # print(f"occurances: {occurances}")
    # print()
    # print(f"list of values to encode into: {traversed}")
    # print(f"occurances in traversed: {traversedOccurances}")

    # Translate traversed values into indexes to embed
    traversedIndexes = {}
    for item in traversedOccurances:
        traversedIndexes[item] = getIndexes(differences, item)[:traversedOccurances[item]]

    # print()
    # print(traversedIndexes)

    encodingIndexes = []
    for item in traversed:
        encodingIndexes.append(traversedIndexes[item].pop(0))

    print(f"index order to encode: {encodingIndexes}")
    

@executionTime
def main():
    testingImage = PIL.Image.open("/mnt/c/users/alex/downloads/langa.png")
    maxStorable, sizeLabel, differences, occurances = getMaxStorage(testingImage, verbose=True)
    print(f"{maxStorable} {sizeLabel}\n")
    seededTraversal(differences, 102384, occurances)
    # print(chunkArray(differences, 7))
    # print(list(groupImagePixels(differences, 5)))

main()


# import random
# def getEmbedIndexes(differences, bitLength):
#     # differences = [1,4,6,1,3,1,3,5,1,4,7,3,3,2,3,4,5,6,7,8,9,1,1,1,1,1]

#     occurances = occuranceCount(differences)
#     occurances = {item[0]:item[1] for item in sorted(occurances.items())}

#     keys = list(occurances.keys())
#     keyCount = list(occurances.values())
#     keyStorableValues = [item[0] * item[1] for item in zip(keys,keyCount)]
#     weights = [round(item/sum(keyStorableValues),2) for item in keyStorableValues]
#     random.seed(69)

#     # when choice is made pop out of keys, adjust weights
#     print(random.choices(keys, weights=weights, k=5))
#     print()
#     print(f"{keys}\n{keyCount}\n{keyStorableValues}\n{weights}\n")
    
#     if len(keys) % 2 == 0:
#         end = len(keys)/2
        
#         lowSum = sum(keyStorableValues[end:])
#         midSum = 0
#         highSum = sum(keyStorableValues[:end])

#         print(f"{keys[:len(keys)/2]}, {keys[len(keys)/2:]}")
#         print(f"{lowSum}, {midSum}, {highSum}")
#     else:
#         lowEnd = math.floor(len(keys)/2)
#         highEnd = math.ceil(len(keys)/2)
        
#         lowSum = keyStorableValues[lowEnd:]
#         midSum = keyStorableValues[int(len(keys)/2)]
#         highSum = keyStorableValues[:highEnd]

#         print(f"{keys[:lowEnd]}, {keys[int(len(keys)/2)]}, {keys[highEnd:]}")
#         print(f"{lowSum}, {midSum}, {highSum}")
        
#     low = keys[0]
#     middle = mid(keys)
#     high = keys[-1]

#     lowDiff = middle - low
#     highDiff = high - middle

#     print(f"\n{low}, {middle}, {high}\n{lowDiff}, {highDiff}")



# class ValueIndexPair(object):
#     def __init__(self, value, index):
#         self.value = value
#         self.index = index

# def createPairArray(array):
#     pairedArray = []

#     currentIndex = 0
#     for value in array:
#         pairedArray += [ValueIndexPair(value, currentIndex)]
#         currentIndex += 1
        
#     return pairedArray

# def chunkArray(array, chunksCount):
#     average = len(array) / float(chunksCount)
#     chunkedArrays = []
#     last = 0.0

#     while last < len(array):
#         chunkedArrays.append(array[int(last):int(last + average)])
#         last += average

#     return chunkedArrays

# def groupImagePixels(imagePixels, imageWidth):
#     """
#     Split array of pixel values into nested: [[1,2],[3,4],[5,6],[7,8]] --> [[[1,2],[3,4]],[[5,6],[7,8]]]
#     """
#     for i in range(0, len(imagePixels), imageWidth): 
#         yield imagePixels[i : i + imageWidth]

# testingImage = PIL.Image.open("./IO/inColor.png")
# maxStorable, sizeLabel, differences = getMaxStorage(testingImage, verbose=True)
# print(chunkArray(differences, 7))
# print(list(groupImagePixels(differences, 5)))


# def combinationSum(candidates: List[int], finalTarget: int) -> List[List[int]]:
#     results = list()
#     if not candidates:
#         return results

#     if sum(candidates) == finalTarget:
#         return candidates

#     def depthFirstSearch(candidates, temp, index, length, target):
#         if target == 0:
#             results.append(list(temp))
#             return
#         if target > finalTarget:
#             return
#         for currentIndex in range(index, length):
#             # print(f"{index}, {target}", end="\r")
#             if target < candidates[currentIndex]:
#                 break
                
#             temp.append(candidates[currentIndex])
#             depthFirstSearch(candidates, temp, currentIndex, length, target - candidates[currentIndex])
#             temp.pop()
    
#     length = len(candidates)
#     candidates.sort()
    
#     depthFirstSearch(candidates, list(), 0, length, finalTarget)
#     return results

# @executionTime
# def main():
#     testingImage = PIL.Image.open("./IO/inColor.png")
#     maxStorable, sizeLabel, differences = getMaxStorage(testingImage, verbose=True)
#     print(f"{maxStorable} {sizeLabel}")
#     print(differences)

#     print("Starting combination sum algorithm...")
#     test = combinationSum(differences, 32)
#     print(test)
# main()

# test = ValueIndexPair(1,0)()
# print(test)



# def getPairArray(pairArray, mode=""):
#     if mode == "values":
#         return [item.value for item in pairArray]
#     return {item.value:item.index for item in pairArray}





# pairedArray = createPairArray([2,2,3,4,5])
# for item in pairedArray:
#     item.value += 1
#     print(item.value)

# for i, j in enumerate(pairedArray):
#     print(f"{i}, {j.value}")

# print(getPairArray(pairedArray))

# import numpy as np
# import functools
# @functools.lru_cache(maxsize=None)
# def subset_sum(numbers, target, partial=[], partial_sum=0):
#     if partial_sum == target:
#         yield partial
#     if partial_sum >= target:
#         return
#     for index, value in enumerate(numbers):
#         remaining = numbers[index + 1:]
#         yield from subset_sum(remaining, target, partial + [value.value], partial_sum + value.value)

# @executionTime
# def testing():
#     testingImage = PIL.Image.open("./IO/inColor.png")
#     count, label, differences = getMaxStorage(testingImage, verbose=True)
#     differences = createPairArray(differences)
#     print(f"\n{count} {label}")
#     print(f"{getPairArray(differences)}")

#     # indexes = dict(zip(differences,range(0,len(differences))))
#     # print(indexes)
#     test = subset_sum(differences, 135)
#     # highestAverage = 0
#     itemValue = None
#     # for item in test: 
#     #     average = np.average(np.diff(np.array(item)))
#     #     if average > highestAverage:
#     #         highestAverage = average
#     #         itemValue = item

#     print([value for value in test])
#     # itemValue = max(test)

#     print(getPairArray(differences))
#     print(itemValue)
#     # encodingIndexes = [indexes[value] for value in itemValue]
#     # print(encodingIndexes)


# testing()

# @executionTime
# def changes(amount, coins):
#     ways = [0] * (amount + 1)
#     ways[0] = 1
#     for coin in coins:
#         for j in range(coin, amount + 1):
#             ways[j] += ways[j - coin]
#     return ways




# for item in test:
#     print(item)
 
# print(changes(100, [1, 5, 10, 25]))
# print(changes(100000, [1, 5, 10, 25, 50, 100]))

# testing()