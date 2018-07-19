import glob
class Transformer2port:
    def __init__(self, name, x, y, direction, canv, adjDict):
        self.name = name
        self.size = [48, 60]
        self.x = x
        self.canv = canv
        self.adjDict = adjDict
        self.direction = direction
        if direction == "up":
            self.y = y + 33
            self.other = [self.x, self.y-30]
        else:
            self.y = y - 33
            self.other = [self.x, self.y+30]
        self.arrangeBus()

    def getCorrectPort(self, x, y):
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
        t = self.findTailHead()
        bus = self.BusConnected(t, self.name)
        if  bus== None:
            drawableHead = [x for x in self.adjDict[t] if x != self.name][0]
            x,y = self.getCorrectPort(0, 0)
            self.canv.drawTail(x, y, drawableHead, [t], self.direction)

    @staticmethod
    def BusConnected(node, fromnode):
        future = [node]
        visited = [fromnode]
        while future:
            tmp = future.pop()
            if tmp in visited:
                continue
            visited.append(tmp)
            if tmp in glob.BusCNID:
                return tmp
            future.extend(glob.adjDict[tmp])
        return None



class Transformer3port:
    def __init__(self, name, x, y, direction, canv, adjDict):
        self.name = name
        self.size = [85, 66]
        self.x = x
        if direction == "up":
            self.y = y + 33
            self.ports = [[self.x + 42.5, self.y], [self.x, self.y - 33]]
        else:
            self.y = y - 33
            self.ports = [[self.x + 42.5, self.y], [self.x, self.y + 33]]
        #print "Define a transformer: %s at (%d, %d), direction %s"%(name, self.x ,self.y, direction)
        self.direction = direction
        self.idx = 0
        self.adjDict = adjDict
        self.canv = canv
        self.np = self.findNeutralPoint()
        self.arrangeBus()



    def getCorrectPort(self, x, y):
        if y < self.y:#right port
            self.idx = 1
            return [self.x + 42.5, self.y]
        else: #lower port
            self.idx = 0
            return [self.x, self.y + 33]

    def nextIsStrightPort(self):
        if self.idx == 1:
            return True
        return False

    def getNextPort(self):
        res = self.ports[self.idx]
        self.idx += 1
        self.idx = self.idx % 2
        return res

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
                x,y = self.getNextPort()
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


    def findNeutralPoint(self):
        t = self.adjDict[self.name]
        for i in t:
            if "neutral_point" in i:
                return i


