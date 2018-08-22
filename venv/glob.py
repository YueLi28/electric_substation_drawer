import collections
VerticalBusPair = {}
HorizontalBusPair = {}
AllTrans = {}
adjDict = {}
BusCNID = set()
BusDict = {}
nodeSize = {"daozha": (48, 58), "daozhakai": (48, 58), "kaiguan": (24, 64), "singlearrow": (24, 64),
            "kaiguankai": (24, 64), "CN": (0, 0), "transformer2": (72, 90), "transformer3": (127.5, 99),
            "generator": (40, 40), "C_S":(40, 40)}
daozhastat = {}
kaiguanstat = {}
sideBusFP = ['Disconnector', 'Disconnector', 'Breaker', 'Disconnector']
busPairFP = ['Disconnecto   r', 'Disconnector']
transBus = collections.defaultdict(list)
globOffset = None
voltMap = {}
colorRGB = { "white":"rgb(255,255,255)", "cherry":"rgb(200,40,150)", "500Color":"rgb(255,0,0)", "220Color":"rgb(255,0,255)",
            "10Color":"rgb(170,170,0)", "35Color":"rgb(255,255,0)", "110Color":"rgb(240,65,85)","11Color":"rgb(0,89,127)",
            "6Color":"rgb(0,0,0)", "13Color":"rgb(0,210,0)"}
voltColor = {220: "220Color", 35: "35Color", 110: "110Color", 10: "10Color", 0:"cherry", 500:"500Color", 4:"white",
             11:"11Color", 20: "white",22: "white",13:"13Color", 6: "6Color", 60:"white", 15:"white", 18:"white", 24:"white"}
drawnNode = {}
infoMap = {}
VoltPosition = {}
TransformerLine = {}

stationX1 = None
stationX2 = None
stationY = None

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

def isPair(n, ID):
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
    global VoltPosition
    global TransformerLine
    global stationX1
    global stationX2
    global stationY

    TransformerLine = {}
    VoltPosition = {}
    drawnNode = {}
    CNpos = {}
    voltMap = {}
    kaiguanstat = {}
    globOffset = None
    HorizontalBusPair = {}
    VerticalBusPair = {}
    AllTrans = {}
    adjDict = {}
    BusCNID = set()
    BusDict = {}
    daozhastat = {}
    transBus = collections.defaultdict(list)
    infoMap = {}
    stationX1 = None
    stationX2 = None
    stationY = None

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




def collidewithOther(x, y, portX):
    res = False
    if y in TransformerLine:
        lines = TransformerLine[y]
        for l in lines:
            e1,e2 = l
            if max(x, portX) < min(e1, e2) or min(x, portX) > max(e1, e2): #No collide
                pass
            else:
                res = True
    else:
        TransformerLine[y] =[]
    TransformerLine[y].append([x, portX])
    return res







visitedBusCN = set()