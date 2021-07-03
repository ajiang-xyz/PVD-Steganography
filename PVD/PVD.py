from prompt_toolkit import prompt
from rgbChannels import *
from typing import *
import argparse
import datetime
import imghdr
import signal
import ast

def getHelp(specificOption=None):
    """
    Basic help information
    """

    helpDictionary = {
            "default":"""This program uses a custom PVD steganography algorithm to embed and retrieve data from PNG files

Type 'help <category name>' to view all options for a specific category
    Currently available categories: 'interactive', 'universal', 'embed', 'retrieve'

    Example: help interactive""",
            "interactive":"""In order to enter interactive mode, simply run the progran as follows:
    PVD.py interactive

Interactive mode commands:
    Type 'exit' to exit this program
    Type 'clear' to clear the screen
    Type 'help' to receive this help message again
    Type 'credits' to see credits for this program
    Type 'license' to see the license for this project
    Type 'cwd' to see the current working directory
    Type 'files' to see all png files in the current working directory""",
            "categoryHeader":"""Tilde'd options have additional information that can be accessed via 'help <long option name>'
    Example: help quantization

Starred options are optional""",
            "universal":"""Universal options:
    --infile/-i <filename>                 name of input image to read pixel values from
    --outfile/-o <filename> OR 'stdout'    name of output image to write encoded pixel values to OR output to standard out       
~   --quantization/-q <widths>             width classifications to determine amount of data to encode
~   --traversal/-t <order>                 order to traverse pixel pairs for RGB images
*   --verbose/-v                           enable verbose messages""",
            "embed":"""Embed specific options:
    --message/-m <message>                 message to embed in input image
~*  --verify/-V                            add verification data to PNG properties

Example usage:
    embed --infile in.png --out out.png --message hello world! --verbose
    embed -o out.png -i in.png -m banana fish -v -V
    embed -V -o out.png -m banana fish -i in.png -v""",
            "retrieve":"""Retrieve specific options:
~*  --verify/-V                            use verification data in PNG properties to verify retrieved binary

Example usage:
    retrieve --in out.png --out stdout --verify --verbose
    retrieve -o message.txt -i out.png -v -V""",
            "quantization":"""Quantization widths format:""",
            "traversal":"""foobar 2""",
            "verify":"""foobar 3""",
    }
    if specificOption:
        try:
            if specificOption in ["universal", "embed", "retrieve"]:
                print(helpDictionary["categoryHeader"])
            print(helpDictionary[specificOption])
        except:
            print(f"'{specificOption}' does not have any help information")
        
    else:
        print(helpDictionary["default"])

    return

def progCreds():
    """
    Program credits
    """

    print("""Written by Alex Jiang (@ajiang-xyz on GitHub, syossu#2202 on Discord)""")

def progCopyright():
    """
    Program copyright
    """

    print("""Copyright (c) 2021 Alex Jiang.
All Rights Reserved.""")

def progLicense():
    """
    Program license
    """

    print("See https://github.com/ajiang-xyz/PVD-Steganography/blob/main/LICENSE.txt")

def getWorkingDictory():
    """
    Print cwd
    """

    print(os.getcwd())

def printFiles():
    """
    Print all png and bmp files in cwd
    """

    # Get all files that are of type png and bmp
    files = [file for file in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), file)) and imghdr.what(file) in ["png", "bmp"]]

    if len(files) == 0:
        print(f"No png files in this directory {os.getcwd()}")
    else:
        print(f"Found {len(files)} png files in {os.getcwd()}:")
        files = sorted([str(item) for item in files])

        # Get terminal size
        columns = os.get_terminal_size()[0]
        columnWidth = int(columns/3)

        # Add padding names
        if len(files) % 3 != 0:
            for i in range(3-(len(files) % 3)):
                files.append(" ")

        # Print into columns, truncate if needed
        for count, item in enumerate(files, 1):
            if len(item) > columnWidth:
                item = f"{item[:columnWidth-5]}..."
            print(item.ljust(columnWidth), end="")
            if count % 3 == 0:
                print()

def parseAction(parsed):
    """
    Given some input action object, perform designated function on values
    """

    parameterlessCommandDict = {
        "exit":exit,
        "clear":clearBuffer,
        "credits":progCreds,
        "copyright":progCopyright,
        "license":progLicense,
        "cwd":getWorkingDictory,
        "files":printFiles
    }

    if parsed.action:
        # If action has designated handler function, call it
        if parsed.action in parameterlessCommandDict:
            parameterlessCommandDict[parsed.action]()
        elif parsed.action == "help":
            # Parse help arguments
            getHelp(parsed.specificOption[0])
        else:
            # Evaluate str representation of nested arrays into nested arrays
            parsed.quantization = ast.literal_eval(parsed.quantization)
            parsed.traversal = ast.literal_eval(parsed.traversal)

            errors = []

            # Cleanse / verify validity of arguments
            if parsed.action == "embed":
                if parsed.message == "":
                    errors.append("Must input a message to encode")
            if parsed.action == "retrieve":
                if parsed.outfile == "":
                    parsed.outfile = "stdout"
                parsed.message = ""

            # Ensure outfile is writeable
            if parsed.outfile:
                path = os.path.split(parsed.outfile)[0]
                if path and not os.path.isdir(path):
                    errors.append(f"Invalid out file path: '{parsed.outfile}' (can't write to {path})")
            else:
                errors.append(f"Must input an out file name")

            # Ensure infile exists and is correct filetype
            if parsed.infile:
                if not os.path.exists(parsed.infile):
                    # Check if exists
                    errors.append(f"Invalid in file path: '{parsed.infile}' (does not exist)")
                elif imghdr.what(parsed.infile) not in ["png", "bmp"]:
                    # Check filetype
                    errors.append(f"Invalid in file format: '{parsed.infile}' (must be png or bmp)")
            else:
                errors.append(f"Must input an in file name")

            if errors != []:
                for error in errors:
                    print(error)
            else:
                preTime = int(round(time.time() * 1000))
                infile = PIL.Image.open(parsed.infile)
                returnValue = rgbChannels(inFile=infile, outFile=parsed.outfile, message=" ".join(parsed.message), verify=parsed.verify, verbose=parsed.verbose)
                print()
                if isinstance(returnValue, bool):
                    if returnValue == True:
                        print("Done.")
                    else:
                        print("Completed with errors.")
                else:
                    print("Done.")

                    # Print binary to console or write to file
                    if parsed.outfile == "stdout":
                        print(f"Retrieved binary: {returnValue}")
                    else:
                        with open(parsed.outfile, "wb") as out:
                            out.write(int(returnValue, 2).to_bytes((len(returnValue) + 7) // 8, byteorder="big"))
                postTime = int(round(time.time() * 1000))
                print(f"Time elapsed: {postTime - preTime} ms")

def interactive():
    """
    Interactive command prompt
    """

    signal.signal(signal.SIGINT, ctrlCHandler)

    # Get all the current time and date info
    currentYear = datetime.date.today().year
    currentMonth = datetime.date.today().month
    currentMonth = datetime.date(currentYear, currentMonth, 1).strftime("%b")
    currentDay = datetime.date.today().day
    time = datetime.datetime.now().strftime("%H:%M").split(":")
    currentTime = ""
    if int(time[0]) - 12 > 0:
        currentTime += str(int(time[0]) - 12)
        currentTime += ":" + time[1]
        currentTime += " PM"
    else:
        currentTime += time[0]
        currentTime += ":" + time[1]
        currentTime += "AM"

    # Display all the fancy stuffs :D
    print("""PVD Beta (built on Python) {1} {2} {3}, {0}
Type "help", "copyright", "credits" or "license" for more information.""".format(currentTime, currentMonth, currentDay, currentYear))

    while True:
        try:
            command = prompt("PVD >>> ").strip()
            parsed = parseInteractiveArgs(command)
            parseAction(parsed)
        except KeyboardInterrupt:
            print("")
            exit()

class ArgumentParser(argparse.ArgumentParser):
    """
    Override argparse.ArgumentParser's error function (custom error handling)
    """

    def error(self, message):
        pass

def ctrlCHandler(sig, frame):
    """
    Graceful exit
    """

    print("")
    exit()

def parseInteractiveArgs(string):
    """
    Parse commands passed into interactive program
    """

    # Instantiate parser class
    parser = ArgumentParser(prog="PVD interactive")

    # Add shared arguments for embed and retrieve actions
    parent = ArgumentParser(add_help=False)
    parent.add_argument("-i", "--infile", metavar="infile", default="")
    parent.add_argument("-o", "--outfile", metavar="outfile", default="")
    parent.add_argument("-q", "--quantization", default="[[0,1], [2,3], [4,7], [8,11], [12,15], [16,23], [24,31], [32,47], [48,63], [64,95], [96,127], [128,191], [192,255]]")
    parent.add_argument("-t", "--traversal", default="[1,3,5,2,4,6]")
    parent.add_argument("-V", "--verify", action="store_true", default=False)
    parent.add_argument("-v", "--verbose", action="store_true", default=False)

    # Create different actions and arguments
    subparsers = parser.add_subparsers(title="actions", dest="action")

    # Define embed action, inherit parent arguments, and define unique arguments
    encodeParser = subparsers.add_parser("embed", parents=[parent])
    encodeParser.add_argument("-m", "--message", metavar="message", nargs="*", default="")

    # Define retrieve action, inherit parent arguments, and define unique arguments
    retrieveParser = subparsers.add_parser("retrieve", parents=[parent])

    # Define help messages
    helpParser = subparsers.add_parser("help")
    helpParser.add_argument("specificOption", default=["default"], nargs="*")

    # Define basic actions
    subparsers.add_parser("exit")
    subparsers.add_parser("clear")
    subparsers.add_parser("credits")
    subparsers.add_parser("copyright")
    subparsers.add_parser("license")
    subparsers.add_parser("cwd")
    subparsers.add_parser("files")

    # Parse args passed into file
    try:
        args = parser.parse_args(string.split())
        return args
    except:
        print(f"Invalid command: '{string.split()[0]}'")
        return parser.parse_args("")

if __name__ == "__main__":
    interactive()

# def parseFileArgs(string):
#     # Instantiate parser class
#     parser = ArgumentParser(prog="PVD file")

#     # Add shared arguments for embed and retrieve actions
#     parent = ArgumentParser(add_help=False)
#     parent.add_argument("-i", "--infile", metavar="infile", default="")
#     parent.add_argument("-o", "--outfile", metavar="outfile", default="")
#     parent.add_argument("-q", "--quantization", default="[[0,1], [2,3], [4,7], [8,11], [12,15], [16,23], [24,31], [32,47], [48,63], [64,95], [96,127], [128,191], [192,255]]")
#     parent.add_argument("-t", "--traversal", default="[1,3,5,2,4,6]")
#     parent.add_argument("-V", "--verify", action="store_true", default=False)
#     parent.add_argument("-v", "--verbose", action="store_true", default=False)

#     # Create different actions and arguments
#     subparsers = parser.add_subparsers(title="actions", dest="action")

#     # Define embed action, inherit parent arguments, and define unique arguments
#     encodeParser = subparsers.add_parser("embed", parents=[parent])
#     encodeParser.add_argument("-m", "--message", metavar="message", default="")

#     # Define retrieve action, inherit parent arguments, and define unique arguments
#     retrieveParser = subparsers.add_parser("retrieve", parents=[parent])

#     # Define interactive mode action
#     subparsers.add_parser("interactive")

#     # Define help messages
#     helpParser = subparsers.add_parser("help")
#     helpParser.add_argument("specificOption", default=["default"], nargs="*")

#     # Parse args passed into file
#     try:
#         args = parser.parse_args(string.split())
#         return args
#     except:
#         print(f"Invalid command: '{string.split()[0]}'")