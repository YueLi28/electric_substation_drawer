from Utility import *
import transformer
import glob
import random
import SizeEstimator
DrawnTail = set()





class Branch:
    def __init__(self, node, fromNode, canv, bus, direction):
        self.node = node
        self.fromNode = fromNode
        self.isReversed = False
        self.isPaired = False
        self.WithinLayout = True
        self.isSingle = True
        self.canvas = canv
        self.parent = bus
        self.ySize = 0
        self.direction = direction
        self.transName = None
        self.hasGen = False

        self.newFindProperty(node, fromNode)

        #SizeEstimator.estimateWidth(self)


    def newFindProperty(self, node, fromNode):
        tails = findTail(node, fromNode)
        if len(tails) > 1:
            self.isSingle = False
        for t in tails:
            if self.parent.cnID in glob.VerticalBusPair and t[-1] == glob.VerticalBusPair[self.parent.cnID]:
                self.isPaired = True
            if self.parent.cnID in glob.HorizontalBusPair and t[-1] == glob.HorizontalBusPair[self.parent.cnID]:
                self.isPaired = True
                self.WithinLayout = False
            if "transformer" in t[-1] and (not self.parent.is32 or self.isSingle):#has transformer
                self.transName = t[-1]
                transObj = findTransformerObj(self.transName)
                if transObj:
                    tgtY = transObj.y
                    if tgtY < self.parent.y:
                        self.direction = "up"
                    else:
                        self.direction = "down"
                elif "two" in t[-1]:
                    otherport = [x for x in glob.adjDict[t[-1]] if "transformer" in x][0]
                    if transformer.Transformer2port.BusConnected(otherport, t[-1]):# Connected to another bus
                        self.direction = reverseDirect(self.direction)
                    else:
                        if transformer.Transformer2port.hasGenerator(otherport, t[-1]):
                            self.direction = "down"
                else:
                    self.direction = reverseDirect(self.direction)
            if "unit" in t[-1]:
                self.hasGen = True
        if not self.transName and self.hasGen:
            self.direction = "down"



    def SetLayout(self, x, y):
        self.x = x
        self.y = y


    def findheadL(self):
        headL = 40
        if self.parent.cnID in glob.VerticalBusPair:
            thisBus = self.parent
            pairY = glob.BusDict[glob.VerticalBusPair[self.parent.cnID]].y
            if self.direction == "up" and thisBus.y > pairY:
                headL += 50
            elif self.direction == "down" and thisBus.y < pairY:
                headL += 50
        return headL


    def draw(self):  #TODO:draw
        if self.node in DrawnTail:
            return
        tmp = findTail(self.node, self.fromNode)
        for each in tmp:
            if each[-1] in glob.BusCNID:
                DrawnTail.add(each[-2])
            # if "two_port_transformer" in each[-1]:
            #     transK =each[-1].split("#")[1].split(".")[0]
            #     if transK in glob.AllTrans:
            #         self.x = glob.AllTrans[transK].x
        headL = self.findheadL()
        if self.isPaired:
            self.drawPair()
        else:
            self.canvas.drawTail(self.x, self.y, self.node, self.fromNode, self.direction, headL)

    def drawPair(self):
        tmp = findTail(self.node, self.fromNode)
        for i in tmp:
            if i[-1] in glob.BusCNID and glob.isPairEnd(i[-1], self.parent.cnID): #draw the pair
                if (len(i) == 2 or len(i) == 4 or len(i) == 6) and not self.parent.is32:#Have Assumed only one pair across 2 lines
                    bridge = i[:-1]
                    newX, newY = self.drawConnection(self.x, self.y, i, self.direction)
                    if not self.isSingle:
                        mididx = len(bridge)/2
                        if "CN" not in bridge[mididx]:
                            self.canvas.drawTail(self.x, newY, bridge[len(bridge) / 2 - 1], bridge, self.direction)
                            self.canvas.drawTail(2*newX - self.x, newY, bridge[len(bridge) / 2 + 1], bridge, self.direction)
                        else:
                            self.canvas.drawTail(newX, newY, bridge[len(bridge)/2], bridge, self.direction)
                    break
                if (len(i) - 18)% 6==  0 :
                    self.draw500Branch(self.x, self.y, i, "up")
                    break
        else:
            #print tmp, len(tmp)
            raise ValueError("ILLEGAL PAIR")

    def find500BranchDirReversed(self, eles):
        for line in eles:
            for e in line:
                if "transformer" in e:
                    return True
        return False

    def draw500Branch(self, x, y, eles, dir):
        color = glob.voltMap[eles[0]]
        newY = y
        dirOffset = 40
        reversedDirOffset = 60
        otherBusY = glob.BusDict[eles[-1]].y
        for i in range(0, len(eles)+1-6, 6):
            seg = eles[i:i+6]
            newY = self.canvas.drawBranch(x, newY, 40, seg, dir)
            if i+6 != len(eles):
                seghead = seg[-1]
                tails = findTail(seghead, eles)
                if len(tails) > 0:
                    tailLength = SizeEstimator.estimateWidth(seghead, eles)
                    if self.find500BranchDirReversed(tails):
                        tgtX, tgtY = self.x + reversedDirOffset, self.y
                        reversedDirOffset+=40+tailLength
                        newDir = "down"
                    else:
                        tgtX, tgtY = self.x + dirOffset, otherBusY
                        newDir = "up"
                        dirOffset += 40 +tailLength
                    self.canvas.drawLine(x, newY, tgtX, newY, color)
                    self.canvas.drawLine(tgtX, newY, tgtX, tgtY, color)
                    self.canvas.drawTail(tgtX, tgtY, seghead, eles, newDir)
            else:
                self.canvas.drawLine(x, newY, x, otherBusY, color)

    def drawConnection(self, posX, posY, connector, direction):
        tgtBus = connector[-1]
        connector = connector[:-1]
        connectorIDX = len(connector)/2
        connectorNode = connector[connectorIDX]
        startX = posX
        startY = posY
        h1=h2=40

        if glob.BusDict[self.parent.cnID].y == glob.BusDict[tgtBus].y:#horizontal pair
            endX = glob.BusDict[tgtBus].x - glob.BusDict[tgtBus].w/2
            offSet = glob.BusDict[self.parent.cnID].x + glob.BusDict[self.parent.cnID].w/2 - startX
            endX += offSet
            endY = startY
        else:#vertical pairs
            endX = startX + glob.nodeSize[cleanElement(connectorNode)][1] + 40
            endY = glob.BusDict[tgtBus].y
            if direction == "up":
                tgt = min(startY, endY) - 40
                h1, h2 = abs(tgt-startY), abs(tgt-endY)
            else:
                tgt = max(startY, endY) + 40
                h1, h2 = abs(tgt - startY), abs(tgt - endY)

        self.canvas.drawBranch(startX, startY, h1, connector[:connectorIDX], direction)
        floatY = self.canvas.drawBranch(endX, endY, h2, connector[connectorIDX+1:][::-1], direction)
        self.canvas.drawFloat(startX, floatY, endX, connectorNode)
        return (endX+startX)/2, floatY