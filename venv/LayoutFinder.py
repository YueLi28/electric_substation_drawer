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
        self.is32 = False
        self.offset32 = 0


    def getEstimatedLength(self, cnID):
        return 100 * len(glob.adjDict[cnID])


    def FixedTransformer(self, buses):
        fixedT = []
        for b in buses:
            if b in glob.transBus:
                for e in glob.transBus[b]:
                    if "two" in e.name:
                        fixedT.append([b, e])
                    else:
                        if e.y < self.y:
                            fixedT.append([b, e])

        return fixedT

    def find1newX(self, buses):
        fixedT = self.FixedTransformer(buses)
        if fixedT:
            t = fixedT[0][1]
            if t.y > self.y:
                self.dir = Utility.reverseDirect(self.dir)
            self.y = t.y + glob.globOffset
            glob.globOffset += 300
            self.x = t.x

    def find2newX(self, buses):
        fixedT = self.FixedTransformer(buses)
        if fixedT:
            fixedT.sort(key = lambda x: x[1].x)
            sortedBus = [x[0] for x in fixedT]
            sortedPos = [x[1] for x in fixedT]
            self.y = sortedPos[0].y + glob.globOffset
            glob.globOffset += 200
            tails = [x for x in buses if x not in sortedBus]
            self.buses = sortedBus + tails
            self.x = sum([e.x for e in sortedPos])/(len(sortedPos))


    def findLayout(self):
        if len(self.buses) == 1:
            self.find1newX(self.buses)
            glob.placeBus(self.buses[0], self.x, self.y, self.getEstimatedLength(self.buses[0]), self.dir)
            return self.buses
        elif len(self.buses) == 2:
            self.find2newX(self.buses)
            return self.determineLayout2()
        elif len(self.buses) == 3:
            return self.determineLayout3()
        else:
            return self.determineLayout4()



    def findVertical(self, cn):
        branchHeads = [x for x in glob.adjDict[cn] if "BUS" not in x]
        busPairFP = []
        for h in branchHeads:
            lines = [[cn] + x for x in Utility.findTail(h, [cn])]
            for line in lines:
                if line[-1] in self.busCN:
                    if line[-1] != cn:
                        l = [x.split("#")[0] for x in line if "CN" not in x]
                        if l == glob.busPairFP and len(lines)!=1:
                            busPairFP.append(line[-1])
                    else:
                        raise ValueError("SELF CONNECTED")
        return busPairFP

    def findHorizontal(self, cn):
        branchHeads = [x for x in glob.adjDict[cn] if "BUS" not in x]
        busConnector = []
        for h in branchHeads:
            lines = [[cn] + x for x in Utility.findTail(h, [cn])]
            for line in lines:
                if line[-1] in self.busCN:
                    if line[-1] != cn:
                        l = [x.split("#")[0] for x in line if "CN" not in x]
                        if len(l) == 3 or len(l)==1:
                            busConnector.append(line[-1])
                    else:
                        raise ValueError("SELF CONNECTED")
        return busConnector

    def determineLayout4(self):
        stats = [(cn, self.newCheckStat(cn)) for cn in self.buses]
        for cn in self.buses:
            tmp = self.findVertical(cn)
            if len(set(tmp)) == 1:
                glob.AddVerticalBusPair(cn, tmp[0])
            else:
                print tmp, cn
                raise ValueError("AAAA")
            tmp = [x for x in self.findHorizontal(cn) if x!=glob.VerticalBusPair[cn]]
            glob.AddHorizontalBusPair(cn, tmp[0])
            b1, b2 = cn, tmp[0]
        b3, b4 = glob.VerticalBusPair[b1],glob.VerticalBusPair[b2]

        w1,w2 = self.getEstimatedLength(b1), self.getEstimatedLength(b2)
        glob.placeBus(b1, self.x - w1 / 2 - 50, self.y, w1, self.dir)
        glob.placeBus(b2, self.x + w2 / 2 + 50, self.y, w2, self.dir)
        glob.placeBus(b3, self.x - w1 / 2 - 50, self.y+50, w1, self.dir)
        glob.placeBus(b4, self.x + w2 / 2 + 50, self.y+50, w2, self.dir)
        glob.BusDict[b1].reverseConnector()
        return [b1,b2,b3,b4]




    def determineLayout2(self):
        b1, b2 = self.buses
        busD = self.checkStat(b1)[0]
        if self.is32:
            glob.AddVerticalBusPair(b1, b2)
            glob.placeBus(b1, self.x, self.y + 250 + 100*self.offset32, 1500, self.dir)
            glob.placeBus(b2, self.x, self.y - 250 - 100*self.offset32, 1500, self.dir)
            glob.BusDict[b1].define32()
            glob.BusDict[b2].define32()
            return [b1,b2]
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
                glob.AddHorizontalBusPair(b1, b2)
                glob.AddHorizontalBusPair(b2, b3)
                glob.placeBus(b1, self.x - 600 - 50, self.y, 600, self.dir)
                glob.placeBus(b2, self.x, self.y, 600, self.dir)
                glob.placeBus(b3, self.x + 600 + 50, self.y, 600, self.dir)
                return self.buses
            else: #maxCN is the long bus vertically aligned with the other 2
                b1, b2 = [x for x in self.buses if x != maxCN]
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
            if len(tmpLines) == 1 and len(tmpLines[0]) >= 13 and (len(tmpLines[0]) - 13)%6==0: #500 volt station
                self.offset32 = max(self.offset32, (len(tmpLines[0])-13)/6)
                self.is32 = True

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


