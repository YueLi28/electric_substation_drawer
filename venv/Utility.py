import glob


def findTail(node, fromnodes):
    visited = fromnodes[:]
    lines = []
    findPairTailDFS(node, visited+[node], lines, [node])
    return lines

def findPairTailDFS(node, visited, res, cur):
    if len(glob.adjDict[node]) == 1 or "transformer" in node or node in glob.BusCNID or "ACline" in node:
        res.append(cur)
    else:
        for i in glob.adjDict[node]:
            if i not in visited:
                if i not in glob.BusCNID:
                    visited.append(i)
                findPairTailDFS(i, visited, res, cur + [i])


def reverseDirect(direction):
    if direction == "up":
        return "down"
    else:
        return "up"

def cleanElement(element):
    elementName = element.split("#")[0]
    if elementName == "Disconnector":
        elementName = "daozha"
    if elementName == "Breaker":
        elementName = "kaiguan"
    if elementName == "l_oad" or elementName == "C_P":
        elementName = "singlearrow"
    if elementName == "ACline":
        elementName = "singlearrow"
    if elementName == "two_port_transformer":
        elementName = "transformer2"
    if elementName == "three_port_transformer":
        elementName = "transformer3"
    if elementName == "unit":
        elementName = "generator"
    return elementName

def findTransformerObj(transName):
    transID = transName.split("#")[1].split(".")[0]
    if transID in glob.AllTrans:
        return glob.AllTrans[transID]
    return None

def get32Connection(node, cnID):
    tmp = findTail(node, [cnID])
    for i in tmp:
        if i[-1] in glob.BusCNID and glob.isPair(i[-1], cnID):  # draw the pair
            if match32Feature(i):
                return i
    return None

def match32Feature(eles):
    cleanEles = [x for x in eles if "CN" not in x]
    if len(cleanEles) % 3 != 0:
        return False
    for i in range(0, len(cleanEles),3):
        if "Disconnector" in cleanEles[i] and "Disconnector" in cleanEles[i+2] and "Breaker" in cleanEles[i+1]:
            continue
        else:
            return False
    return True
