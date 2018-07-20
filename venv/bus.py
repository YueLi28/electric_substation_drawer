import glob
from branch import *



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

def transformerBranchCMP(b1, b2):
    if b1.isReversed and "three" in b1.transName:
        return 1
    if b2.isReversed and "three" in b2.transName:
        return -1
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
                b = Branch(node, [self.cnID], self.canvas, self)
                if b.isReversed:
                    self.reversedBranches.append(b)
                else:
                    self.branches.append(b)
        self.branches.sort(cmp=branchCMP)
        self.reversedBranches.sort(cmp=transformerBranchCMP)

    def generateLayouts(self):
        self.generateLayout(self.branches, self.direction, 0 )
        self.generateLayout(self.reversedBranches, reverseDirect(self.direction), 20)


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
        for n in layout_branches:
            n.SetLayout(xStart, self.y, direction)
            xStart += gap
        if len(not_layout_branches) > 2:
            raise ValueError("I do not know how to draw this")
        tmpdir = direction
        not_layout_branches.sort(cmp=No_Layout_Branch_CMP)
        ct = 1
        for n in not_layout_branches:
            tmpdir = reverseDirect(tmpdir)
            if self.reversC:
                tmpdir = reverseDirect(tmpdir)
            n.SetLayout(self.x+self.length/2-15*ct, self.y, tmpdir)
            ct+=1



    def getDimension(self):
        return [self.x, self.y, self.length]

    def draw(self):
        self.InitializeBranches()
        self.generateLayouts()
        self.canvas.drawLine(self.x - self.length / 2 , self.y, self.x + self.length / 2 , self.y, glob.voltMap[self.cnID], 3.5)
        for each in self.branches:
            each.draw()
        for each in self.reversedBranches:
            each.draw()