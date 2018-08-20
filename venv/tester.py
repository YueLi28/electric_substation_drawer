from drawer import *
class tester:
    def __init__(self):
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
                    print name, [[e, len(x.VoltBUSDict[e])] for e in x.VoltBUSDict], "VOLTAGE LEVEL:", len(x.VoltBUSDict)
                    x.newdraw(True)
                except Exception, err:
                    print "\tCANNOT DRAW: ", err