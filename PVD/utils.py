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