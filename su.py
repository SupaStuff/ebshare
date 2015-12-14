#!/usr/bin/env python
from userAuth.models import create_profile
from django.contrib.auth.models import User
from collections import OrderedDict
import json
import sys

def su():
    with open('db.json') as dataFile:
        jsonFile = json.load(dataFile)
    
    sulist = []
    for jason in jsonFile:
        if jason['model'] == "auth.user":
            if jason['fields']['is_superuser']:
                sulist.append(User.objects.get(pk=jason['pk']))

    for user in sulist:
        create_profile(user)
        print("created profile for SU " + user.username)
    #pprint(jsonFile)

if __name__ == "__main__":
    su()
