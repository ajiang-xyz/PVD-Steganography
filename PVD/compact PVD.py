_G='./IO/outColor.png'
_F='\nVerbose warning: only encoded underlined section of message:'
_E='big'
_D='Verbose message: no message given, assuming retrieval of message'
_C=False
_B='0'
_A=True
from PIL.PngImagePlugin import PngImageFile,PngInfo
from utils import *
import numpy as np,itertools,math,PIL,os
def rgbChannels(loadedImage,message='',quantizationWidths=[],traversalOrder=[],verbose=_C):
	if message=='':
		if verbose:print(_D)
	quantizationWidths=validateQuantization(quantizationWidths,_A);traversalOrder=validateTraversal(traversalOrder,_A);pixelPairs=pixelArrayToZigZag(loadedImage,3,2)
	if message=='':
		messageBinary='';currentPairCounter=0
		for pixelPair in pixelPairs:
			currentPairCounter+=1
			if len(pixelPair)==2:
				pixelArray=[pixel for pair in pixelPair for pixel in pair];pixelIndicesDict=dict(sorted(dict(zip(traversalOrder,pixelArray)).items()));traversedPixelPairs=list(groupImagePixels(list(pixelIndicesDict.values()),2));currentTraversedCounter=0
				for traversedPixelPair in traversedPixelPairs:
					currentTraversedCounter+=1;difference=traversedPixelPair[1]-traversedPixelPair[0]
					for width in quantizationWidths:
						if width[0]<=abs(difference)<=width[1]:lowerBound=width[0];upperBound=width[1];break
					testingPair=pixelPairEncode(traversedPixelPair,upperBound,difference)
					if testingPair[0]<0 or testingPair[1]<0 or testingPair[0]>255 or testingPair[1]>255:
						if verbose==_A:print(f"Verbose message: channel pair number {currentTraversedCounter} in pixel pair number {currentPairCounter} has the possibility of falling off; skipping")
					else:
						storableCount=int(math.log(upperBound-lowerBound+1,2))
						if difference>=0:retrievedDecimal=difference-lowerBound
						else:retrievedDecimal=-difference-lowerBound
						retrievedBinary=bin(retrievedDecimal).replace('0b','')
						if storableCount>len(retrievedBinary):retrievedBinary=_B*(storableCount-len(retrievedBinary))+retrievedBinary
						messageBinary+=retrievedBinary
		return messageBinary
	else:
		newPixels=[];messageBinary=_B+str(bin(int.from_bytes(message.encode(),_E)))[2:];currentMessageIndex=0;currentPairCounter=0
		for pixelPair in pixelPairs:
			currentPairCounter+=1
			if len(pixelPair)==2 and currentMessageIndex<len(messageBinary)-1:
				pixelArray=[pixel for pair in pixelPair for pixel in pair];traversalIndiceDict=list(zip(traversalOrder,[0,1,2,3,4,5]));pixelIndicesDict=dict(sorted(dict(zip(traversalIndiceDict,pixelArray)).items()));traversedPixelPairs=list(groupImagePixels(list(pixelIndicesDict.values()),2));postEncodingValues=[];currentTraversedCounter=0
				for traversedPixelPair in traversedPixelPairs:
					currentTraversedCounter+=1;difference=traversedPixelPair[1]-traversedPixelPair[0]
					for width in quantizationWidths:
						if width[0]<=abs(difference)<=width[1]:lowerBound=width[0];upperBound=width[1];break
					testingPair=pixelPairEncode(traversedPixelPair,upperBound,difference)
					if testingPair[0]<0 or testingPair[1]<0 or testingPair[0]>255 or testingPair[1]>255:
						postEncodingValues+=traversedPixelPair
						if verbose:print(f"Verbose message: channel pair number {currentTraversedCounter} in pixel pair number {currentPairCounter} has the possibility of falling off; skipping")
					else:
						storableCount=int(math.log(upperBound-lowerBound+1,2))
						if currentMessageIndex+storableCount<=len(messageBinary):endIndex=currentMessageIndex+storableCount;storableBits=messageBinary[currentMessageIndex:endIndex];currentMessageIndex+=storableCount
						elif currentMessageIndex==len(messageBinary):currentMessageIndex=len(messageBinary);postEncodingValues+=pixelPair;continue
						else:storableBits=messageBinary[currentMessageIndex:];storableBits+=_B*(storableCount-len(messageBinary[currentMessageIndex:]));currentMessageIndex=len(messageBinary)
						storableBitsValue=int(storableBits,2);differencePrime=lowerBound+storableBitsValue if difference>=0 else-(lowerBound+storableBitsValue);newPixelPair=pixelPairEncode(traversedPixelPair,differencePrime,difference);postEncodingValues+=newPixelPair
				pixelIndicesDict=dict(sorted(dict(zip([key[1]for key in pixelIndicesDict.keys()],postEncodingValues)).items()));reversedPaired=list(groupImagePixels([pixel for pixel in pixelIndicesDict.values()],3));newPixels+=reversedPaired;print(pixelPair);print(reversedPaired)
			else:newPixels+=pixelPair
		returnValue=_A
		if currentMessageIndex!=len(messageBinary):
			print(f"Warning: only {len(messageBinary[0:currentMessageIndex])} of {len(messageBinary)} bits encoded");print(f"\nOriginal message: {message}");returnValue=_C
			if verbose==_A:
				width=os.get_terminal_size()[0];printableMessageLines=list(groupImagePixels(messageBinary,width));printableUnderlinings=list(groupImagePixels('~'*len(messageBinary[0:currentMessageIndex]),width));print(_F)
				for (printableMessageLine,printableUnderlining) in itertools.zip_longest(printableMessageLines,printableUnderlinings,fillvalue=''):
					print(f"{printableMessageLine}")
					if printableUnderlining:print(f"{printableUnderlining}")
		newPixels=list(groupImagePixels(newPixels,loadedImage.size[0]));newPixels=pixelArrayToZigZag(newPixels,1,loadedImage.size[0],loadedImage.size[0],loadedImage.size[1]);array=np.array(newPixels,dtype=np.uint8);savedImage=PIL.Image.fromarray(array);savedImage.save(_G);return returnValue
def singleChannel(loadedImage,message='',quantizationWidths=[],verbose=_C):
	if message=='':
		if verbose:print(_D)
	quantizationWidths=validateQuantization(quantizationWidths,_A);pixelPairs=pixelArrayToZigZag(loadedImage,1,2)
	if message=='':
		messageBinary=''
		for pixelPair in pixelPairs:
			if len(pixelPair)==2:
				difference=pixelPair[1]-pixelPair[0]
				for width in quantizationWidths:
					if width[0]<=abs(difference)<=width[1]:lowerBound=width[0];upperBound=width[1];break
				testingPair=pixelPairEncode(pixelPair,upperBound,difference)
				if testingPair[0]<0 or testingPair[1]<0 or testingPair[0]>255 or testingPair[1]>255:
					if verbose==_A:print(f"Verbose message: pixel pair number {pixelPairs.index(pixelPair)} had the possibility of falling off and was skipped during the encoding process")
				else:
					storableCount=int(math.log(upperBound-lowerBound+1,2))
					if difference>=0:retrievedDecimal=difference-lowerBound
					else:retrievedDecimal=-difference-lowerBound
					retrievedBinary=bin(retrievedDecimal).replace('0b','')
					if storableCount>len(retrievedBinary):retrievedBinary=_B*(storableCount-len(retrievedBinary))+retrievedBinary
					messageBinary+=retrievedBinary
		return messageBinary
	else:
		newPixels=[];messageBinary=_B+str(bin(int.from_bytes(message.encode(),_E)))[2:];currentMessageIndex=0
		for pixelPair in pixelPairs:
			if len(pixelPair)==2 and currentMessageIndex<len(messageBinary)-1:
				difference=pixelPair[1]-pixelPair[0]
				for width in quantizationWidths:
					if width[0]<=abs(difference)<=width[1]:lowerBound=width[0];upperBound=width[1];break
				testingPair=pixelPairEncode(pixelPair,upperBound,difference)
				if testingPair[0]<0 or testingPair[1]<0 or testingPair[0]>255 or testingPair[1]>255:
					newPixels+=pixelPair
					if verbose:print(f"Verbose message: pixel pair number {pixelPairs.index(pixelPair)} has the possibility of falling off; skipping")
				else:
					storableCount=int(math.log(upperBound-lowerBound+1,2))
					if currentMessageIndex+storableCount<=len(messageBinary):endIndex=currentMessageIndex+storableCount;storableBits=messageBinary[currentMessageIndex:endIndex];currentMessageIndex+=storableCount
					elif currentMessageIndex==len(messageBinary):currentMessageIndex=len(messageBinary);newPixels+=pixelPair;continue
					else:storableBits=messageBinary[currentMessageIndex:];storableBits+=_B*(storableCount-len(messageBinary[currentMessageIndex:]));currentMessageIndex=len(messageBinary)
					storableBitsValue=int(storableBits,2);differencePrime=lowerBound+storableBitsValue if difference>=0 else-(lowerBound+storableBitsValue);newPixelPair=pixelPairEncode(pixelPair,differencePrime,difference);newPixels+=newPixelPair
			else:newPixels+=pixelPair
		returnValue=_A
		if currentMessageIndex!=len(messageBinary):
			print(f"Warning: only {len(messageBinary[0:currentMessageIndex])} of {len(messageBinary)} bits encoded");print(f"\nOriginal message: {message}");returnValue=_C
			if verbose==_A:
				width=os.get_terminal_size()[0];printableMessageLines=list(groupImagePixels(messageBinary,width));printableUnderlinings=list(groupImagePixels('~'*len(messageBinary[0:currentMessageIndex]),width));print(_F)
				for (printableMessageLine,printableUnderlining) in itertools.zip_longest(printableMessageLines,printableUnderlinings,fillvalue=''):
					print(f"{printableMessageLine}")
					if printableUnderlining:print(f"{printableUnderlining}")
		newPixels=list(groupImagePixels(newPixels,loadedImage.size[0]));newPixels=pixelArrayToZigZag(newPixels,1,loadedImage.size[0],loadedImage.size[0],loadedImage.size[1]);array=np.array(newPixels,dtype=np.uint8);savedImage=PIL.Image.fromarray(array);savedImage.save('./IO/out.png');return returnValue
@executionTime
def main():
	print('Beginning execution...');imagePath=_G;loadedImage=PIL.Image.open(imagePath)
	if'RGB'in loadedImage.mode.upper():returnValue=rgbChannels(loadedImage,traversalOrder=[],verbose=_A)
	elif loadedImage.mode.upper()=='L':returnValue=singleChannel(loadedImage,message='hi',verbose=_A)
	else:raise Exception(f"The image located at {imagePath} is not in a supported format.")
	print()
	if isinstance(returnValue,bool):
		if returnValue==_A:print('Done.')
		else:print('Completed with errors.')
	else:print(f"Retrieved binary: {returnValue}")
if __name__=='__main__':main()