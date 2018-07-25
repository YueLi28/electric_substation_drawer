#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataModel import *
from LayoutFinder import *
from Utility import *
import glob
import os
import pickle
import urllib

# x = Canvas()

# x.drawBus(0,0,800,[["Disconnector", "Breaker", "Disconnector","singlearrow"]]*1, "down")
# x.printToFile(None)


import re, urlparse

def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )


import urllib, json
import collections
workingdir = u"/tmp/offlineData/"

class drawer():
    def __init__(self, name):
        self.colorHead = {}
        glob.reset()
        self.name = name
        fname = workingdir + name
        if os.path.isfile(fname):
            with open(fname,'rb') as f:
                data = pickle.load(f)
        else:
            url = u"http://192.168.2.5:9000/query/TwoOptionsNAME?SubstationNAME="+name
            response = urllib.urlopen(iriToUri(url))
            data = json.loads(response.read())
            with open(fname, 'wb') as f:
                pickle.dump(data, f)

        datasets = data["results"][0]["@@setedge"]

        self.adjDict = collections.defaultdict(set)
        for points in datasets:
            fromNode = points["from_type"] + "#" + points["from_id"]
            toNode = points["to_type"] + "#" + points["to_id"]
            # print points["from_type"]
            self.adjDict[fromNode].add(toNode)
            self.adjDict[toNode].add(fromNode)

        for k in self.adjDict:
            self.adjDict[k] = list(self.adjDict[k])

        self.busCN = set()
        self.VoltBUSDict = collections.defaultdict(set)
        for each in data["results"][1]["vertexSet"]:
            if each["v_type"] == "BUS":
                busID = "BUS#" + each["v_id"]
                bCN = self.adjDict[busID][0]
                if len(self.adjDict[bCN]) > 1:
                    self.VoltBUSDict[int(each["attributes"]["volt"])].add(self.adjDict[busID][0])
                    self.busCN.add(bCN)
            if each["v_type"] == "Disconnector":
                glob.daozhastat[each["attributes"]["id"]] = each["attributes"]["point"]
            if each["v_type"] == "Breaker":
                glob.kaiguanstat[each["attributes"]["id"]] = each["attributes"]["point"]
            if "transformer" in each["v_type"]:
                self.colorHead[each["v_type"]+"#"+each["v_id"]]=each["attributes"]["volt"]
            if "BUS" in each["v_type"]:
                self.name = each["attributes"]["name"].split("/")[0]
                self.colorHead[each["v_type"] + "#" + each["v_id"]] = each["attributes"]["volt"]
            glob.infoMap[each["v_type"] + "#" + each["v_id"]] = each['attributes']

        glob.fillRelation(self.adjDict, self.busCN)
        self.coloring()


    def tainting(self, h, color):
        glob.voltMap[h] = color
        visited = [h]
        future = self.adjDict[h][:]
        while future:
            tmp = future.pop()
            if tmp in visited:
                continue
            visited.append(tmp)
            if "transformer" not in tmp:
                glob.voltMap[tmp] = color
                future.extend(self.adjDict[tmp])


    def coloring(self):
        for h in self.colorHead:
            color = self.colorHead[h]
            self.tainting(h, color)
        #if len(self.colorHead) == 0:#no transformer




    def isVisited(self):


        if len(glob.visitedBusCN) == len(glob.visitedBusCN.union(self.busCN)):
            return True
        glob.visitedBusCN = glob.visitedBusCN.union(self.busCN)
        #print len(glob.visitedBusCN)
        return False

    def drawBuses(self, buses, x, y, dir, canv, startingP = None):
        buses = list(buses)
        rightedge, leftedge = -float('inf'), float('inf')
        # LayoutFinder(self.adjDict, buses, self.busCN, x, y).findConnectedBranch()
        # # Layout = LayoutFinder(self.adjDict, buses, self.busCN, x, y).determineLayout()
        # # print Layout
        # return
        #print LayoutFinder(self.adjDict, buses, self.busCN, x, y).findConnectedBranch()
        layout = LayoutFinder(self.adjDict, buses, self.busCN, x, y, dir)
        Bs = layout.findLayout()
        for b in Bs:
            bs = glob.BusDict[b]
            rightedge = max(bs.x + bs.w/2, rightedge)
            leftedge = min(bs.x - bs.w/2, leftedge)
        if startingP == None:
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

    def drawBusPair(self, buses, x, y, dir, busL, canv):
        b1,b2 = buses
        glob.AddBusPair(b1, b2)
        bus1 = Bus(x, y - 25, busL, b1, dir, canv)
        bus2 = Bus(x, y + 25, busL, b2, dir, canv)
        bus1.draw()

        bus2.draw()

    def drawHorizontalBusPair(self, buses, x, y, dir, len, canv):
        bus1, bus2 = buses
        b1 = Bus(x - 50 - len/2, y, len, bus1, dir, canv)
        b2 = Bus(x + 50 + len/2, y, len, bus2, dir, canv)
        b1.draw()
        b2.draw()


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

    def newdraw(self, isTest):
        x = Canvas(self.name)
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


        #self.drawHorizontalBusPair(x)
        #self.drawVerticalBusPair(x)
        if isTest:
            x.printToFile(u"/tmp/stationDraw/"+self.name+u".js")
        else:
            x.printToFile()

    def findBusConnector(self):
        reversedConjunctions = [x[::-1] for x in self.conjunctions]
        for i in range(len(self.conjunctions)):
            for j in range(i + 1, len(reversedConjunctions)):
                if self.conjunctions[i] == reversedConjunctions[j]:
                    res = self.conjunctions[i]
                    self.conjunctions.remove(res)
                    self.conjunctions.remove(res[::-1])
                    return res

    def findConjunctions(self):
        raw = collections.defaultdict(list)
        pairs = {}
        transformers = {}
        for each in self.conjunctions:
            raw[each[-1]].append(each)
        for each in raw:
            if self.IsTransformerBranch(raw[each]):
                transformers[each] = raw[each]
            else:
                pairs[each] = raw[each]
        return [pairs, transformers]

    def IsTransformerBranch(self, conj):
        visited = set()
        for each in conj:
            start = each[-1]
            visited.add(each[-2])
        future = [start]
        while future:
            tmp = future.pop()
            if tmp in visited:
                continue
            if "transformer" in tmp:
                return True
            visited.add(tmp)
            for each in self.adjDict[tmp]:
                future.append(each)
        return False


class tester:
    def __init__(self):
        ct = collections.Counter()
        count = 0
        with open("/tmp/Substation.csv","r") as f:
            ids = [x.strip().split(',')[1] for x in f.readlines()]
            names = list((set(ids)))
            print len(names)
            for name in names:
                name = unicode(name, "utf-8")
                try:
                    x = drawer(name)
                except Exception, err:
                    print "ERROR!", err
                    continue
                count+=1
                if x.isVisited():
                    print "VISITED: ", name
                    continue
                try:
                    print name, [[e, len(x.VoltBUSDict[e])] for e in x.VoltBUSDict]
                    x.newdraw(True)
                except Exception, err:
                    print "\tCANNOT DRAW: ", err


import operator

isTest = False

inp = "西南.普提"
inp = unicode(inp, "utf-8")
#k = tester()
#25745: Vertical bus pair
#25559: Single bus with segmentation and side bus
#4909:  Vertical bus pair with side bus
#25613: Vertical bus pair with side bus (with Transformer connected to the side bus
#25920: Bus Pair with segmentation
#25322: connected ACLine
#5372: 10V and 220V
if isTest:
    testCases = [25745, 25559, 4909, 25613, 25920, 25322, 5372, 2578, 20465]
    for i in testCases:
        #print i
        k = drawer(i)
        k.newdraw(False)
else:
    k = drawer(inp)
    k.newdraw(False)


print "Done"


