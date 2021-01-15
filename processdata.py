import json
import time
import csv
import hashlib
import sys

jsonfile="current.json"
einwohnercsvfile="kreiseinwohner.csv"

kreisdaten = {}
lksearchlist = []

with open ( einwohnercsvfile ) as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    for row in reader:
        kreisdaten[row[0]]=int(row[2])
        lksearchlist.append(row[0]);

tagemitdaten = []

# read data
with open ( jsonfile ) as f:
    data = json.load(f)
    resultset = {}
    datadict = {}

    counter=0
    ec=0

    for dataobject in data:
        try:
            for feature in dataobject['features']:
                try:
#                print(json.dumps(feature,indent=True))
                    if not feature["attributes"]["IdLandkreis"] in datadict:
                        datadict[feature["attributes"]["IdLandkreis"]]={}

                    if "Kreisname" not in datadict[feature["attributes"]["IdLandkreis"]]:
                        datadict[feature["attributes"]["IdLandkreis"]]["Kreisname"] = feature["attributes"]["Landkreis"]
                    if "AnzahlFall" not in datadict[feature["attributes"]["IdLandkreis"]]:
                        datadict[feature["attributes"]["IdLandkreis"]]["AnzahlFall"] = {}

                    if feature["attributes"]["Meldedatum"] in datadict[feature["attributes"]["IdLandkreis"]]["AnzahlFall"]:
                        datadict[feature["attributes"]["IdLandkreis"]]["AnzahlFall"][feature["attributes"]["Meldedatum"]]+=feature["attributes"]["AnzahlFall"]
                    else:
                        datadict[feature["attributes"]["IdLandkreis"]]["AnzahlFall"][feature["attributes"]["Meldedatum"]]=feature["attributes"]["AnzahlFall"]
                    counter+=1
                except:
                    ec+=1
                    print("Feature parse error")
                    print(json.dumps(feature,indent=True),file=sys.stderr)
                    pass
        except:
            print("Dataobject without features")
            print(json.dumps(dataobject,indent=True),file=sys.stderr)
            pass

#print(json.dumps(datadict,indent=True))
#print(counter,ec)

#quit()

for idlandkreis in sorted(lksearchlist):
    try:
        resultset[idlandkreis]={}
        resultset[idlandkreis]["AnzahlFall"]={}
        resultset[idlandkreis]["Einwohner"]=kreisdaten[idlandkreis]
        resultset[idlandkreis]["Kreisname"]=datadict[idlandkreis]["Kreisname"]
        for key in sorted(datadict[idlandkreis]["AnzahlFall"]):
            if key not in tagemitdaten:
                tagemitdaten.append(key)
            resultset[idlandkreis]["AnzahlFall"][time.strftime('%d.%m.%Y', time.localtime(key/1000))] = datadict[idlandkreis]["AnzahlFall"][key]
    except:
        print(idlandkreis,file=sys.stderr)
        pass

#            pass

#print(json.dumps(resultset,indent=True))

# create a list with all days
# this will serve as label for the final graph and to check if
# any kreis is missing some data
labels = []
for tag in sorted(tagemitdaten):
    labels.append(time.strftime('%d.%m.%Y', time.localtime(tag/1000)))


# print(resultset)

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

#print(json.dumps(resultset,indent=True))

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
        sdi = round(100000/kreisdaten[landkreiskey]*sds)
        dataset["data"].append(sdi)

    chartdata["datasets"].append(dataset)

# the only thing left is to print the json data
print(json.dumps(chartdata,indent=True))
