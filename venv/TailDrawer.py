from Utility import *
import SizeEstimator
import glob



class TailDrawer:
    def __init__(self, x, y, node, fromNodes, direction, canv, headLength=40):
        self.x = x
        self.y = y
        self.node = node
        self.fromNodes = fromNodes
        self.direction = direction
        self.headL = headLength
        self.canvas = canv



    def findSinglePath(self, node, fromNodes):
        res = []
        isEnd = True
        future = [x for x in glob.adjDict[node] if x not in fromNodes]
        while len(future) == 1 and "transformer" not in node and "ACline" not in node:
            res+=[node]
            node, fromNodes = future[0], [node]
            future = [x for x in glob.adjDict[node] if x not in  fromNodes]
        res += [node]
        if node in glob.BusCNID or node in glob.CNpos:
            isEnd = True
        else:
            if len(future) >= 2:
                isEnd = False
        return res, isEnd



    def newDraw(self, node, fromNodes, x, y, dir):
        if node in glob.drawnNode:
            return
        compHead = False
        neighbors = [i for i in glob.adjDict[node] if i not in fromNodes]
        tgtY = 0
        volt = glob.voltMap[node]
        if len(neighbors) == 0:
            self.drawBranch(x, y, self.headL, [node], dir)
        elif len(neighbors) == 1:
            #print "DRAW: ", node, "FROM", fromNode
            path, isEnd = self.findSinglePath(node, fromNodes)
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
                self.canvas.drawLine(x,newY,x,tgtY,volt)

        else:
            paths = [self.findSinglePath(i, [node]) for i in neighbors]
            onlyPaths = [i[0] for i in paths]
            direct,right = self.findDirectTail(onlyPaths)
            offset = 0
            for p in direct:
                self.newDraw(p[0], [node], x, y, dir)
                offset = SizeEstimator.estimateWidth(p[0], [node])
            for p in right:
                x += 40 + offset
                self.canvas.drawLine(x-40-offset, y, x, y,volt)
                #print p[0], [node]
                self.newDraw(p[0], [node], x, y, dir)
                offset = SizeEstimator.estimateWidth(p[0], [node])




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