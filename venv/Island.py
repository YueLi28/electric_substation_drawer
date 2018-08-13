from LayoutFinder import *
from bus import *


class Island:
    def findVoltFromBus(self, buses):
        myDict = {}
        for b in buses:
            volt = glob.infoMap[b]["volt"]
            if volt not in myDict:
                myDict[volt] = []
            myDict[volt].append(b)
        return myDict
    def __init__(self, buses, x, y):
        self.VoltBUSDict = self.findVoltFromBus(buses)
        self.x, self.y = x, y

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
        glob.VoltPosition[highVolt] = [self.x, self.y-800]
        glob.VoltPosition[lowVolt] = [self.x, self.y]
        self.drawBuses(self.VoltBUSDict[highVolt], self.x, self.y-800, "up", canv)
        self.drawBuses(self.VoltBUSDict[lowVolt], self.x, self.y, "down", canv)

    def draw3Section(self, canv):
        kset = list(self.VoltBUSDict.keys())
        kset.sort()
        lowVolt, midVolt, highVolt = kset
        glob.VoltPosition[highVolt] = [self.x-800, self.y-800]
        glob.VoltPosition[midVolt] = [self.x+1000, self.y-800]
        glob.VoltPosition[lowVolt] = [self.x-800, self.y+300]
        re = self.drawBuses(self.VoltBUSDict[highVolt], glob.VoltPosition[highVolt][0], glob.VoltPosition[highVolt][1], "up", canv)
        self.drawBuses(self.VoltBUSDict[midVolt], glob.VoltPosition[midVolt][0], glob.VoltPosition[midVolt][1], "up", canv, re)
        self.drawBuses(self.VoltBUSDict[lowVolt], glob.VoltPosition[lowVolt][0], glob.VoltPosition[lowVolt][1], "down", canv)

    def draw4Section(self, canv):
        kset = list(self.VoltBUSDict.keys())
        kset.sort()
        lowVolt, midlowVolt, midhighVolt, highVolt = kset
        glob.VoltPosition[highVolt] = [self.x-600, self.y-800]
        glob.VoltPosition[midhighVolt] = [self.x+600, self.y-800]
        glob.VoltPosition[midlowVolt] = [self.x-630, self.y]
        glob.VoltPosition[lowVolt] = [self.x+600, self.y]

        re = self.drawBuses(self.VoltBUSDict[highVolt], glob.VoltPosition[highVolt][0], glob.VoltPosition[highVolt][1], "up", canv)
        self.drawBuses(self.VoltBUSDict[midhighVolt], glob.VoltPosition[midhighVolt][0], glob.VoltPosition[midhighVolt][1], "up", canv, re)
        re = self.drawBuses(self.VoltBUSDict[midlowVolt], glob.VoltPosition[midlowVolt][0], glob.VoltPosition[midlowVolt][1], "down", canv)
        self.drawBuses(self.VoltBUSDict[lowVolt], glob.VoltPosition[lowVolt][0], glob.VoltPosition[lowVolt][1], "down", canv, re)


    def draw(self, x):
        if len (self.VoltBUSDict) == 1:
            vt = list(self.VoltBUSDict.keys())[0]
            glob.VoltPosition[vt] = [self.x, self.y]
            self.drawBuses(self.VoltBUSDict[vt], self.x, self.y, "up", x)
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
        keys = glob.AllTrans.keys()[:]
        for k in keys:
            glob.AllTrans[k].drawTails()