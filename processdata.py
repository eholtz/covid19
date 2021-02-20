import json
import time
import csv
import hashlib
import sys
import os
import re

datadir="data-aligned"
einwohnercsvfile="kreiseinwohner.csv"

kreisdaten = {}
lksearchlist = []

with open ( einwohnercsvfile ) as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    for row in reader:
        kreisdaten[row[0]]=int(row[2])
        lksearchlist.append(row[0])

resultset={}
tagemitdaten={}
kreisnames={}

# we will calculate germanys overall inzidenzwert
resultset["BRD"]={}
resultset["BRD"]["Einwohner"]=0
resultset["BRD"]["AnzahlFall"]={}
resultset["BRD"]["Kreisname"]="BRD Gesamt"

# read data
files = os.listdir(datadir)
for file in sorted(files):
    # read the kreisnames if it is the kreisname file
    if re.match(r'kreisname\.json',file):
        with open ( datadir + "/" + file ) as jsonfile:
            data = json.load(jsonfile)
            for entry in data:
                kreisnames[entry["attributes"]["IdLandkreis"]]=entry["attributes"]["Landkreis"]
    # read the infection numbers if it is a kreisdata file
    if re.match(r'[0-9]{5}\.json',file):
        # this is a file named [kreisid].json
        kreisid=file[0:5]
        resultset[kreisid]={}
        resultset[kreisid]["AnzahlFall"]={}
        resultset[kreisid]["Einwohner"]=kreisdaten[kreisid]
        with open ( datadir + "/" + file ) as jsonfile:
            data = json.load(jsonfile)
            for entry in data:
                datestring = time.strftime('%d.%m.%Y', time.localtime(entry["attributes"]["Meldedatum"]/1000))
                resultset[kreisid]["AnzahlFall"][datestring]=entry["attributes"]["AnzahlFallAlle"]
                tagemitdaten[entry["attributes"]["Meldedatum"]]=True
                # add to the grand total. first assignment will fail, so in this case just write the value
                try:
                    resultset["BRD"]["AnzahlFall"][datestring]+=entry["attributes"]["AnzahlFallAlle"]
                except:
                    resultset["BRD"]["AnzahlFall"][datestring]=entry["attributes"]["AnzahlFallAlle"]

# fill in all the kreisnames - and while we're at it: compute the grand total of the population
for kreisid in resultset:
    if kreisid!="BRD":
        resultset[kreisid]["Kreisname"]=kreisnames[kreisid]
        resultset["BRD"]["Einwohner"]+=kreisdaten[kreisid]

# create a list with all days
# this will serve as label for the final graph and to check if
# any kreis is missing some data
labels = []
for tag in sorted(tagemitdaten):
    labels.append(time.strftime('%d.%m.%Y', time.localtime(tag/1000)))

# go through all kreise for a first time to fill in gaps we might have
# so the calculation of inzidenzwert will not be off
for landkreiskey in resultset:
    nogapdict = {}
    for label in labels:
        try:
            if label in resultset[landkreiskey]["AnzahlFall"]:
                nogapdict[label]=resultset[landkreiskey]["AnzahlFall"][label]
            else:
                nogapdict[label]=0
        except:
            pass
    resultset[landkreiskey]["AnzahlFallNoGaps"]=nogapdict

# we can now be sure to have data for each single day we want to calculate
# so we go ahead and fill the chart data datasets
chartdata = {}
chartdata["labels"]=labels
chartdata["datasets"]=[]
for landkreiskey in resultset:
    dataset={}
    if "Kreisname" not in resultset[landkreiskey]:
        continue
    dataset["label"]=resultset[landkreiskey]["Kreisname"]
    dataset["fill"]=False
    dataset["borderColor"]="#"+hashlib.sha1(dataset["label"].encode('utf-8')).hexdigest()[0:6]
    dataset["hidden"]=False
    dataset["data"]=[]
    sevendays = []
    # we want the inzidenzwert (no of infections the last 7 days for 100000 inhabitants)
    for label in labels:
        sevendays.append(resultset[landkreiskey]["AnzahlFallNoGaps"][label])
        if len(sevendays) > 7:
            sevendays.pop(0)
        sds = 0
        for num in sevendays:
            sds += num
        sdi = round(100000/resultset[landkreiskey]["Einwohner"]*sds)
        dataset["data"].append(sdi)

    chartdata["datasets"].append(dataset)

# the only thing left is to print the json data
print(json.dumps(chartdata,indent=True))
