import urllib, json
import collections
import glob
import Utility



class LayoutFinder:
    def __init__(self, adjDict, buses, busCN, centerX, centerY, dir):
        glob.adjDict = adjDict
        self.buses = buses
        self.busCN = busCN
        self.x = centerX
        self.y = centerY
        self.dir = dir


    def getEstimatedLength(self, cnID):
        return 100 * len(glob.adjDict[cnID])


    def findLayout(self):
        if len(self.buses) == 1:
            newX = self.findTransCorrespondingX(self.buses)
            if -float('inf') < newX < float('inf'):
                self.x = newX
            glob.placeBus(self.buses[0], self.x, self.y, self.getEstimatedLength(self.buses[0]), self.dir)
            return self.buses
        elif len(self.buses) == 2:
            return self.determineLayout2()
        elif len(self.buses) == 3:
            return self.determineLayout3()
        else:
            raise ValueError("NOT Handled Yet")

    def findTransCorrespondingX(self, bs):
        xmin = float('inf')
        xmax = -float('inf')
        y = None
        for each in bs:
            if each in glob.transBus:
                tmp = glob.transBus[each]
                for e in tmp:
                    xmin = min(xmin, e[0])
                    xmax = max(xmax, e[0])
                    y = e[1]
        if y != None and self.y < y:
            self.y = 400
            self.dir = Utility.reverseDirect(self.dir)
            print self.dir
        if xmin == xmax and len(bs) == 2:#only one but 2 buses
            self.y = 400
            if bs[0] in glob.transBus:
                return xmin + 100
            else:
                return xmin - 100
        return (xmin+xmax)/2

    def determineLayout2(self):
        b1, b2 = self.buses
        if b1 in glob.BusFlow and b2 in glob.BusFlow:
            if glob.BusFlow.index(b1) > glob.BusFlow.index(b2):
                b1, b2 = b2, b1
        busD = self.checkStat(b1)[0]
        newX = self.findTransCorrespondingX(self.buses)
        if -float('inf') < newX < float('inf'):
            self.x = newX
        if busD[1] > busD[0]:#vertical pair
            glob.AddVerticalBusPair(b1, b2)
            w = self.getEstimatedLength(b1)
            glob.placeBus(b1, self.x, self.y, w, self.dir)
            glob.placeBus(b2, self.x, self.y + 50, w, self.dir)
        else:
            glob.AddHorizontalBusPair(b1, b2)
            w1, w2 = self.getEstimatedLength(b1), self.getEstimatedLength(b2)
            glob.placeBus(b1, self.x - w1/2 - 50, self.y, w1 , self.dir)
            glob.placeBus(b2, self.x + w2/2 + 50, self.y, w2, self.dir)
        return [b1,b2]


    def determineLayout3(self):
        stats = [(cn, self.newCheckStat(cn)) for cn in self.buses]
        for cn, stat in stats:
            if stat[0] > 0:#has side bus
                s = cn
                b1, b2 = [c for c in self.buses if c!=cn]
                tmp = self.newCheckStat(b1)
                if self.dir == "up":
                    sY = -400
                else:
                    sY = 400
                if tmp[1] > tmp[2]:#vertical pair
                    glob.AddVerticalBusPair(b1, b2)
                    glob.placeBus(b1, self.x, self.y - 25, 1000, self.dir)
                    glob.placeBus(b2, self.x, self.y + 25, 1000, self.dir)
                    glob.placeBus(s, self.x, self.y + sY, 1000, self.dir)
                else:
                    if b1 in glob.BusFlow and b2 in glob.BusFlow:
                        if glob.BusFlow.index(b1) > glob.BusFlow.index(b2):
                            b1, b2 = b2, b1
                    glob.AddHorizontalBusPair(b1, b2)
                    glob.placeBus(b1, self.x - 500 - 50, self.y, 1000, self.dir)
                    glob.placeBus(b2, self.x + 500 + 50, self.y, 1000, self.dir)
                    glob.placeBus(s, self.x, self.y + sY, 2100, self.dir)
                return [b1, b2, s]
        else:
            maxCN, maxB = None, 0
            for cn in self.buses:
                bStat = self.newCheckStat(cn)
                if (bStat[1] > maxB):
                    maxCN = cn
                    maxB = bStat[1]
            if maxCN == None:#3 bus horizontally aligned
                b1, b2, b3 = self.buses
                glob.placeBus(b1, self.x - 600 - 50, self.y, 600, self.dir)
                glob.placeBus(b2, self.x, self.y, 600, self.dir)
                glob.placeBus(b3, self.x + 600 + 50, self.y, 600, self.dir)
                return self.buses
            else: #maxCN is the long bus vertically aligned with the other 2
                b1, b2 = [x for x in self.buses if x != maxCN]
                if b1 in glob.BusFlow and b2 in glob.BusFlow:
                    if glob.BusFlow.index(b1) > glob.BusFlow.index(b2):
                        b1, b2 = b2, b1
                glob.AddVerticalBusPair(b1, maxCN)
                glob.AddVerticalBusPair(b2, maxCN)
                glob.AddHorizontalBusPair(b1, b2)
                glob.placeBus(maxCN, self.x, self.y - 25, 2100, self.dir)
                glob.placeBus(b1, self.x - 500 - 50, self.y + 25, 1000, self.dir)
                glob.placeBus(b2, self.x + 500 + 50, self.y + 25, 1000, self.dir)
                return [b1, b2, maxCN]


    def checkStat(self, cn):
        branchHeads = [x for x in glob.adjDict[cn] if "BUS" not in x]
        busD = collections.Counter()
        checkSideBus = [0, 0]
        for h in branchHeads:
            lines = [[cn]+x for x in Utility.findTail(h, [cn])]
            Otherbus = 0
            tmpLines = []
            for line in lines:
                if line[-1] in self.busCN:
                    if line[-1] != cn:
                        Otherbus += 1
                        tmpLines.append(line)
                    else:
                        raise ValueError("SELF CONNECTED")
            if len(tmpLines) == 2:
                l1, l2 = tmpLines
                if len(l1) == len(l2): #Two lines look identical for a side bus
                    checkSideBus[0] += 1
                else:
                    checkSideBus[1] += 1

            busD[Otherbus] += 1
        return busD, checkSideBus



    def newCheckStat(self, cn):
        branchHeads = [x for x in glob.adjDict[cn] if "BUS" not in x]
        sideBusFP = busPairFP = busConnector = 0
        for h in branchHeads:
            lines = [[cn]+x for x in Utility.findTail(h, [cn])]
            for line in lines:
                if line[-1] in self.busCN:
                    if line[-1] != cn:
                        l = [x.split("#")[0] for x in line if "CN" not in x]
                        if l == glob.sideBusFP:
                            sideBusFP+=1
                        elif l == glob.busPairFP:
                            busPairFP+=1
                        elif len(l) == 3:
                            busConnector+=1
                    else:
                        raise ValueError("SELF CONNECTED")
        return sideBusFP, busPairFP, busConnector

