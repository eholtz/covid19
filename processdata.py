import json
import time
import csv
import hashlib
import sys
import os
import re

datadir="data"
einwohnercsvfile="kreiseinwohner.csv"

kreisdaten = {}
lksearchlist = []

with open ( einwohnercsvfile ) as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    for row in reader:
        kreisdaten[row[0]]=int(row[2])
        lksearchlist.append(row[0])

resultset = {}
tagemitdaten = {}
kreisnames = {}

# we will calculate germanys overall inzidenzwert
resultset["BRD"] = {}
resultset["BRD"]["Einwohner"] = 0
resultset["BRD"]["AnzahlFall"] = {}
resultset["BRD"]["Kreisname"] = "BRD Gesamt"

# read data new
with open ( datadir + "/data-current.ndjson" ) as ndjsonfile:
    for jsonstring in ndjsonfile:
        jsonobject = json.loads(jsonstring)
        kreisid = jsonobject['IdLandkreis']
        kreisid = "{:0>5}".format(kreisid)
        meldedatum = jsonobject['MeldedatumISO']
        anzahlfall = jsonobject['AnzahlFall']
        kreisname = jsonobject['Landkreis']
        # add the number of cases to the existing cases
        try:
            resultset[kreisid]["AnzahlFall"][meldedatum] += anzahlfall
        except:
            # this branch gets executed if the kreisid has not been initialized
            if kreisid not in resultset:
                resultset[kreisid] = {}
                resultset[kreisid]["AnzahlFall"] = {}
            resultset[kreisid]["AnzahlFall"][meldedatum] = anzahlfall
        
        # set kreisname and einwohneranzahl
        try:
            kreisnames[kreisid] = kreisname
            resultset[kreisid]["Einwohner"] = kreisdaten[kreisid]
        except:
            pass

        # add the number of cases to the BRD count
        try:
            resultset["BRD"]["AnzahlFall"][meldedatum] += anzahlfall
        except:
            resultset["BRD"]["AnzahlFall"][meldedatum] = anzahlfall
            tagemitdaten[meldedatum] = True
            
# fill in all the kreisnames - and while we're at it: compute the grand total of the population
for kreisid in resultset:
    if kreisid != "BRD":
        resultset[kreisid]["Kreisname"] = kreisnames[kreisid]
        resultset["BRD"]["Einwohner"] += kreisdaten[kreisid]

# create a list with all days
# this will serve as label for the final graph and to check if
# any kreis is missing some data
labels = []
for tag in sorted(tagemitdaten):
    datum = tag.split('-')
    labels.append(datum[2]+"."+datum[1]+"."+datum[0])

# go through all kreise for a first time to fill in gaps we might have
# so the calculation of inzidenzwert will not be off
for kreisid in resultset:
    nogapdict = {}
    for tag in sorted(tagemitdaten):
        try:
            if tag in resultset[kreisid]["AnzahlFall"]:
                nogapdict[tag] = resultset[kreisid]["AnzahlFall"][tag]
            else:
                nogapdict[tag] = 0
        except:
            pass
    resultset[kreisid]["AnzahlFallNoGaps"] = nogapdict

# we can now be sure to have data for each single day we want to calculate
# so we go ahead and fill the chart data datasets
chartdata = {}
chartdata["labels"] = labels
chartdata["datasets"] = []
for landkreiskey in resultset:
    dataset = {}
    if "Kreisname" not in resultset[landkreiskey]:
        continue
    dataset["label"] = resultset[landkreiskey]["Kreisname"]
    dataset["kreisid"] = landkreiskey
    dataset["fill"] = False
    dataset["borderColor"] = "#"+hashlib.sha1(dataset["label"].encode('utf-8')).hexdigest()[0:6]
    dataset["backgroundColor"] = "#"+hashlib.sha1(dataset["label"].encode('utf-8')).hexdigest()[0:6]
    dataset["hidden"] = False
    dataset["data"] = []
    sevendays = []
    # we want the inzidenzwert (no of infections the last 7 days for 100000 inhabitants)
    for tag in sorted(tagemitdaten):
        sevendays.append(resultset[landkreiskey]["AnzahlFallNoGaps"][tag])
        if len(sevendays) > 7:
            sevendays.pop(0)
        sds = 0
        for num in sevendays:
            sds += num
        sdi = round(100000/resultset[landkreiskey]["Einwohner"]*sds)
        dataset["data"].append(sdi)

    chartdata["datasets"].append(dataset)

# the only thing left is to print the json data
print(json.dumps(chartdata, indent = True))
