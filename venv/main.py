#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from drawer import *
#workingdir stores the offline cache data
workingdir = u"/home/liyue/tmp/"

#The json file is output to this JsonDir
JsonDir = u"/tmp/"


queryURL = u"http://192.168.2.5:9000/query/TwoOptionsNAME?SubstationNAME="

#Should always be true in a production environment
isProductionEnvironment = False


if __name__ == "__main__":
    if isProductionEnvironment:
        if len(sys.argv) != 2:
            raise ValueError("Wrong number of arguments")
        else:
            inp = sys.argv[1]
    else:
        inp = "四川.德昌风电厂"
    inp = unicode(inp, "utf-8")
    k = drawer(inp, workingdir, queryURL, JsonDir)
    k.newdraw(isProductionEnvironment)
    print "Done"


