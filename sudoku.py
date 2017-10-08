#!/usr/bin/env python3
# Sudoku solver
#
from __future__ import print_function
from math import sqrt
from copy import copy, deepcopy
import sys

# Zero means 'not known' in input data, which must be square

'''
#Telegraph - Tough level Oct 7 2017
s=[ [0,0,0, 8,2,0, 0,0,0],
    [0,2,0, 0,0,1, 0,8,0],
    [3,7,0, 0,0,0, 0,0,5],

    [0,0,6, 0,3,0, 0,0,0],
    [7,0,0, 0,6,0, 0,5,9],
    [0,0,0, 0,9,0, 2,7,0],

    [9,0,0, 0,0,0, 0,4,2],
    [0,5,0, 3,0,0, 0,6,0],
    [0,0,0, 0,7,4, 0,0,0]]

# blank
s=[ [0,0,0, 0,0,0, 0,0,0],
    [0,0,0, 0,0,0, 0,0,0],
    [0,0,0, 0,0,0, 0,0,0],

    [0,0,0, 0,0,0, 0,0,0],
    [0,0,0, 0,0,0, 0,0,0],
    [0,0,0, 0,0,0, 0,0,0],

    [0,0,0, 0,0,0, 0,0,0],
    [0,0,0, 0,0,0, 0,0,0],
    [0,0,0, 0,0,0, 0,0,0]]

'''
#Telegraph - Diabolical level no. 4164, 22 Sep 2017
s=[ [6,0,4, 0,9,0, 7,0,3],
    [0,0,3, 0,0,0, 0,6,0],
    [0,0,0, 0,0,0, 0,1,8],

    [0,0,0, 1,8,0, 0,0,9],
    [0,0,0, 0,0,4, 3,0,0],
    [7,0,0, 0,3,9, 0,0,0],

    [0,7,0, 0,0,0, 0,0,0],
    [0,4,0, 0,0,0, 8,0,0],
    [9,0,8, 0,6,0, 4,0,5]]

'''
# "the most difficult puzzle" from academic paper https://www.dcc.fc.up.pt/~acm/sudoku.pdf
s=[ [9,0,0, 8,0,0, 0,0,0],
    [0,0,0, 0,0,0, 5,0,0],
    [0,0,0, 0,0,0, 0,0,0],

    [0,2,0, 0,1,0, 0,0,3],
    [0,1,0, 0,0,0, 0,6,0],
    [0,0,0, 4,0,0, 0,7,0],

    [7,0,8, 6,0,0, 0,0,0],
    [0,0,0, 0,3,0, 1,0,0],
    [4,0,0, 0,0,0, 2,0,0]]
'''
# Functions to map 2D 'human' representation onto linear vector representation, which is easier for machine solving
def toLinear(r,c):
    return r*N + c

def fromLinear(l):
    return [l//N, l%N]

# Return the "cell" number of element (r, c)
# where for example with a 9x9 puzzle, the cell numbers are
# 0 0 0  1 1 1   2 2 2
# 0 0 0  1 1 1   2 2 2
# 0 0 0  1 1 1   2 2 2
# 3 3 3  4 4 4   5 5 5
# 3 3 3  4 4 4   5 5 5
# 3 3 3  4 4 4   5 5 5
# 6 6 6  7 7 7   8 8 8
# 6 6 6  7 7 7   8 8 8
# 6 6 6  7 7 7   8 8 8
def cellOf(r, c):
    return (r//sqrtN)*sqrtN + (c//sqrtN)

# Pretty-printing helper functions
def sudokuHorzLine(ch):
    l = len(prettyElem(all))*N + N + 1
    return ch * l

# work out the longest possible string and format for that, to give monospacing
def prettyElem(e):
    estr = str(e).replace(' ','').replace(',', ' ')
    maxl = len(str(all).replace(' ',''))
    estr = estr.ljust(maxl)
    return estr

# Pretty-print a sudoku possibility-set form
def sudokuPrint(ps):
    try:
        Tposs = 0
        Tunk = 0
        print(sudokuHorzLine('-'))
        for i in range(N):
            print('|', end='', flush=True)
            for j in range(N):
                elem = ps[toLinear(i, j)]
                vstr = prettyElem(elem)
                if (j+1) % sqrtN == 0:
                    sep = '|'
                else:
                    sep = ' '
                print(vstr+sep, end='', flush=True)
                if len(elem) > 1:                   # Counters for remaining possibile values / unknown cells
                    Tunk += 1
                    Tposs += len(elem)
            print()
            if (i+1) % sqrtN == 0:
                print(sudokuHorzLine('-'))
        print('Uncertain cells', Tunk, 'Number of uncertain values:', Tposs)
        return Tposs
    except:
        print('Invalid puzzle - cannot print')
        return None

# solve vectorised puzzle ps by applying logical reduction rules by looking for perfect number rings within rows, columns, 'cells'
def sudokuLogicalSolve(allvec, ps):
    iters = 0
    hits = 1                                    # ensure loop runs at least once
    while hits:
        iters += 1
        hits = 0
        for i, v in enumerate(allvec):
            for j in v:
                elem = ps[j]
                if len(elem) <=3:                 # Check rings of up to specified length
                    exactMatches = set()
                    subsetMatches = set()
                    for k in v:
                        if ps[k] == elem:
                            exactMatches.add(k)
                        elif ps[k].intersection(elem) == elem:
                            subsetMatches.add(k)
                    # check if we have a perfect (length p) ring of p possibilities in our exact matches
                    if len(elem) == len(exactMatches):
                        for l in subsetMatches:
                            ps[l] = ps[l] - elem
                            hits += 1           # we found one this time
    return ps

# check a sudoku is still self-consistent, i.e. no duplicate singleton values, and every value is still possible at least once
def sudokuCheck(allvec, ps, all):
    try:
        errStr = ''
        for i, v in enumerate(allvec):
            singletonValues = set()
            collectedValues = set()
            for j in v:
                elem = ps[j]
                if len(elem) == 1:
                    if singletonValues.intersection(elem):
                        f1 = fromLinear(v[0])
                        f2 = fromLinear(v[-1])
                        f3 = fromLinear(j)
                        errStr = 'In row/col/cell '+str(f1)+' .. '+str(f2)+' : duplicate singleton '+str(elem)+' at '+str(f3)
                        return False, errStr
                    else:
                        singletonValues = singletonValues.union(elem)
                collectedValues = collectedValues.union(elem)
            if collectedValues != all:
                f1 = fromLinear(v[0])
                f2 = fromLinear(v[-1])
                f3 = fromLinear(j)
                errStr = 'In row/col/cell ' + str(f1) + ' .. ' + str(f2) + ' : all values not possible any more ' + str(collectedValues)
                return False, errStr
        return True, errStr
    except:
        print('sudokuCheck function encountered exception:')
        sudokuPrint(ps)
        exit(1)

# Recursively try resolving the possibilities. If puzzle becomes non-consistent then we have to backtrack
def sudokuRecursiveSolve(allvec, ps, all, lvl, starti):
    unknowns = 0
    for i in range(starti, len(ps)):
        elem = ps[i]
        if len(elem) > 1:
            unknowns += 1                           # still got possibilities to resolve - try each in turn
            for j in elem:
                if debug:
                    print('Recursion level', lvl, ': try fixing element', fromLinear(i), 'to', j, end='', flush=True)
                ps[i] = {j}                         # Force element value
                ok, e = sudokuCheck(allvec, ps, all)
                if not ok:
                    if debug:
                        print(e)
                    continue                        # try next j
                if debug:
                    print()
                    print('Applying logical reduction to this candidate')
                ps3 = sudokuLogicalSolve(allvec, copy(ps))
                ok, e = sudokuCheck(allvec, ps3, all)
                if not ok:
                    if debug:
                        print(e)
                    continue                        # try next j
                # Logically OK so far. May still have unknowns. Can start search for possibilities in the i+1th element
                ps3 = sudokuRecursiveSolve(allvec, ps3, all, lvl+1, i+1)
                if ps3:
                    ok, e = sudokuCheck(allvec, ps3, all)
                    if ok:
                        return ps3                  # We've got it
                    else:
                        if debug:
                            print(e)
                        continue                    # try next j
                else:
                    continue                        # try next j

    if unknowns==0:
        return ps
    else:
        return None

# -----------------------------------------------------------------------------------------
# Main code
# -----------------------------------------------------------------------------------------

debug = False
N = len(s)                                  # size of the puzzle
sqrtN = int(sqrt(N))
if (sqrtN **2) != N:
    print('Error: puzzle size', N, 'is not a square number')

# pre-dimension the puzzle contents into linear possibiity-set form, representing as a set. minus one as arrays are zero based
all = set(range(1, N+1))                        # Zero means 'wildcard' i.e. an undefined element
ps = [set() for index in range(toLinear(N-1, N-1) + 1) ]

# build up vectors comprising the set of l-values for each element that belongs in a given row, column and cell
rowvec = [list() for index in range(N)]
colvec = [list() for index in range(N)]
cellvec = [list() for index in range(N)]

for i in range(N):                              # walk all rows
    if len(s[i]) != N:
        print('Error: input data is non-square on row', i)
        exit(1)
    else:
        for j in range(N):                      # walk all columns in this row
            v = s[i][j]
            l = toLinear(i, j)                  # linear index
            rowvec[i].append(l)
            colvec[j].append(l)
            cellvec[cellOf(i, j)].append(l)
            if v==0:
                ps[l] = all.copy()              # Zero values = wildcard
            elif v in all:                      # inputs must lie in the set of possible values
                ps[l] = {v}                     # This element is now certain
            else:
                print('Error: input data in row ', i, 'col', j, 'has value', v)
                exit(1)

# We now have the puzzle, row, column, and cell IDs in linear vector form and can process them. We can treat rows, cols, cells
# exactly the same by deferencing via the vectors.
allvec = rowvec + colvec + cellvec
ps = sudokuLogicalSolve(allvec, ps)             # Get rid of as many possibilities as we can logically
ok, e = sudokuCheck(allvec, ps, all)
if ok:
    ps = sudokuRecursiveSolve(allvec, ps, all, 0, 0)
    print()
    sudokuPrint(ps)
else:
    print(e)
    exit(1)