#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataModel import *
import glob
import pickle
import urllib, json
import collections
import re, urlparse
import Island
workingdir = u"/home/liyue/substation_offline/"




def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )




class drawer():

    def mutateTransformerName(self, name):
        if "transformer" in name:
            name = name[:-1] + "." + name[-1]
        return name

    def __init__(self, name):
        self.colorHead = {}
        glob.reset()
        self.name = name
        fname = workingdir + name
        try:
            url = u"http://192.168.2.5:9000/query/TwoOptionsNAME?SubstationNAME="+name
            print url
            response = urllib.urlopen(iriToUri(url), timeout=1)
            data = json.loads(response.read())
        except:
            data = {}
        if "results" in data:#Try to use online data, if no Online data, use offline data
            with open(fname, 'wb') as f:
                pickle.dump(data, f)
        else:
            with open(fname,'rb') as f:
                data = pickle.load(f)
        edges = data["results"][0]["@@setedge"]
        self.adjDict = collections.defaultdict(set)
        for points in edges:
            fromNode = self.mutateTransformerName(points["from_type"] + "#" + points["from_id"])
            toNode = self.mutateTransformerName(points["to_type"] + "#" + points["to_id"])
            # print points["from_type"]
            self.adjDict[fromNode].add(toNode)
            self.adjDict[toNode].add(fromNode)
        for k in self.adjDict:
            self.adjDict[k] = list(self.adjDict[k])
        self.busCN = set()
        self.VoltBUSDict = collections.defaultdict(set)
        nodes = data["results"][1]["vertexSet"]
        for each in nodes:
            nodeName = self.mutateTransformerName(each["v_type"] + "#" + each["v_id"])
            if each["v_type"] == "BUS":
                bCN = self.adjDict[nodeName][0]
                if len(self.adjDict[bCN]) > 1:
                    self.VoltBUSDict[int(each["attributes"]["volt"])].add(self.adjDict[nodeName][0])
                    self.busCN.add(bCN)
                    glob.infoMap[bCN] = each["attributes"]
            if "transformer" in each["v_type"]:
                self.colorHead[nodeName]=each["attributes"]["volt"]
            if "BUS" in each["v_type"]:
                self.colorHead[nodeName] = each["attributes"]["volt"]
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

    def isVisited(self):
        if len(glob.visitedBusCN) == len(glob.visitedBusCN.union(self.busCN)):
            return True
        glob.visitedBusCN = glob.visitedBusCN.union(self.busCN)
        #print len(glob.visitedBusCN)
        return False


    def findIsland(self):
        candidates = list(self.busCN)
        islands = []
        while candidates:
            seed = candidates.pop()
            res = [seed]
            visited = []
            future = [seed]
            while future:
                tmp = future.pop()
                if tmp in visited:
                    continue
                if tmp in candidates:
                    candidates.remove(tmp)
                    res.append(tmp)
                visited.append(tmp)
                future.extend(glob.adjDict[tmp])
            islands.append(res)
        return islands

    def newdraw(self, isTest):
        islands = self.findIsland()
        x = Canvas(self.name)
        islX, islY = 0, 0
        for i in islands:
            isl = Island.Island(i, islX, islY)
            isl.draw(x)
            islX+=2000
        if isTest:
            x.printToFile(u"/home/liyue/substation_Json/"+self.name+u".js")
        else:
            x.printToFile()


class tester:
    def __init__(self):
        ct = collections.Counter()
        count = 0
        with open("/home/liyue/substation_offline/Substation.csv","r") as f:
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

inp = "四川.德昌风电厂"
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


