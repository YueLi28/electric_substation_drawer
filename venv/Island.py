from LayoutFinder import *
from bus import *


class Island:

    def __init__(self, VoltBusDict):
        self.VoltBUSDict = VoltBusDict

    def drawBuses(self, buses, x, y, dir, canv, startingP = None):
        buses = list(buses)
        rightedge, leftedge = -float('inf'), float('inf')
        layout = LayoutFinder(glob.adjDict, buses, glob.BusCNID, x, y, dir)
        Bs = layout.findLayout()
        for b in Bs:
            bs = glob.BusDict[b]
            rightedge = max(bs.x + bs.w/2, rightedge)
            leftedge = min(bs.x - bs.w/2, leftedge)
        if startingP is None:
            Offset = 0
        else:
            Offset = startingP + 100 - leftedge
        for b in Bs:
            bs = glob.BusDict[b]
            bs.x += Offset
        for b in Bs:#must draw after all reposition is done
            bs = glob.BusDict[b]
            self.drawSingleBus(bs.id, bs.x, bs.y, layout.dir, bs.w, canv)
        return rightedge+Offset

    def drawSingleBus(self, bus, x, y, dir, busLen, canv):
        b = Bus(x, y, busLen, bus, dir, canv)
        b.draw()


    def draw2Section(self, canv):
        kset = list(self.VoltBUSDict.keys())
        kset.sort()
        lowVolt, highVolt = kset
        self.drawBuses(self.VoltBUSDict[highVolt], 0, -800, "up", canv)
        self.drawBuses(self.VoltBUSDict[lowVolt], 0, 0, "down", canv)

    def draw3Section(self, canv):
        kset = list(self.VoltBUSDict.keys())
        kset.sort()
        lowVolt, midVolt, highVolt = kset
        re = self.drawBuses(self.VoltBUSDict[highVolt], -800, -800, "up", canv)
        self.drawBuses(self.VoltBUSDict[midVolt], 1000, -800, "up", canv, re)
        self.drawBuses(self.VoltBUSDict[lowVolt], -800, 0, "down", canv)

    def draw4Section(self, canv):
        kset = list(self.VoltBUSDict.keys())
        kset.sort()
        lowVolt, midlowVolt, midhighVolt, highVolt = kset
        self.drawBuses(self.VoltBUSDict[highVolt], -600, -800, "up", canv)
        self.drawBuses(self.VoltBUSDict[midhighVolt], 600, -800, "up", canv)
        self.drawBuses(self.VoltBUSDict[midlowVolt], -630, 0, "down", canv)
        self.drawBuses(self.VoltBUSDict[lowVolt], 600, 0, "down", canv)


    def draw(self, x):
        if len (self.VoltBUSDict) == 1:
            vt = list(self.VoltBUSDict.keys())[0]
            self.drawBuses(self.VoltBUSDict[vt], 0, 0, "up", x)
        elif len(self.VoltBUSDict) == 2:
            self.draw2Section(x)
        elif len(self.VoltBUSDict) == 3:
            self.draw3Section(x)
        elif len(self.VoltBUSDict) == 4:
            self.draw4Section(x)
        elif len (self.VoltBUSDict) == 0:
            raise ValueError("No connected bus!")
        else:
            raise ValueError("Unknown type")
        for t in glob.AllTrans:
            glob.AllTrans[t].drawTails()