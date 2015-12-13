#!/usr/bin/env python
from collections import OrderedDict
import json
from pprint import pprint
import sys

def getModels(jsonIn):
    with open(jsonIn) as dataFile:
        jsonFile = json.load(dataFile)
    
    modelList = []
    for jason in jsonFile:
        modelList.append(jason['model'])

    uniqueList = list(OrderedDict.fromkeys(modelList))

    for model in uniqueList:
        print(model)
    #pprint(jsonFile)

if __name__ == "__main__":
    getModels(sys.argv[1])
