import glob



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
    if node == "Disconnector#8336":
        print "XXXX"
        for t in tails:
            print t
    return (len(tails)-1) * 40


