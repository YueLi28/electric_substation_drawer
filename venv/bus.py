from branch import *
import Utility


def branchCMP(b1, b2):
    if b1.isPaired and b1.isSingle:
        return -1
    elif b2.isPaired and b2.isSingle:
        return 1
    if b1.isPaired:
        return -1
    elif b2.isPaired:
        return 1
    return 0

def getOtherSideVoltage(transName):
    otherPort = [x for x in glob.adjDict[transName] if "transformer" in x][0]
    return glob.voltMap[otherPort]

def transformerBranchCMP(b1, b2):
    if b1.transName and "three" in b1.transName:
        if Utility.findTransformerObj(b1.transName):
            return -1
        else:
            return 1
    if b2.transName and "three" in b2.transName:
        if Utility.findTransformerObj(b2.transName):
            return 1
        else:
            return -1
    if b1.transName and "two" in b1.transName and b2.transName and "two" in b2.transName:
        return getOtherSideVoltage(b2.transName) - getOtherSideVoltage(b1.transName)
    return 0


def No_Layout_Branch_CMP(b1, b2):
    if b1.isSingle:
        return -1
    return 1



class Bus:
    def __init__(self, x, y, length, cnID, direction, canv):
        self.x = x
        self.y = y
        self.length = length
        self.direction = direction
        self.canvas = canv
        self.cnID = cnID
        self.branches = []
        self.reversedBranches = []
        self.pairBus = None
        self.reversC = False
        self.reversC = glob.BusDict[cnID].reverseC
        self.is32 =glob.BusDict[cnID].is32


    def setPairBus(self, p):
        self.pairBus = p

    def InitializeBranches(self):
        for node in glob.adjDict[self.cnID]:
            if "BUS" not in node:
                b = Branch(node, [self.cnID], self.canvas, self, self.direction)
                if b.direction != self.direction:
                    b.isReversed = True
                if b.isReversed:
                    self.reversedBranches.append(b)
                else:
                    self.branches.append(b)

        if self.is32:
            self.branches += self.reversedBranches
            self.reversedBranches = []
        self.branches.sort(cmp=branchCMP)
        self.reversedBranches.sort(cmp=transformerBranchCMP)

    def generateLayouts(self):
        self.generateLayout(self.branches, self.direction, 0 )
        self.generateLayout(self.reversedBranches, reverseDirect(self.direction), 20)

    def hasLargeBranch(self, branches, gap):
        tmpMAX = 0
        for n in branches:
            tmpMAX = max(n.estimatedSize+50, tmpMAX)
        if tmpMAX > gap:
            return True
        else:
            return False


    def generateLayout(self, branches, direction, offset):
        layout_branches = [b for b in branches if b.WithinLayout]
        not_layout_branches = [b for b in branches if not b.WithinLayout]
        NoBranch = len(layout_branches)
        if NoBranch == 0:
            gap = self.length / 2
        else:
            gap = self.length / NoBranch

        localOffset = (self.length - ((gap * (NoBranch - 1)) )) / 2
        xStart = self.x - self.length / 2 + localOffset + offset
        if self.cnID in glob.VerticalBusPair and self.cnID < glob.VerticalBusPair[self.cnID]:
            xStart -= 30
        hasLargeB =  self.hasLargeBranch(layout_branches, gap)
        for n in layout_branches:
            n.SetLayout(xStart, self.y)
            #xStart += gap
            if hasLargeB:
                xStart += n.estimatedSize+100
            else:
                xStart += gap
        if len(not_layout_branches) > 2:
            print [x.node for x in not_layout_branches]
            raise ValueError("I do not know how to draw this")
        tmpdir = direction
        not_layout_branches.sort(cmp=No_Layout_Branch_CMP)
        ct = 1
        for n in not_layout_branches:
            tmpdir = reverseDirect(tmpdir)
            if self.reversC:
                tmpdir = reverseDirect(tmpdir)
            n.SetLayout(self.x+self.length/2-15*ct, self.y)
            n.direction = tmpdir
            ct+=1


    def getDimension(self):
        return [self.x, self.y, self.length]

    def draw(self):
        self.InitializeBranches()
        self.generateLayouts()
        self.canvas.drawLine(self.x - self.length / 2 , self.y, self.x + self.length / 2 , self.y, glob.voltMap[self.cnID], 15)
        for each in self.branches:
            each.draw()
        for each in self.reversedBranches:
            each.draw()
