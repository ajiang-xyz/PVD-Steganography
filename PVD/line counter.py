import sys
with open(sys.argv[1],'r') as D:
    B=0;C=0
    for A in D:
        if A.strip()!=''and'#'not in A.strip():B,C=B+1,C+1
    print(f'{B} out of {C} lines in "{sys.argv[1]}" are code')