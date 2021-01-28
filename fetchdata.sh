#!/bin/bash

# ensure data dir is there
mkdir -p data

curl="timeout 10 curl --silent --connect-timeout 2 --max-time 5"

for kreis in $(cat kreiseinwohner.csv | cut -d ';' -f 1); do
  $curl -o data/$kreis.json "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/ArcGIS/rest/services/RKI_COVID19/FeatureServer/0/query?where=IdLandkreis%3D$kreis&objectIds=&time=&resultType=none&outFields=*&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=Meldedatum&groupByFieldsForStatistics=Meldedatum&outStatistics=%5B%7B%0D%0A++++%22statisticType%22%3A+%22sum%22%2C%0D%0A++++%22onStatisticField%22%3A+%22AnzahlFall%22%2C+%0D%0A++++%22outStatisticFieldName%22%3A+%22AnzahlFallAlle%22%0D%0A%7D%5D&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=json"
done

$curl -o data/kreisname.json "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/ArcGIS/rest/services/RKI_COVID19/FeatureServer/0/query?where=1%3D1&objectIds=&time=&resultType=none&outFields=Landkreis%2CIdLandkreis&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=true&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=pjson&token="


