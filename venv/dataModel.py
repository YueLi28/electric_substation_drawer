#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from transformer import *
from TailDrawer import *
from Utility import *
from branch import *
import glob
import random



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





#            startX = self.drawTail(startX, startY, l1[-1], l1 + l2, direction)




def findTransformers(node, visitedNode):
    nxt = glob.adjDict[node][:]
    while nxt:
        tmp = nxt.pop()
        if tmp in visitedNode:
            continue
        visitedNode.append(tmp)
        if "transformer" in tmp:
            return tmp
        nxt.extend(glob.adjDict[tmp][:])


class Canvas:
    def __init__(self, stationName):
        self.canvas = {"v": "6.2.2", "d":[],"p": {"background":"rgb(0,0,0)", "layers":["0",1], "autoAdjustIndex":True, "hierarchicalRendering":True}}
        self.allBus = {}
        self.name = stationName
        self.generateName()

    def drawFloat(self, x, y, eX, ele):
        color =glob.voltMap[ele]
        if "CN" not in ele:
            n = Node(ele, float(x + eX) / 2, y, "up", color, True)
            self.canvas["d"].append(n.getRepresentation())
        complement = float(eX - x) / 2 - float(glob.nodeSize[cleanElement(ele)][1]) / 2
        self.drawLine(x, y, x + complement, y, color)
        self.drawLine(eX, y, eX - complement, y, color)

    def generateName(self):
        namej = {"c":"ht.Text", "i":1, "p": {"name":"文字", "layer":1, "position":{"x":-800, "y":-800}},
                 "s":{"label":"", "text.color":"rgb(255,0,0)", "text.font": "32px arial, sans-serif"}}
        namej["s"]["text"] = self.name

        self.canvas["d"].append(namej)


    def tmpFindNewTail(self, node, fromNodes):
        res = [x for x in glob.adjDict[node] if x not in fromNodes]
        return res

    def drawTail(self, x, y, node, fromNodes, direction, headLength=40):

        drawer = TailDrawer(x, y, node, fromNodes, direction, self, headLength)
        drawer.draw()

            #raise ValueError("WRONG TAIL!", lines)


    def findTransformerObj(self, transName):
        transID = transName.split("#")[1].split(".")[0]
        if transID in glob.AllTrans:
            return glob.AllTrans[transID]

    def DefineTransformerLoc(self, transName, x, y, direction, can):
        transID = transName.split("#")[1].split(".")[0]
        if "three" in transName:
            glob.AllTrans[transID] = Transformer3port(transName, x,y,direction, can,glob.adjDict)
        else:
            glob.AllTrans[transID] = Transformer2port(transName, x,y,direction, can, glob.adjDict)

    def printToFile(self, fname="/home/liyue/jichengnnegyuanhinhightopozhongruinew/demo/2deditor/Test_new.js"):
        if "Test_new" not in fname:
            toJson = True
            fname = fname.replace(".js",".json")
        else:
            toJson = False
        with open(fname, "w") as f:
            f.write(self.toString(toJson))

    def drawBranch(self, x, y, hLen, components, direction):
        if len(components) == 0:
            return y
        defineTrans = False
        hasTrans = False
        volt = glob.voltMap[components[0]]
        if "transformer" in components[-1]:
            hasTrans = True
            transName = components[-1]
            tran = self.findTransformerObj(components[-1])
            if tran is not None:
                #x = transLoc[0]
                components = components[:-1]
                portX, portY = tran.getCorrectPort(x,y)
                if portY == tran.y:
                    self.drawLine(portX, portY, x, portY, glob.voltMap[components[-1]])
                    portX = x
                else:
                    pass
                    #x = portX
            else:
                defineTrans = True

        if direction == "down":
            sign = 1
        else:
            sign = -1
        hLen *= sign
        self.drawLine(x, y, x, y + hLen, volt)
        y += hLen

        def update(y, c):  # move down 1/2 height of c
            cType = cleanElement(c.split("#")[0])
            if direction == "up":
                y -= float(glob.nodeSize[cType][1]) / 2
            elif direction == "down":
                y += float(glob.nodeSize[cType][1]) / 2
            else:
                raise ValueError('undefined direction: ' % (direction))
            return y

        res = []
        #components = map(cleanElement, components)
        for c in components:
            if "CN" in c:
                self.drawLine(x, y, x, y, 0)
            else:
                if "transformer" in c and defineTrans:
                    oldy = y
                    y = update(y, c)
                    y = update(y, c)
                    self.drawLine(x, oldy, x, y, volt)
                    for t in glob.AllTrans:
                        if "three" in glob.AllTrans[t].name and abs(glob.AllTrans[t].y - y) < 66:
                            oldy = y
                            y = update(y, c)
                            y = update(y, c)
                            self.drawLine(x,oldy,x,y, volt)

                y = update(y, c)
                n = Node(c, x, y, direction, volt)
                res.append(n.getRepresentation())
                y = update(y, c)
        self.canvas["d"].extend(res)
        if defineTrans:
            self.DefineTransformerLoc(transName, x, y, direction,self)
        elif hasTrans:
            self.drawLine(x, y, portX, portY, volt)
        return y

    def drawLine(self, startX, startY, endX, endY, color, borderWidth=2):
        l = Line(startX, startY, endX, endY, color, borderWidth)
        self.canvas["d"].append(l.getRepresentation())

    def __str__(self):
        return "var datamodel_config = " + json.dumps(self.canvas, indent=2)

    def toString(self, toJson):
        if toJson:
            return json.dumps(self.canvas, indent=2)
        else:
            return "var datamodel_config = " + json.dumps(self.canvas, indent=2)


    def printContent(self):
        return json.dumps(self.canvas["d"], indent=2)


class Line:
    def __init__(self, startX, startY, endX, endY, color, borderWidth):
        self.representation = {}
        self.startX, self.startY = startX, startY
        self.endX, self.endY = endX, endY
        self.representation["c"] = "ht.Shape"
        self.representation["i"] = 1
        self.representation["p"] = {"width": abs(self.endX - self.startX), "height": abs(self.endY - self.startY),
                                    "position": {"x": float(self.startX + self.endX) / 2,
                                                 "y": float(self.startY + self.endY) / 2}, "points": {}}
        self.representation["p"]["points"]["__a"] = [{"x": startX, "y": startY}, {"x": endX, "y": endY}]
        self.representation["s"] = {"shape.border.width": borderWidth, "shape.border.color": glob.getVoltRGB(color)}

    def __str__(self):
        return json.dumps(self.representation, indent=2)

    def __repr__(self):
        return json.dumps(self.representation, indent=2)

    def getRepresentation(self):
        return self.representation


class Node:
    def __init__(self, name, x, y, direction, volt, isFloat=False):
        self.volt = volt
        self.tag = name
        self.name, self.id = name.split("#")
        self.name = cleanElement(self.name)
        self.x = float(x)
        self.y = float(y)
        self.direction = direction
        self.isFloat = isFloat
        if self.name not in glob.nodeSize:
            raise ValueError('Node %s not defined' % self.name)
        self.width, self.height = map(float, glob.nodeSize[self.name])
        self.representation = {}
        self.initRepresentation()


    def initRepresentation(self):
        self.representation["c"] = "ht.Node"
        self.representation["i"] = 1  # not sure the usage
        self.representation["p"] = {"name": self.name, "layer": 1,
                                    "position": {"x": self.x, "y": self.y},"tag":self.tag}
        self.representation["a"] = {}

        self.representation["a"]["lineColor"] = glob.getVoltRGB(self.volt)
        self.representation["a"]["voltage"] = str(self.volt)+"kV"
        if self.tag in glob.infoMap:
            self.representation["a"]["name"] = glob.infoMap[self.tag]["name"]

        if "transformer2" in self.name:
            otherport = [x for x in glob.adjDict[self.tag] if "transformer" in x][0]
            self.representation["a"]["lineColor2"] = glob.getVoltRGB(glob.voltMap[otherport])
            if self.direction == "up":
                self.representation["a"]["lineColor"], self.representation["a"]["lineColor2"] = self.representation["a"]["lineColor2"],self.representation["a"]["lineColor"]
        if "transformer3" in self.name:
            np = [x for x in glob.adjDict[self.tag] if "neutral_point" in x][0]
            p1,p2 = [x for x in glob.adjDict[np] if x!=self.tag]
            if glob.voltMap[p1] > glob.voltMap[p2]:
                p1, p2 = p2, p1
            self.representation["a"]["lineColor2"] = glob.getVoltRGB(glob.voltMap[p1])
            self.representation["a"]["lineColor3"] = glob.getVoltRGB(glob.voltMap[p2])



        if self.name != "CN":
            self.representation["p"]["image"] = "symbols/electricity/%s.json" % self.name
        self.representation["s"] = {"label": ""}
        if self.name == "daozha":
            if glob.daozhastat[int(self.id)] == 1:
                self.representation["a"]["state"] = True
            else:
                self.representation["a"]["state"] = False
        if self.name == "kaiguan":
            if glob.kaiguanstat[int(self.id)] == 1:
                self.representation["a"]["state"] = True
            else:
                self.representation["a"]["state"] = False

        if self.name == "singlearrow" and self.direction == "up":
            self.representation["p"]["rotation"] = 3.14159,
        if self.isFloat:
            self.representation["p"]["rotation"] = 1.57079,

    def __str__(self):
        return json.dumps(self.representation, indent=2)

    def __repr__(self):
        return json.dumps(self.representation, indent=2)

    def getRepresentation(self):
        return self.representation

