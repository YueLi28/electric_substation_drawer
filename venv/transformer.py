import glob
class Transformer2port:
    def __init__(self, name, x, y, direction, canv, adjDict):
        self.name = name
        self.size = [72, 90]
        self.x = x
        self.canv = canv
        self.adjDict = adjDict
        self.direction = direction
        self.TailDrawn = False

        if direction == "up":
            self.y = y + self.size[1]/2
            self.other = [self.x, self.y-self.size[1]/2]
        else:
            self.y = y - self.size[1]/2
            self.other = [self.x, self.y+self.size[1]/2]
        self.arrangeBus()
        self.drawTails()

    def getCorrectPort(self, volt):
        return self.other

    def findTailHead(self):
        tailHs = [x for x in self.adjDict[self.name] if "transformer" in x]
        if len(tailHs) > 1:
            raise ValueError("Abnormal 2 port transformer:" + self.name)
        elif len(tailHs) == 0:
            return
        return tailHs[0]


    def arrangeBus(self):
        t = self.findTailHead()
        bus = self.BusConnected(t, self.name)
        if  bus != None:
            glob.transBus[bus].append(self)

    def drawTails(self):
        if self.TailDrawn:
            return
        t = self.findTailHead()
        bus = self.BusConnected(t, self.name)
        if  bus == None:
            drawableHead = [x for x in self.adjDict[t] if x != self.name][0]
            x,y = self.getCorrectPort(None)
            if self.direction == "up":
                off = -40
            else:
                off = 40
            self.canv.drawLine(x,y, x, y+off,glob.voltMap[t])
            self.canv.drawTail(x, y+off, drawableHead, [t], self.direction)
            self.TailDrawn = True

    @staticmethod
    def BusConnected(node, fromnode):
        future = glob.adjDict[node][:]
        visited = [fromnode, node]
        while future:
            tmp = future.pop()
            if tmp in visited:
                continue
            visited.append(tmp)
            if tmp in glob.BusCNID:
                return tmp
            if "transformer" not in tmp:
                future.extend(glob.adjDict[tmp])
        return None

    @staticmethod
    def hasGenerator(node, fromnode):
        future = [node]
        visited = [fromnode]
        while future:
            tmp = future.pop()
            if tmp in visited:
                continue
            visited.append(tmp)
            if "unit" in tmp:
                return True
            if tmp not in glob.BusCNID:
                future.extend(glob.adjDict[tmp])
        return False

class Transformer3port:
    def __init__(self, name, x, y, direction, canv, adjDict):
        self.name = name
        self.size = [127.5, 99]
        self.x = x
        if direction == "up":
            self.y = y + self.size[1]/2
            self.ports = [[self.x + self.size[0]/2, self.y], [self.x, self.y - self.size[1]/2]]
        else:
            self.y = y - self.size[1]/2
            self.ports = [[self.x + self.size[0]/2, self.y], [self.x, self.y + self.size[1]/2]]
        #print "Define a transformer: %s at (%d, %d), direction %s"%(name, self.x ,self.y, direction)
        self.direction = direction
        self.idx = 0
        self.adjDict = adjDict
        self.canv = canv
        self.rightPortVolt = None
        self.lowerPortVolt = None
        self.np = self.findNeutralPoint()
        self.arrangeBus()
        self.findPortVolt()


    def findPortVolt(self):
        np = [x for x in glob.adjDict[self.name] if "neutral_point" in x][0]
        p1, p2 = [x for x in glob.adjDict[np] if x != self.name]
        v1, v2 = glob.voltMap[p1], glob.voltMap[p2]
        if v1 < v2:
            p1, p2 = p2, p1
            v1, v2 = glob.voltMap[p1], glob.voltMap[p2]

        if v1 in glob.VoltPosition and glob.VoltPosition[v1][1] > self.y:
            self.rightPortVolt = glob.voltMap[p2]
            self.lowerPortVolt = glob.voltMap[p1]
        elif v2 in glob.VoltPosition and glob.VoltPosition[v2][1] < self.y:
            self.rightPortVolt = glob.voltMap[p2]
            self.lowerPortVolt = glob.voltMap[p1]
        else:
            self.rightPortVolt = glob.voltMap[p1]
            self.lowerPortVolt = glob.voltMap[p2]

    def getCorrectPort(self, volt):
        return self.getPortFromVolt(volt)

    def nextIsStrightPort(self):
        if self.idx == 1:
            return True
        return False

    def getNextPort(self):
        res = self.ports[self.idx]
        self.idx += 1
        self.idx = self.idx % 2
        return res

    def getPortFromVolt(self, volt):
        x,y = self.getNextPort()
        if volt == self.rightPortVolt:
            if y != self.y:
                x,y = self.getNextPort()
        else:
            if y == self.y:
                x,y = self.getNextPort()
        return x, y

    def arrangeBus(self):
        tailHs = [x for x in self.adjDict[self.np] if x != self.name]
        for h in tailHs:
            bus = self.BusConnected(h, self.np)
            if bus != None:
                glob.transBus[bus].append(self)

    def drawTails(self):
        tailHs = [x for x in self.adjDict[self.np] if x != self.name]
        tailHs.sort(key=lambda x:glob.voltMap[x], reverse=True)
        for h in tailHs:
            bus = self.BusConnected(h, self.np)
            if bus == None:
                drawableHead = [x for x in self.adjDict[h] if x != self.np][0]
                x,y = self.getPortFromVolt(glob.voltMap[h])
                if y == self.y:#horizontal
                    self.canv.drawLine(x,y,x+40,y,glob.voltMap[h])
                    self.canv.drawTail(x+40, y, drawableHead, [h], self.direction, 73)
                else: #vertical
                    self.canv.drawTail(x, y, drawableHead, [h], self.direction)


    def BusConnected(self, node, fromnode):
        future = [node]
        visited = [fromnode]
        while future:
            tmp = future.pop()
            if tmp in visited:
                continue
            visited.append(tmp)
            if tmp in glob.BusCNID:
                return tmp
            future.extend(self.adjDict[tmp])
        return None

    def isBlockingOtherTransformers(self):
        tailHs = [x for x in self.adjDict[self.np] if x != self.name]
        tailHs.sort(key=lambda x: glob.voltMap[x], reverse=True)
        for h in tailHs:
            bus = self.BusConnected(h, self.np)
            if bus:
                busY = glob.VoltPosition[glob.infoMap[bus]['volt']][1]
                if busY < self.y:
                    return True
        return False


    def findNeutralPoint(self):
        t = self.adjDict[self.name]
        for i in t:
            if "neutral_point" in i:
                return i


