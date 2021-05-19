# Description of Wu and Tsai's 8-Bit Black & White PVD algorithm

## Encoding message
Suppose we have a gray-scale image that's 5 by 5 pixels (zoomed in for clarity):
<div align="center"><img src="https://raw.githubusercontent.com/ajiang-xyz/PVD-Steganography/master/Research/Resources/example.png"/></div>
<div align="center"><i>Fig. 1: A gray-scale 5 by 5 pixel image</i></div>


Let's take the top left-most pixels, shown here, and try to hide some data between them:
<div align="center"><img src="https://raw.githubusercontent.com/ajiang-xyz/PVD-Steganography/master/Research/Resources/twoPixels.png"/></div>
<div align="center"><i>Fig. 2: The top left-most pixels of Fig. 1</i></div>

In this example, the two pixels have values of 73 and 80, respectively. Note: lower pixel values represent darker pixels.
```
pixelOne = 73
pixelTwo = 80
```
Next, let's choose some secret message we'd like to store. For this example, let's go with the message "hi"


Given these two pixel values and this message, let's encode our secret:

1. Calculate the absolute value of the difference of the two pixel values:
```
difference = 80 - 73 = 7
```
2. Determine which quantization range it falls into:
```
Quantization ranges used:
[0,1], [2,3], [4,7], [8,11], [12,15], [16,23], [24,31], 
[32,47], [48,63], [64,95], [96,127], [128,191], [192,255]

difference falls into the [4, 7] range:
lowerBound = 4
upperBound = 7
```
3. Calculate number of storable bits:
```
log base 2 of (<width of range> + 1)
log base 2 of (7 - 4 + 1) = 2

This means we can store 2 bits here without much visual change:
storableBits = 2
```
4. Calculate the decimal value of the next number of storable bits:
```
Binary value of "hi" is 0110100001101001
In this example, the next storable bits are

0110100001101001
~~

In decimal, b"01" represents the integer 1:
binaryValue = 1
```
5. Calculate the absolute difference prime
```
if difference >= 0:
    differencePrime = lowerBound + binaryValue
else:
    differencePrime = -(lowerBound + binaryValue)

We apply this to our current values:
differencePrime = 5
```
6. Finally, calculate encoded pixel values:
```
m = differencePrime - difference
if difference % 2 == 0:
    # difference variable is an even value
    pixelOnePrime = pixelOne - floor(m/2)
    pixelTwoPrime = pixelTwo + ceiling(m/2)
else:
    # difference variable is an odd value
    pixelOnePrime = pixelOne - ceiling(m/2)
    pixelTwoPrime = pixelTwo + floor(m/2)

With our values, this becomes:
m = 5 - 7
# difference variable is an odd value
pixelOnePrime = 73 - ceiling((-2)/2)
pixelTwoPrime = 80 + floor((-2)/2)

This results in the pair (74, 79) as the final encoded pixel pair 
```

Let's compare this with our original pixel pair:

<div align="center"><img src="https://raw.githubusercontent.com/ajiang-xyz/PVD-Steganography/master/Research/Resources/twoPixels.png"/></div>
<div align="center"><i>Fig. 2: The top left-most pixels of Fig. 1</i></div>

<div align="center"><img src="https://raw.githubusercontent.com/ajiang-xyz/PVD-Steganography/master/Research/Resources/encodedPixels.png"/></div>
<div align="center"><i>Fig. 3: The new encoded pixel pair</i></div>

Pretty good right?

## Retrieving message
```
fall-off test:
f((modified steg values), upper bound of range of difference - difference)

where f = 

(pixel1 - ceil((upper bound of range of difference - difference)/2), pixel2 + floor((upper bound of range of difference - difference)/2) if difference is odd

(pixel1 - floor((upper bound of range of difference - difference)/2), pixel2 + ceil((upper bound of range of difference - difference)/2) if difference is even

calculate data if no pixel falls off:
d = abs(72-81) = 9

 d - lower bound for d >= 0
-d - lower bound for d < 0

gives 9-6 = 3
in binary gives us 11 (because 2 bits are storable so there aren't any padding 0s)
```