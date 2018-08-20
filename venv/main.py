#!/usr/bin/env python
# -*- coding: utf-8 -*-

from drawer import *
#This place stores the offline data
workingdir = u"/home/liyue/tmp/"

#The json file is output to this place
JsonDir = u"/tmp/"


queryURL = u"http://192.168.2.5:9000/query/TwoOptionsNAME?SubstationNAME="

#Should always be true if in a production environment
isProductionEnvironment = False



inp = "国调.复龙换流站"
inp = unicode(inp, "utf-8")
k = drawer(inp, workingdir, queryURL, JsonDir)
k.newdraw(isProductionEnvironment)
print "Done"


