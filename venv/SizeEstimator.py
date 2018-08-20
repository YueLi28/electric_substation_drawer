import glob
import Utility



def findAllTail(node, fromnodes):
    visited = fromnodes[:]
    lines = []
    findPairTailDFS(node, visited+[node], lines, [node])
    return lines

def findPairTailDFS(node, visited, res, cur):
    if len(glob.adjDict[node]) == 1 or node in glob.BusCNID or "ACline" in node:
        res.append(cur)
    else:
        for i in glob.adjDict[node]:
            if i not in visited:
                if i not in glob.BusCNID:
                    visited.append(i)
                findPairTailDFS(i, visited, res, cur + [i])

def estimateWidth(node, fromNodes):
    tails = findAllTail(node, fromNodes)
    return (len(tails)-1) * 40

def estimateLeftWidth(node, cnID):
    i = Utility.get32Connection(node, cnID)
    if i:
        return estimate32Side(i, True)
    else:
        return 0

def estimateRightWidth(node, cnID):
    i = Utility.get32Connection(node, cnID)
    if i:
        return estimate32Side(i, False)
    else:
        return estimateWidth(node, [cnID])

def estimate32Side(eles, isLeft):
    leftEdge = 0
    rightEdge = 0
    turn = True
    for i in range(0, len(eles) + 1 - 6, 6):
        seg = eles[i:i + 6]
        if i + 6 != len(eles):
            seghead = seg[-1]
            tails = Utility.findTail(seghead, eles)
            if len(tails) > 0:
                tailLength = estimateWidth(seghead, eles)
                if turn:  # branch to left
                    # if i != 0:  # first turn, no need to offset
                    leftEdge += tailLength + 40
                else:
                    rightEdge += tailLength + 40
                turn = not turn
    if isLeft:
        return leftEdge
    else:
        return rightEdge
