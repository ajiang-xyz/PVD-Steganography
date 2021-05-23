

# PVD Steganography Research Project

## Objective
Create several variations of the PVD steganographic method and write a tool for the encoding and decoding of these variations. 

## Background

### What is steganography?
Steganography, in the case of images, is the practice of hiding secret data inside a normal image such that the yielded image is almost or completely visually indiscernible from the original. There are numerous types of steganography, but all methods are reversible and difficult to detect. After encoding a message into a file using a steganographic technique, one must still be able to retrieve the secret, hidden data from the output file. Moreover, one must not be able to determine which image contains the secret message.

### What is Pixel Value Differencing (PVD)?
Abstract, modified for clarity, from Wu and Tsai's 2002 paper, "A steganographic method for imagesby pixel-value differencing":

> Pixel Value Differencing is a new and efficient steganographic method for embedding secret messages into a gray-valued cover image. In the process of embedding a secret message, a cover image is partitioned into non-overlapping blocks of two consecutive pixels. A difference value is calculated from the values of the two pixels in each block. All possible difference values are classified into a number of ranges. The selection of the range intervals is based on the characteristics of human visions sensitivity to gray value variations from smoothness to contrast. The difference value then is replaced by a new value to embed the value of a sub-stream of the secret message. The number of bits which can be embedded in a pixel pair is decided by the width of the range that the difference value belongs to. The method is designed in such a way that the modification is never out of the range interval. This method provides an easy way to produce a more imperceptible result than those yielded by simple least-significant-bit replacement methods. The embedded secret message can be extracted from the resulting stego-image without referencing the original cover image. Moreover, a pseudo-random mechanism may be used to achieve secrecy protection. Experimental results show the feasibility of the proposed method. Dual statistics attacks were also conducted to collect related data to show the security of the method.

## Directory Tree

```
Root of PVD-Steganography
├── PVD                                        Python module
│   ├── IO                                     IO directory for the PVD module
│   │   ├── in.png                             Input PNG file
│   │   └── out.png                            Output PNG file
│   ├── deprecated items.py                    Contains deprecated chunks that I might want to reuse later
│   ├── line counter.py                        Counts number of code lines in PVD.py
│   ├── PVD.py                                 Driver script file
│   ├── requirements.txt                       Python module requirements file
│   └── utils.py                               Helper file for PVD.py
├── Research                                   Research directory. Contains explanations of algorithms, any findings I make, etc
│   ├── My Algorithms                          Contains explanations of the variation algorithms I created.
│   │   └── 24-bit RGB PVD.md                  Explains my 24-bit (3, 8-bit channels) RGB PVD variation algorithm
│   ├── Resources                              Contains all files referenced in the README file in the root of the repo
│   │   └── encodedPixels.png                  Fig. 3 in Research/8-bit Single PVD (Wu and Tsai).md
│   │   └── example.png                        Fig. 1 in Research/8-bit Single PVD (Wu and Tsai).md
│   │   └── twoPixels.png                      Fig. 2 in Research/8-bit Single PVD (Wu and Tsai).md
│   ├── 8-bit Single PVD (Wu and Tsai).md      Explains Wu and Tsai's original 8-bit (single black/white channel) PVD algorithm
│   └── README.md                              Description of directory
├── LICENSE.txt                                License
├── README.md                                  This file
└── todo.txt                                   List of items I'd like to complete
```


## Resources

>Wu, Da-Chun, and Wen-Hsiang Tsai. _A Steganographic Method for Images by Pixel Value Differencing_, Pattern Recognition Letters 24 (2003) 1613–1626, 29 Oct. 2001, https://people.cs.nctu.edu.tw/~whtsai/Journal%20Paper%20PDFs/Wu_&_Tsai_PRL_2003.pdf. Accessed 29 April 2021.

> Hameed, Mohamed Abdel, et al. “A High Payload Steganography Method Based on Pixel Value Differencing.” _A High Payload Steganography Method Based on Pixel ValueDifferencing_, 11th International Conference on Informatics and Systems, 10 Dec. 2018, https://ssrn.com/abstract=3389800. Accessed 30 April 2021.
