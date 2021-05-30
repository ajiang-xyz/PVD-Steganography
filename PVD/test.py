import math

quantizationWidths = [
                    [0,1], [2,3], [4,7], [8,11], [12,15], [16,23], [24,31], [32,47], 
                    [48,63], [64,95], [96,127], [128,191], [192,255],
                    ]

valuesCovered = set()
for quantizationWidth in quantizationWidths:
    # Ensure each width is of size one less than a power of 2
    log = math.log(quantizationWidth[1] - quantizationWidth[0] + 1, 2)
    if math.ceil(log) != math.floor(log):
        raise Exception(f"Width of each quantization must be one less than a power of 2 (found width of {quantizationWidth[1] - quantizationWidth[0] + 1} instead)")

    # Ensure no widths overlap
    quantizationWidthSet = range(quantizationWidth[0], quantizationWidth[1] + 1)
    if list(set.intersection(valuesCovered, quantizationWidthSet)) == []:
        # Ranges don't overlap, merge with previously covered values
        valuesCovered = set.union(valuesCovered, quantizationWidthSet)
    else:
        # Ranges overlap
        raise Exception("Quantization ranges must not overlap")
    
# Test to ensure ranges cover all values 0 to 255
if valuesCovered != set(range(0,256)):
    expectedVals = set(range(0,256))
    missing = list(expectedVals - valuesCovered)
    extra = list(valuesCovered - expectedVals)
    if missing != [] and extra != []:
        builtText = f"(missing items {missing} and found extra items {extra} instead)"
    elif missing == []:
        builtText = f"(found extra items {extra} instead)"
    else:
        builtText = f"(missing items {missing} instead)"
    
    raise Exception(f"Quantization ranges must cover all values from 0 to 255 {builtText}")