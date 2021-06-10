from singleChannel import *
from rgbChannels import *
from utils import *

@executionTime
def main():
    """
    Main driver function
    """

    imagePath = "./IO/inColor.png"
    loadedImage = PIL.Image.open(imagePath)

    # 24-bit RGB image; ignores Alpha channel
    if "RGB" in loadedImage.mode.upper():
        returnValue = rgbChannels(loadedImage, message="hello world!", verify=True, verbose=True)
    
    # 8-bit Black & White image
    elif loadedImage.mode.upper() == "L":
        returnValue = singleChannel(loadedImage, message="hola", verbose=True)
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
        print("Done.")
        print(f"Retrieved binary: {returnValue}")

@executionTime
def test():
    """
    Dev function
    """

    # Get maximum number of bits storable in image
    imagePath = "./IO/inColor.png"
    loadedImage = PIL.Image.open(imagePath)
    returnVals = getMaxStorage(loadedImage, verbose=True)

    print(f"\n{returnVals[0]} {returnVals[1]}")

if __name__ == "__main__":
    print("Beginning execution...")
    main()