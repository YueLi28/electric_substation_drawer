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