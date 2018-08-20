from dataModel import *
import glob
import pickle
import urllib, json
import collections
import re, urlparse
import Island



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

    def __init__(self, name, workingdir, queryURL, JsonDir):
        glob.reset()
        self.colorHead = {}
        self.name = name
        self.JsonDir = JsonDir
        fname = workingdir + name
        try:
            #raise ValueError("AAA")
            url = queryURL+name
            response = urllib.urlopen(iriToUri(url))
            data = json.loads(response.read())
        except:
            data = {}
        if "results" in data and data["results"][0]["@@setedge"]:#Try to use online data, if no Online data, use offline data
            print "Data received from remote host"
            with open(fname, 'wb') as f:
                pickle.dump(data, f)
        else:
            print "Try to get offline data"
            try:
                with open(fname,'rb') as f:
                    data = pickle.load(f)
            except:
                print "No offline data is available"
                exit(0)
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

    def newdraw(self, isProduction):
        islands = self.findIsland()
        x = Canvas(self.name)
        islX, islY = 0, 0
        for i in islands:
            isl = Island.Island(i, islX, islY)
            isl.draw(x)
            islX+=2500
        if isProduction:
            x.printToFile(self.JsonDir+self.name+u".json")
        else:
            x.printToFile()