import sys
with open(sys.argv[1],"r") as file:
    code = 0
    lines = 0
    for line in file:
        if line.strip() != "" and "#" not in line.strip():
            code += 1
        lines += 1
    print(f'{code} out of {lines} lines in "{sys.argv[1]}" are code')