#!/usr/bin/env python
# -*- coding: utf-8 -*-
import collections
import glob
import Utility
import SizeEstimator



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
        return self.newGetEstimatedLength(cnID)

    def newGetEstimatedLength(self, cnID):
        Hs =  [x for x in glob.adjDict[cnID] if "BUS" not in x]
        res = 0
        for h in Hs:
            res += 120 + SizeEstimator.estimateWidth(h, [cnID])
        return max(res+100, 400)



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
            if glob.globOffset is None:
                glob.globOffset = t.y + 450
            self.y =  glob.globOffset
            self.x = t.x
            print self.x, t.x

    def find2newX(self, buses):
        fixedT = self.FixedTransformer(buses)
        if fixedT:
            fixedT.sort(key = lambda x: x[1].x)
            sortedBus = [x[0] for x in fixedT]
            sortedPos = [x[1] for x in fixedT]
            if glob.globOffset is None:
                glob.globOffset = max([x.y for x in sortedPos]) + 450
            self.y = glob.globOffset
            seen = set()
            seen_add = seen.add
            tails = [x for x in buses if x not in sortedBus]
            self.buses = [x for x in sortedBus if not (x in seen or seen_add(x))]
            for i in range(len(tails)):
                if i%2 == 1:
                    self.buses +=  [tails[i]]
                else:
                    self.buses = [tails[i]] + self.buses
            self.x = sum([e.x for e in sortedPos]) / (len(set(sortedPos)))

    #def sortBuses(self):


    def findLayout(self):
        if len(self.buses) == 1:
            self.find1newX(self.buses)
            glob.placeBus(self.buses[0], self.x, self.y, self.getEstimatedLength(self.buses[0]), self.dir)
            return self.buses
        elif len(self.buses) == 2:
            self.find2newX(self.buses)
            return self.determineLayout2()
        elif len(self.buses) == 3:
            self.find2newX(self.buses)
            return self.determineLayout3()
        elif len(self.buses) == 4:
            return self.determineLayout4()
        elif len(self.buses) == 5:
            return self.randomPut()
        else:
            print "unknown pattern:", len(self.buses)
            return self.randomPut()



    def findVertical(self, cn):
        branchHeads = [x for x in glob.adjDict[cn] if "BUS" not in x]
        busPairs = []
        for h in branchHeads:
            lines = [[cn] + x for x in Utility.findTail(h, [cn])]
            for line in lines:
                if line[-1] in self.busCN:
                    if line[-1] != cn:
                        if len(line) >= 13 and (len(line) - 13)%6==0:
                            busPairs.append(line[-1])

                        else:
                            l = [x.split("#")[0] for x in line if "CN" not in x]
                            if l == glob.busPairFP and len(lines)!=1:
                                busPairs.append(line[-1])
                    else:
                        raise ValueError("SELF CONNECTED")
        return busPairs

    def findHorizontal(self, cn):
        branchHeads = [x for x in glob.adjDict[cn] if "BUS" not in x]
        Ct = collections.Counter()
        for h in branchHeads:
            lines = [[cn] + x for x in Utility.findTail(h, [cn])]
            for line in lines:
                if line[-1] in self.busCN:
                    if line[-1] != cn:
                        Ct[line[-1]]+=1
                    else:
                        raise ValueError("SELF CONNECTED")
        for k in Ct.keys():
            if Ct[k] == 1:
                return k
        return None

    def randomPut(self):
        self.find2newX(self.buses)
        totalW = 0
        for b in self.buses:
            totalW += self.getEstimatedLength(b)
        totalGap = (len(self.buses) - 1) * 100
        totalW += totalGap
        startingPoint = self.x - totalW/2
        for b in self.buses:
            w = self.getEstimatedLength(b)
            glob.placeBus(b, startingPoint+w/2, self.y, w, self.dir)
            startingPoint += w+100
        return self.buses

    def notConnected(self):
        for b in self.buses:
            if len(glob.findAttachedBus(b)) != 0:
                break
        else:
            return True
        return False

    def determineLayout4(self):
        if self.notConnected():
            return self.randomPut()
        sBus = self.findSideBus()
        if sBus:
            print "HAS SIDE BUS"
            self.buses = [x for x in self.buses if x != sBus]
            bses = self.determineLayout3()
            if self.dir == "up":
                sY = -450
            else:
                sY = 450
            sWidth = 0
            sX = self.x
            for b in bses:
                if glob.BusDict[b].w > sWidth:
                    sWidth = glob.BusDict[b].w
                    sX = glob.BusDict[b].x

            glob.placeBus(sBus, sX, self.y + sY, sWidth, self.dir)
            return bses + [sBus]

        for cn in self.buses:
            self.checkStat(cn)
            tmp = self.findVertical(cn)
            if len(set(tmp)) == 1:
                glob.AddVerticalBusPair(cn, tmp[0])
            else:
                raise ValueError("CANNOT FIND VERTICAL BUS PAIR")


            tmp = self.findHorizontal(cn)
            glob.AddHorizontalBusPair(cn, tmp)
            b1, b2 = cn, tmp
        b3, b4 = glob.VerticalBusPair[b1],glob.VerticalBusPair[b2]
        w1,w2 = max(self.getEstimatedLength(b1),self.getEstimatedLength(b3)), max(self.getEstimatedLength(b2),self.getEstimatedLength(b4))
        if self.is32:
            glob.placeBus(b1, self.x-w1/2-50, self.y + 20 + 110*self.offset32, w1, self.dir)
            glob.placeBus(b3, self.x-w1/2-50, self.y - 20 - 110*self.offset32, w1, self.dir)
            glob.placeBus(b2, self.x+w2/2+50, self.y + 20 + 110*self.offset32, w2, self.dir)
            glob.placeBus(b4, self.x+w2/2+50, self.y - 20 - 110*self.offset32, w2, self.dir)
            glob.BusDict[b1].define32()
            glob.BusDict[b2].define32()
            glob.BusDict[b3].define32()
            glob.BusDict[b4].define32()
        else:
            glob.placeBus(b1, self.x - w1 / 2 - 50, self.y, w1, self.dir)
            glob.placeBus(b2, self.x + w2 / 2 + 50, self.y, w2, self.dir)
            glob.placeBus(b3, self.x - w1 / 2 - 50, self.y+50, w1, self.dir)
            glob.placeBus(b4, self.x + w2 / 2 + 50, self.y+50, w2, self.dir)
        glob.BusDict[b1].reverseConnector()
        return [b1,b2,b3,b4]






    def findSideBus(self):
        res = []
        for b in self.buses:
            bName = glob.infoMap[b]['name']
            if u'旁路' in bName:
                res.append(b)
        if len(res) > 1:
            raise ValueError("Found more than one side bus")
        elif len(res) == 1:
            return res[0]
        else:
            return None


    def OnePlusSide(self, mBus, sideBus):
        width = max(self.getEstimatedLength(mBus), self.getEstimatedLength(sideBus))
        if self.dir == "up":
            sY = -400
        else:
            sY = 400
        glob.placeBus(sideBus, self.x, self.y + sY, width, self.dir)
        glob.placeBus(mBus, self.x, self.y, width, self.dir)
        return mBus, sideBus


    def determineLayout2(self):
        def hasDirectionTransformer(myBus):
            branchHeads = [x for x in glob.adjDict[myBus] if "BUS" not in x]
            for h in branchHeads:
                t = Utility.findTail(h, [myBus])
                if len(t) == 1 and "transformer" in t[0][-1]:
                    return True
            return False
        b1, b2 = self.buses
        sideBus = self.findSideBus()
        if sideBus is not None:
            print "HAS SIDE BUS"
            if b1 == sideBus:
                otherBus = b2
            else:
                otherBus = b1
            return self.OnePlusSide(otherBus, sideBus)
        busD = self.checkStat(b1)
        if self.is32:
            if hasDirectionTransformer(b2):
                b1, b2 = b2, b1
            glob.AddVerticalBusPair(b1, b2)
            w1, w2 = self.getEstimatedLength(b1), self.getEstimatedLength(b2)
            tmpL = max([w1, w2, 1000])
            glob.placeBus(b1, self.x, self.y + 20 + 110*self.offset32, tmpL, self.dir)
            glob.placeBus(b2, self.x, self.y - 20 - 110*self.offset32, tmpL, self.dir)
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
                print "HAS SIDE BUS2"
                s = cn
                b1, b2 = [c for c in self.buses if c!=cn]
                tmp = self.newCheckStat(b1)
                if self.dir == "up":
                    sY = -450
                else:
                    sY = 450
                if tmp[1] > tmp[2]:#vertical pair
                    glob.AddVerticalBusPair(b1, b2)
                    width = max(self.getEstimatedLength(b1), self.getEstimatedLength(b2))
                    glob.placeBus(b1, self.x, self.y - 25, width, self.dir)
                    glob.placeBus(b2, self.x, self.y + 25, width, self.dir)
                    glob.placeBus(s, self.x, self.y + sY, width, self.dir)
                else:
                    glob.AddHorizontalBusPair(b1, b2)
                    w1,w2 = self.getEstimatedLength(b1),self.getEstimatedLength(b2)
                    glob.placeBus(b1, self.x - w1/2 - 50, self.y, w1, self.dir)
                    glob.placeBus(b2, self.x + w2/2 + 50, self.y, w2, self.dir)
                    glob.placeBus(s, self.x, self.y + sY, w1+w2+100, self.dir)
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
                w1, w2, w3 = self.getEstimatedLength(b1), self.getEstimatedLength(b2), self.getEstimatedLength(b3)
                glob.AddHorizontalBusPair(b1, b2)
                glob.AddHorizontalBusPair(b2, b3)
                totalL = (w1+w2+w3+200)
                glob.placeBus(b1, self.x - totalL/2 + w1/2, self.y, w1, self.dir)
                glob.placeBus(b2, self.x -totalL/2 + w1+100+w2/2, self.y, w2, self.dir)
                glob.placeBus(b3, self.x + totalL/2 - w3/2, self.y, w3, self.dir)
                return self.buses
            else: #maxCN is the long bus vertically aligned with the other 2
                b1, b2 = [x for x in self.buses if x != maxCN]
                w1, w2 = self.getEstimatedLength(b1), self.getEstimatedLength(b2)
                glob.AddVerticalBusPair(b1, maxCN)
                glob.AddVerticalBusPair(b2, maxCN)
                glob.AddHorizontalBusPair(b1, b2)
                glob.placeBus(maxCN, self.x + (w2-w1)/2, self.y - 25, w1+w2+100, self.dir)
                glob.placeBus(b1, self.x - w1/2 - 50, self.y + 25, w1, self.dir)
                glob.placeBus(b2, self.x + w2/2 + 50, self.y + 25, w2, self.dir)
                return [b1, b2, maxCN]


    def checkStat(self, cn):
        branchHeads = [x for x in glob.adjDict[cn] if "BUS" not in x]
        busD = collections.Counter()
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
            if len(tmpLines) == 1 and len(tmpLines[0]) >= 13 and Utility.match32Feature(tmpLines[0]): #500 volt station
                self.offset32 = max(self.offset32, (len(tmpLines[0])/6)) #find the position of the upper bus
                self.is32 = True
            busD[Otherbus] += 1
        if self.is32:  # Sometimes a 32 pattern is not strict, add the leftover (update self.offset32)
            for h in branchHeads:
                lines = [[cn] + x for x in Utility.findTail(h, [cn])]
                for line in lines:
                    if line[-1] in self.busCN:
                        self.offset32 = max(self.offset32, (len(line[:-1])/6.0))
        return busD



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


