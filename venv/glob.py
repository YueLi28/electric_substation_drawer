import collections
VerticalBusPair = {}
HorizontalBusPair = {}
AllTrans = {}
adjDict = {}
BusCNID = set()
BusDict = {}
nodeSize = {"daozha": (48, 58), "daozhakai": (48, 58), "kaiguan": (24, 64), "singlearrow": (24, 64),
            "kaiguankai": (24, 64), "CN": (0, 0), "transformer2": (48, 60), "transformer3": (85, 66),
            "generator": (40, 40)}
daozhastat = {}
kaiguanstat = {}
sideBusFP = ['Disconnector', 'Disconnector', 'Breaker', 'Disconnector']
busPairFP = ['Disconnector', 'Disconnector']
transBus = collections.defaultdict(list)
globOffset = 200
voltMap = {}
colorRGB = {"red":"rgb(250,0,0)", "blue": "rgb(0,0,250)", "yellow": "rgb(250,250,0)", "white":"rgb(255,255,255)", "green":"rgb(0,250,150)", "cherry":"rgb(200,40,150)"}
voltColor = {220: "red", 35: "yellow", 110: "green", 10: "blue", 0:"cherry", 500:"cherry", 4:"white",
             11:"white", 20: "white",22: "white",13:"white", 6: "white", 60:"white", 15:"white", 18:"white"}
drawnNode = {}
infoMap = {}

def getVoltRGB(Volt):
    name = voltColor[Volt]
    return colorRGB[name]



class BusSkeleton:
    def __init__(self, cnID, x, y, w, dir):
        self.id = cnID
        self.x = x
        self.y = y
        self.w = w
        self.dir = dir
        self.reverseC = False
        self.is32 = False

    def define32(self):
        self.is32 = True
    def reverseConnector(self):
        self.reverseC = True

    def GetLength(self):
        BNumber = max(adjDict[self.id]-1, 1)
        return BNumber * 120

def isPairEnd(n, ID):
    if n in VerticalBusPair and n == VerticalBusPair[ID]:
        return True
    if n in HorizontalBusPair and n == HorizontalBusPair[ID]:
        return True
    return False

def reset():
    global BusDict
    global BusCNID
    global VerticalBusPair
    global adjDict
    global AllTrans
    global daozhastat
    global HorizontalBusPair
    global transBus
    global globOffset
    global kaiguanstat
    global voltMap
    global infoMap
    global CNpos
    global drawnNode

    drawnNode = {}
    CNpos = {}
    voltMap = {}
    kaiguanstat = {}
    globOffset = 400
    HorizontalBusPair = {}
    VerticalBusPair = {}
    AllTrans = {}
    adjDict = {}
    BusCNID = set()
    BusDict = {}
    daozhastat = {}
    transBus = collections.defaultdict(list)
    infoMap = {}

def placeBus(id, x, y, w, dir):
    BusDict[id] = BusSkeleton(id, x,y,w, dir)

def AddVerticalBusPair(b1, b2):
    VerticalBusPair[b1] = b2
    VerticalBusPair[b2] = b1

def AddHorizontalBusPair(b1, b2):
    HorizontalBusPair[b1] = b2
    HorizontalBusPair[b2] = b1

def fillRelation(adj, BusCNs):
    global adjDict
    global BusCNID
    adjDict = adj
    BusCNID = BusCNs

def PortWithinBus(x, node):
    attachedBus = findAttachedBus(node)
    if len(attachedBus) >= 1:
        busSk = BusDict[attachedBus[0]]
        if busSk.x - busSk.w/2 < x < busSk.x + busSk.w/2:
            return True
    return False


    #print bus.x, bus.w

def findAttachedBus(node):
    future = adjDict[node][:]
    visited = [node]
    res = []
    while future:
        tmp = future.pop()
        if tmp in visited:
            continue
        visited.append(tmp)
        if "transformer" not in tmp:
            future.extend(adjDict[tmp])
        if tmp in BusCNID:
            res.append(tmp)
    return res








visitedBusCN = set()