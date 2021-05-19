with open("./pvd.py", "r") as pvd:
    count = 0
    for line in pvd:
        line = line.strip()
        if line != "" and "#" not in line:
            count += 1

    print(f"There are {count} lines in PVD.py")