from PIL.PngImagePlugin import PngImageFile, PngInfo
from utils import *
import numpy as np,itertools,math,PIL,os
_A=True
_B=False
def singleChannel(loadedImage,message='',quantizationWidths=[],verbose=_B):
    A='0';quantizationWidths=validateQuantization(quantizationWidths);pixelPairs=pixelArrayToZigZag(loadedImage,1,2)
    if message=='':
        if verbose:print('Verbose message: no message given, assuming retrieval of message')
        messageBinary=''
        for pixelPair in pixelPairs:
            if len(pixelPair)==2:
                difference=pixelPair[1]-pixelPair[0]
                for width in quantizationWidths:
                    if width[0]<=difference<=width[1]:lowerBound=width[0];upperBound=width[1];break
                testingPair=pixelPairEncode(pixelPair,upperBound,difference)
                if testingPair[0]<0 or testingPair[1]<0 or testingPair[0]>255 or testingPair[1]>255:
                    if verbose==_A:print(f"Verbose warning: pixel pair number {pixelPairs.index(pixelPair)} had the possibility of falling off and was skipped during the encoding process")
                else:
                    storableCount=int(math.log(upperBound-lowerBound+1,2))
                    if difference>=0:retrievedDecimal=difference-lowerBound
                    else:retrievedDecimal=-difference-lowerBound
                    retrievedBinary=bin(retrievedDecimal).replace('0b','')
                    if storableCount>len(retrievedBinary):retrievedBinary=A*(storableCount-len(retrievedBinary))+retrievedBinary
                    messageBinary+=retrievedBinary
        return messageBinary
    else:
        newPixels=[];messageBinary=A+str(bin(int.from_bytes(message.encode(),'big')))[2:];currentMessageIndex=0
        for pixelPair in pixelPairs:
            if len(pixelPair)==2 and currentMessageIndex<len(messageBinary)-1:
                difference=pixelPair[1]-pixelPair[0]
                for width in quantizationWidths:
                    if width[0]<=difference<=width[1]:lowerBound=width[0];upperBound=width[1];break
                testingPair=pixelPairEncode(pixelPair,upperBound,difference)
                if testingPair[0]<0 or testingPair[1]<0 or testingPair[0]>255 or testingPair[1]>255:
                    newPixels+=pixelPair
                    if verbose:print(f"Verbose warning: pixel pair number {pixelPairs.index(pixelPair)} has the possibility of falling off; skipping")
                else:
                    storableCount=int(math.log(upperBound-lowerBound+1,2))
                    if currentMessageIndex+storableCount<=len(messageBinary):endIndex=currentMessageIndex+storableCount;storableBits=messageBinary[currentMessageIndex:endIndex];currentMessageIndex+=storableCount
                    elif currentMessageIndex==len(messageBinary):currentMessageIndex=len(messageBinary);newPixels+=pixelPair;continue
                    else:storableBits=messageBinary[currentMessageIndex:];storableBits+=A*(storableCount-len(messageBinary[currentMessageIndex:]));currentMessageIndex=len(messageBinary)
                    storableBitsValue=int(storableBits,2);differencePrime=lowerBound+storableBitsValue if difference>=0 else-(lowerBound+storableBitsValue);newPixelPair=pixelPairEncode(pixelPair,differencePrime,difference);newPixels+=newPixelPair
            else:newPixels+=pixelPair
        returnValue=_A
        if currentMessageIndex!=len(messageBinary):
            print(f"Warning: only {len(messageBinary[0:currentMessageIndex])} of {len(messageBinary)} bits encoded");print(f"\nOriginal message: {message}");returnValue=_B
            if verbose==_A:
                width=os.get_terminal_size()[0];printableMessageLines=list(groupImagePixels(messageBinary,width));printableUnderlinings=list(groupImagePixels('~'*len(messageBinary[0:currentMessageIndex]),width));print('\nVerbose warning: only encoded underlined section of message:')
                for (printableMessageLine,printableUnderlining) in itertools.zip_longest(printableMessageLines,printableUnderlinings,fillvalue=''):
                    print(f"{printableMessageLine}")
                    if printableUnderlining:print(f"{printableUnderlining}")
        newPixels=list(groupImagePixels(newPixels,loadedImage.size[0]));newPixels=pixelArrayToZigZag(newPixels,1,loadedImage.size[0],loadedImage.size[0],loadedImage.size[1]);array=np.array(newPixels,dtype=np.uint8);savedImage=PIL.Image.fromarray(array);savedImage.save('./IO/out.png');return returnValue
@executionTime
def main():
    A='hi';print('Beginning execution...');imagePath='./IO/in.png';loadedImage=PIL.Image.open(imagePath)
    if loadedImage.mode.upper()=='L':returnValue=singleChannel(loadedImage,message=A,verbose=_A)
    else:raise Exception(f"The image located at {imagePath} is not in a supported format.")
    print()
    if isinstance(returnValue,bool):
        if returnValue==_A:print('Done.')
        else:print('Completed with errors.')
    else:print(f"Retrieved binary: {returnValue}")
if __name__=='__main__':main()