from Utility import *
import glob



class TailDrawer:
    def __init__(self, x, y, node, fromNodes, direction, canv, headLength=40):
        self.x = x
        self.y = y
        self.node = node
        self.fromNodes = fromNodes[0]
        self.direction = direction
        self.headL = headLength
        self.canvas = canv
        if len(fromNodes)>1:
            raise ValueError("fromNodes size too large!")


    def findSinglePath(self, node, fromNode):
        res = []
        isEnd = True
        future = [x for x in glob.adjDict[node] if x != fromNode]
        while len(future) == 1 and "transformer" not in node and "ACline" not in node:
            res+=[node]
            node, fromNode = future[0], node
            future = [x for x in glob.adjDict[node] if x != fromNode]
        res += [node]
        if node in glob.BusCNID:
            isEnd = True
        else:
            if len(future) >= 2:
                isEnd = False
        return res, isEnd



    def newDraw(self, node, fromNode, x, y, dir):
        compHead = False
        neighbors = [i for i in glob.adjDict[node] if i != fromNode]
        tgtY = 0
        if len(neighbors) == 0:
            self.drawBranch(x, y, self.headL, [node], dir)
        elif len(neighbors) == 1:
            #print "DRAW: ", node, "FROM", fromNode
            path, isEnd = self.findSinglePath(node, fromNode)
            newDir = dir
            if path[-1] in glob.BusDict:
                compHead = True
                tgtY = glob.BusDict[path[-1]].y
                if tgtY > y:
                    newDir = "down"
                else:
                    newDir = "up"
            newY = self.drawBranch(x, y, self.headL, path, newDir)
            if not isEnd:
                self.newDraw(path[-1], path[-2], x, newY, newDir)
            elif compHead:
                self.drawLine(x,newY,x,tgtY)
        else:
            paths = [self.findSinglePath(i, node) for i in neighbors]
            onlyPaths = [i[0] for i in paths]
            direct,right = self.findDirectTail(onlyPaths)
            for p in direct:
                self.newDraw(p[0], node, x, y, dir)
            for p in right:
                x += 40
                self.drawLine(x-40, y, x, y)
                self.newDraw(p[0], node, x, y, dir)




    def findDirectTail(self, paths):
        direct = []
        seconddirect = []
        right = []
        for path in paths:
            tmp = map(self.cleanElement, path)
            if "generator" in tmp or "transformer2" in tmp or "transformer3" in tmp:
                direct.append(path)
            elif "singlearrow" in tmp:
                seconddirect.append(path)
            else:
                right.append(path)

        tmp = direct+seconddirect + right
        if len(tmp) > 0:
            direct = tmp[:1]
            right = tmp[1:]
        return direct, right




    def draw(self):
        self.newDraw(self.node, self.fromNodes, self.x, self.y, self.direction)

    def drawBranch(self, a1, a2, a3, a4, a5):
        return self.canvas.drawBranch(a1,a2,a3,a4,a5)
    def drawLine(self, a1, a2, a3, a4):
        return self.canvas.drawLine(a1, a2, a3, a4)

    def cleanElement(self, element):
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