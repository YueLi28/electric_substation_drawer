#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from transformer import *
from TailDrawer import *
from Utility import *
from branch import *
from bus import *
import glob
import random







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
        self.canvas = {"v": "6.2.2", "d":[],"p": {"background":"rgb(50,50,50)", "layers":["0",1], "autoAdjustIndex":True, "hierarchicalRendering":True}}
        self.allBus = {}
        self.name = stationName
        # self.generateName()

    def drawFloat(self, x, y, eX, ele):
        color =glob.voltMap[ele]
        if "CN" not in ele:
            n = Node(ele, float(x + eX) / 2, y, "up", color, True)
            self.canvas["d"].append(n.getRepresentation())
        complement = float(eX - x) / 2 - float(glob.nodeSize[cleanElement(ele)][1]) / 2
        self.drawLine(x, y, x + complement, y, color)
        self.drawLine(eX, y, eX - complement, y, color)

    def generateName(self, x=0, y=-1350):
        namej = {"c":"ht.Text", "i":1, "p": {"name":"文字", "layer":1, "position":{"x":x - 15 * len(self.name), "y":y - 300}},
                 "s":{"label":"", "text.color":"rgb(255,0,0)", "text.font": "80px arial, sans-serif"}}
        namej["s"]["text"] = self.name

        self.canvas["d"].append(namej)


    def tmpFindNewTail(self, node, fromNodes):
        res = [x for x in glob.adjDict[node] if x not in fromNodes]
        return res

    def drawTail(self, x, y, node, fromNodes, direction, headLength=40):

        drawer = TailDrawer(x, y, node, fromNodes, direction, self, headLength)

        if glob.stationY is None:
            glob.stationY = y
        elif glob.stationY > y:
            glob.stationY = y

        drawer.draw()

            #raise ValueError("WRONG TAIL!", lines)
    def DefineTransformerLoc(self, transName, x, y, direction, can):
        transID = transName.split("#")[1].split(".")[0]
        if "three" in transName:
            glob.AllTrans[transID] = Transformer3port(transName, x,y,direction, can,glob.adjDict)
        else:
            glob.AllTrans[transID] = Transformer2port(transName, x,y,direction, can, glob.adjDict)

    def printToFile(self, fname="/home/liyue/jichengnnegyuanhinhightopozhongruinew/demo/2deditor/Test_new.js"):
        if "Test_new" not in fname:
            toJson = True
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
            tran = findTransformerObj(components[-1])
            if tran is not None:
                #x = transLoc[0]
                components = components[:-1]
                portX, portY = tran.getCorrectPort(glob.infoMap[transName.replace(".","")]['volt'])
                if portY == tran.y: #3 port transformer going right
                    self.drawLine(portX, portY, x, portY, glob.voltMap[transName])
                    portX = x
                else:
                    if glob.PortWithinBus(portX, transName):
                        x = portX
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
            if cType == "C_S":
                return y
            if direction == "up":
                y -= float(glob.nodeSize[cType][1]) / 2
            elif direction == "down":
                y += float(glob.nodeSize[cType][1]) / 2
            else:
                raise ValueError('undefined direction: ' % (direction))
            return y

        res = []
        #components = map(cleanElement, components)
        for i,c in enumerate(components):
            if "CN" in c:
                self.drawLine(x, y, x, y, 0)
                if c not in glob.CNpos:
                    glob.CNpos[c] = [x,y]
                else:
                    if i !=0 and c not in glob.BusCNID:
                        volt = glob.voltMap[c]
                        tgtx, tgty = glob.CNpos[c]
                        self.drawLine(x, y, x+20, y, volt)
                        self.drawLine(x+20,y,x+20,tgty,volt)
                        self.drawLine(x+20,tgty,tgtx,tgty,volt)

            else:
                if "transformer" in c and defineTrans:
                    oldy = y
                    y = update(y, c)
                    y = update(y, c)
                    self.drawLine(x, oldy, x, y, volt)
                    while self.CollideTrans(y):
                        oldy = y
                        y = update(y, c)
                        y = update(y, c)
                        self.drawLine(x,oldy,x,y,volt)
                y = update(y, c)
                n = Node(c, x, y, direction, volt)
                res.append(n.getRepresentation())
                y = update(y, c)
        self.canvas["d"].extend(res)
        if defineTrans:
            self.DefineTransformerLoc(transName, x, y, direction,self)
        elif hasTrans:
            if x != portX: #cannot draw a vertical line to connect the transformer, need a bend
                Offset = 50
                while glob.collidewithOther(x, y-Offset, portX):
                    if x < portX:
                        Offset -= 25
                    else:
                        Offset += 25
                self.drawLine(x, y, x, y-Offset, volt)
                y-=Offset
                self.drawLine(x, y, portX, y, volt)
            self.drawLine(portX, y, portX, portY, volt)
        return y

    def CollideTrans(self, y):
        for k in glob.AllTrans:
            transObj = glob.AllTrans[k]
            if "three" in transObj.name and abs(transObj.y - y) < 99:
                if transObj.isBlockingOtherTransformers():
                    return True
        return False


    def drawBusLine(self, startX, startY, endX, endY, color, cnID):
        l = Line(startX, startY, endX, endY, color, 15)
        l.addAttributeFromBus(cnID)
        self.canvas["d"].append(l.getRepresentation())

    def drawLine(self, startX, startY, endX, endY, color, borderWidth=7):
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

    def addAttributeFromBus(self, cnID):
        attrs =  glob.infoMap[cnID]
        self.representation["a"] = {}
        self.representation["a"]["name"] = attrs['name']
        self.representation["a"]["voltage"] = attrs["volt"]
        self.representation["p"]["tag"] = cnID
        self.representation["a"]["lineColor"] = glob.getVoltRGB(attrs["volt"])

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
        glob.drawnNode[self.tag] = self

    def initRepresentation(self):
        self.representation["c"] = "ht.Node"
        self.representation["i"] = 1  # not sure the usage
        self.representation["p"] = {"name": self.name, "layer": 1,
                                    "position": {"x": self.x, "y": self.y},"tag":self.tag}
        self.representation["a"] = {}

        self.representation["a"]["lineColor"] = glob.getVoltRGB(self.volt)
        self.representation["a"]["voltage"] = str(self.volt)+"kV"
        tmp = self.tag.replace(".","")
        if tmp in glob.infoMap:
            self.representation["a"]["name"] = glob.infoMap[tmp]["name"]
#            self.representation["a"]["production_id"] = glob.infoMap[tmp]["production_id"]

        if "transformer2" in self.name:
            otherport = [x for x in glob.adjDict[self.tag] if "transformer" in x][0]
            self.representation["a"]["lineColor2"] = glob.getVoltRGB(glob.voltMap[otherport])
            if self.direction == "up":
                self.representation["a"]["lineColor"], self.representation["a"]["lineColor2"] = self.representation["a"]["lineColor2"],self.representation["a"]["lineColor"]
        if "transformer3" in self.name:
            np = [x for x in glob.adjDict[self.tag] if "neutral_point" in x][0]
            p1,p2 = [x for x in glob.adjDict[np] if x!=self.tag]
            v1, v2 = glob.voltMap[p1], glob.voltMap[p2]
            if v1 < v2:
                p1, p2 = p2, p1
                v1, v2 = glob.voltMap[p1], glob.voltMap[p2]
            if v1 in glob.VoltPosition and glob.VoltPosition[v1][1] > self.y:
                self.representation["a"]["lineColor2"] = glob.getVoltRGB(glob.voltMap[p2])
                self.representation["a"]["lineColor3"] = glob.getVoltRGB(glob.voltMap[p1])
            elif v2 in glob.VoltPosition and glob.VoltPosition[v2][1] < self.y:
                self.representation["a"]["lineColor2"] = glob.getVoltRGB(glob.voltMap[p2])
                self.representation["a"]["lineColor3"] = glob.getVoltRGB(glob.voltMap[p1])
            else:
                self.representation["a"]["lineColor2"] = glob.getVoltRGB(glob.voltMap[p1])
                self.representation["a"]["lineColor3"] = glob.getVoltRGB(glob.voltMap[p2])


        if self.name != "CN":
            self.representation["p"]["image"] = "symbols/electricity/%s.json" % self.name
        self.representation["s"] = {"label": ""}
        if self.name == "daozha":
            if glob.infoMap[self.tag]["point"] == 1:
                self.representation["a"]["state"] = True
            else:
                self.representation["a"]["state"] = False
        if self.name == "kaiguan":
            if glob.infoMap[self.tag]["point"] == 1:
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

