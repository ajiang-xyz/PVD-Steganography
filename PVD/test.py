print("Executing...")

storableCount = 69420

power = 1024
counter = 0
labels = {0 : "", 1: "K", 2: "M", 3: "G", 4: "T", 5:"P"}
while storableCount > power:
    storableCount /= power
    counter += 1
print(f"{storableCount} {labels[counter]}B")

# def logisticMap(currentTerm, r, numberToCalculate):
#     if numberToCalculate == 0:
#         return currentTerm
#     else:
#         return logisticMap(r*currentTerm*(1-currentTerm), r, numberToCalculate-1)

# # pixel pair
# def pixelRandom(pair):
#     difference = abs(pair[1] - pair[0])

#     # logistic map
#     currentTerm = (0.99999-0.00001)*(difference)/(255)+0.00001

#     # scale difference to some value between approximate beginning of chaos in logistic map to the value just below divergence
#     r = (3.99999-3.56998)*(difference^5)/(255)+3.56998

#     # calculate bit flip of difference for number of terms to calculate
#     numberToCalculate = 500 # int(bin((difference ^ (2 ** (difference.bit_length()+1) - 1)))[3:], 2)

#     # print(f"current term: {currentTerm}\nr: {r}\nnumber to calculate: {numberToCalculate}")

#     testing = logisticMap(currentTerm, r, numberToCalculate)
#     # print(f"final value: {testing}")
#     return testing

# import random
# def calculatePercent():
#     counter = {str(i):0 for i in range(10)}
#     for i in range(50000):
#         pair = [random.randint(0, 255), random.randint(0, 255)]
#         if pair[1] != pair[0]:
#             randomValue = pixelRandom(pair)
#             counter[str(randomValue)[2]] += 1

#     valueCount = sum(counter.values())
#     returnList = []
#     for count in counter:
#         returnList.append(counter[count]/valueCount*100)
#     return returnList

# counter = calculatePercent()
# for i in range(1):
#     returnList = calculatePercent()
#     counter = [(pair[0]+pair[1])/2 for pair in list(zip(counter, returnList))]
#     print(counter)

# testing = list(dict(sorted(dict(zip(counter, [0,1,2,3,4,5,6,7,8,9])).items())).values())
# print(testing[::-1])
        



# # finalTerms = []
# # for i in range(10000):
# #     pair = [random.randint(0, 255), random.randint(0, 255)]
# #     if pair[1] != pair[0]:
# #         # print(f"pair: {pair}")
# #         randomValue = pixelRandom(pair)
# #         finalTerms.append(str(randomValue)[2])
# #     # print()