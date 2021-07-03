import sys
import os

def countCode(filepath):
    with open(filepath,"r") as file:
        code = 0
        lines = 0
        for line in file:
            if line.strip() != "" and "#" not in line.strip():
                code += 1
            lines += 1
        print(f"{code} out of {lines} lines in \"{filepath}\" are code")
        return code, lines

def main():
    totalCode = 0
    totalLines = 0
    fileCount = 0
    try:
        path = sys.argv[1]
    except:
        path = "."
    files = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
    for filename in files:
        code, lines = countCode(os.path.join(path, filename))
        totalCode += code
        totalLines += lines
        fileCount += 1
    print(f"\n{totalCode} lines out of {totalLines} total lines ({round(100*totalCode/totalLines, 2)}%) across {fileCount} files in \"{path}\" are code")

main()