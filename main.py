import numpy as np
import heapq
import time
from playsound import playsound

global entryCount # tracks the entry number of a state, to break ties

# functions as a struct to hold state information
class State:
    pass

# main program
def main():
    print("Welcome to my 9-men in a trench solver.")

    # Get user input on whether to use the original puzzle or enter a new one
    print("Manually enter puzzle or use original?")
    print("\t1. Enter manually")
    print("\t2. Use original")
    val = int(input())
    while(val != 1 and val != 2):
        print("Invalid Input")
        print("Manually enter puzzle or use original?")
        print("\t1. Enter manually")
        print("\t2. Use original")
        val = int(input())
    
    # intialize the trench to the users liking
    if(val == 1):
        init = manual() # user enters own trench state
    elif(val == 2):
        init = initalize() # initializes state to original puzzle
    else:
        exit(1)

    # User picks an algorithm
    print("Enter the algorithm choice:")
    print("\t1. Uniform Cost Search")
    print("\t2. In the way + Misplaced man heuristic (no pruning)")
    print("\t3. In the way + Misplaced man heuristic (with pruning)")
    alg = int(input())
    while(alg != 1 and alg != 2 and alg != 3):
        print("Invalid Input")
        print("Enter the algorithm choice:")
        print("\t1. Uniform Cost Search")
        print("\t2. In the way + Misplaced man heuristic (no pruning)")
        print("\t3. In the way + Misplaced man heuristic (with pruning)")
        alg = int(input())

    print("Trace Program? (Warning: not advisable on hard puzzles)")
    print("\t1. Yes")
    print("\t2. No")
    trace = int(input())
    while(trace != 1 and trace != 2):
        print("Invalid Input")
        print("Trace Program? (Warning: not advisable on hard puzzles)")
        print("\t1. Yes")
        print("\t2. No")
        trace = int(input())

    # initalize the state with the given trench
    initState = State()
    initState.g = 0
    initState.h = heuristic(init, alg)
    initState.trench = init
    initState.moves = []

    # Run the search
    start = time.time()
    solution, qSize, expanded = search(initState, alg, trace) # returns list of moves to get to solution
    end = time.time()
    print("Time: {:.2f}s".format(end-start)) # print time it takes to search
    print("Maximum Queue Size:", qSize)
    print("# Nodes Expanded:", expanded)
    print()

    print("Solution:")
    for move in solution:
        print("(%d,%d) to (%d,%d)"%(move[0], move[1], move[2], move[3]))

    playsound('audio.mp3')

# intializes puzzle to original state
def initalize():
    state = np.zeros((2,10))
    for i in range(10):
        state[0][i] = -1
        state[1][i] = i+1
    state[1][0] = 0
    state[1][9] = 1
    state[0][3] = 0
    state[0][5] = 0
    state[0][7] = 0
    return state

# lets the user enter their own puzzle
def manual():
    # initial array setup
    state = np.zeros((2,10))
    for i in range(10):
        state[0][i] = -1

    # loop until user accepts a puzzle as correct
    while(True):
        # get the state of the top 3 pockets
        print("Enter the state of the top row (where the three pockets are) from left to right")
        print("Warning: Enter exactly 3 numbers range 1-9, use 0 to represent empty space, put a space to seperate numbers")
        vals = input("\tTop Row: ")
        state[0][3] = float(vals[0])
        state[0][5] = float(vals[2])
        state[0][7] = float(vals[4])

        # get the state of the rest of the trench
        print("Enter the state of the bottom row (the main trench) from left to right")
        print("Warning: Enter exactly 10 numbers range 1-9, use 0 to represent empty space, put a space to seperate numbers")
        vals = input("\tBottom Row: ")
        state[1][0] = float(vals[0])
        state[1][1] = float(vals[2])
        state[1][2] = float(vals[4])
        state[1][3] = float(vals[6])
        state[1][4] = float(vals[8])
        state[1][5] = float(vals[10])
        state[1][6] = float(vals[12])
        state[1][7] = float(vals[14])
        state[1][8] = float(vals[16])
        state[1][9] = float(vals[18])

        # Ask if the puzzle is correct. If not, the user can re-enter the puzzle
        print("Is this your puzzle?")
        printTrench(state)
        print("\t1. Yes")
        print("\t2. No")
        val = int(input())
        while(val != 1 and val != 2):
            print("Invalid Input")
            print("Is this your puzzle?")
            printTrench(state)
            print("\t1. Yes")
            print("\t2. No")
            val = int(input())
        if(val == 1):
            return state
        elif(val == 2):
            continue
        else:
            exit(1)

# calculates the heuristic (in the way + mispaced man is briefly explained, but explained in full in the report)
def heuristic(trench, alg):
    h = 0

    # if alg is UCS, heauristic is 0
    if(alg == 1):
        return h

    # else, perform the in the way + misplaced man heuristic
    result = np.where(trench == 1) # fins location of man 1
    col = int(result[1]) # get column location
    if(int(result[0]) == 0): # if man 1 is in the top row, get column to the right
        col += 1

    # for every column to the left of man 1
    for j in range(col):
        # if there is a man in the way (since man 1 goal is the first column), they must make at least 
        # two moves to clear the way for man 1 to move, then for them to move into the correct position
        if(trench[1][j] > 0): 
            h += 2
        # if any pockets to the left of man 1 (including himself if he is in a pocket) has a man
        # then they must make at least one move to be put in the correct position
        if(trench[0][j] > 0): 
            h += 1
    
    # for every column to the right of man 1
    # if the man is not in the correct position, it takes at least one move to put them there
    for j in range(col, 9):
        if((trench[1][j] > 0) and (trench[1][j] != (j+1))):
            h += 1
        if(trench[0][j] > 0):
            h += 1
    if(trench[1][9] > 0):
        h += 1
    return h

def search(initState, alg, trace):
    global entryCount
    entryCount = 0 # initalize entry count
    q = [] # priority queue
    heapq.heappush(q, ((initState.g + initState.h), entryCount, initState)) # push initial state onto queue
    entryCount+=1

    # setup goal state
    goal = np.zeros((2,10))
    for i in range(10):
        goal[0][i] = -1
        goal[1][i] = i+1
    goal[1][9] = 0
    goal[0][3] = 0
    goal[0][5] = 0
    goal[0][7] = 0

    checkedTrenches = [] # hold checked states
    maxQueueSize = 1 # holds max number of nodes in the queue
    nodesExpanded = 0 # holds number of nodes expanded

    while (len(q) > 0): # Loop while queue is not empty
        item = heapq.heappop(q)
        curState = item[2] # get current state

        if(duplicateCheck(curState.trench, checkedTrenches)): # so we dont expand states we already expanded
            continue

        if(alg == 3):
            if(prune(curState)): # prune a state if not ideal and pruning is enabled
                continue

        if (np.array_equal(curState.trench, goal)): # Test if state is the goal
            if(trace == 1):
                print("The best state to expand with a g(n) = %d and h(n) = %d is…"%(curState.g, curState.h))
                printTrench(curState.trench)
            print("Goal state found!")
            return curState.moves, maxQueueSize, nodesExpanded # return moves as solution if true
        else:
            if(trace == 1):
                print("The best state to expand with a g(n) = %d and h(n) = %d is…"%(curState.g, curState.h))
                printTrench(curState.trench)
            expand(curState, q, alg) # expand state if false
            nodesExpanded += 1

        checkedTrenches.append(curState.trench) # add trench to checked trenches
        if(len(q) > maxQueueSize): # get new max queue size
            maxQueueSize = len(q)

    print("No Solution") # print error if no solution
    return

# checks if trench has been expanded before
def duplicateCheck(cur, checked):
    for trench in checked:
        if(np.array_equal(cur, trench)):
            return True
    return False

# expands a state
def expand(state, q, alg):
    global entryCount
    trench = state.trench

    for i in range(trench.shape[0]):
        for j in range(trench.shape[1]):
            if(trench[i][j] == 0): # for every empty space in the trench
                neighbors = getValidNeighbors(trench, i, j) # find which men can move to it
                for n in neighbors: # for every man that can move to the empty space
                    # make the move, calculate the h and g, append the move to moves list, push to queue
                    child = stateCopy(state)
                    child.trench[i][j] = trench[n[0]][n[1]]
                    child.trench[n[0]][n[1]] = 0
                    child.g += 1
                    child.h = heuristic(child.trench, alg)
                    child.moves.append((n[0], n[1], i, j))
                    heapq.heappush(q, ((child.g + child.h), entryCount, child))
                    entryCount += 1
             
    return

# finds all men that can move to the given space (will only be called on empty spaces)
def getValidNeighbors(t, i, j):
    neighbors = []
    trench = t.copy()
    trench[i][j] = -1

    if((i > 0) and (trench[i-1][j] >= 0)): # if space above is empty or has a man, add
        neighbors.append((i-1,j))

    if((i < trench.shape[0]-1) and (trench[i+1][j] >= 0)): # if space below is empty or has a man, add
        neighbors.append((i+1,j))

    if((j > 0) and (trench[i][j-1] >= 0)): # if space to the left is empty or has a man, add
        neighbors.append((i,j-1))

    if((j < trench.shape[1]-1) and (trench[i][j+1] >= 0)): # if space to the right is empty or has a man, add
        neighbors.append((i,j+1))

    neighbors2 = neighbors.copy()
    
    # recurively calls this function until the list has no empty spaces (a man can move through any amount of empty space as one move)
    for n in neighbors2: # for each empty space or man added
        if(trench[n[0]][n[1]] == 0): # if an empty space was added
            neighbors.extend(getValidNeighbors(trench, n[0], n[1])) # add all the men touching that space
            neighbors.remove((n[0],n[1])) # remove the empty space

    return neighbors

# prunes a state when one of the following two conditions is met:
# the bottom row of the trench has men not in ascending order, excluding man 1
def prune(state):
    trench = state.trench
    cur = 0
    while(trench[1][cur] == 0):
        cur += 1 # locate leftmost man
    nxt = cur + 1 # get his immediate right
    while(nxt <= 9): # until we reach the end of the trench
        if(trench[1][nxt] <= 1): # if the space to the right is empty or man 1, move right again
            nxt += 1
            continue
        if(trench[1][nxt] < trench[1][cur]): # check if the men are in ascending order
            return True
        cur = nxt # next next man and his immediate right
        nxt += 1
    return False

# returns a copy of a state 
def stateCopy(state):
    s = State()
    s.g = state.g
    s.h = state.h
    s.trench = state.trench.copy()
    s.moves = state.moves.copy()
    return s

# prints out a nicely formatted trench
def printTrench(trench):
    t = ""
    for i in range(trench.shape[0]):
        for j in range(trench.shape[1]):
            if(trench[i][j] >= 0):
                t += str(int(trench[i][j])) + " "
            else:
                t += "  "
        t += "\n"
    print(t)

main() # call main program