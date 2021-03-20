#!/bin/bash

# ensure data dir is there and remove old files
mkdir -p data
find data/ -name "*.json" -mmin +240 -delete

# number of retries
retries=5

curlconfigbase=$(mktemp)
curlconfig=$(mktemp)
filelist=$(mktemp)

# base for generating the curl config file
cat << EOF > "$curlconfigbase"
url = https://services7.arcgis.com/mOBPykOjAyBO2ZKk/ArcGIS/rest/services/RKI_COVID19/FeatureServer/0/query?where=IdLandkreis%3D~~~landkreisid~~~&objectIds=&time=&resultType=none&outFields=*&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=Meldedatum&groupByFieldsForStatistics=Meldedatum&outStatistics=%5B%7B%0D%0A++++%22statisticType%22%3A+%22sum%22%2C%0D%0A++++%22onStatisticField%22%3A+%22AnzahlFall%22%2C+%0D%0A++++%22outStatisticFieldName%22%3A+%22AnzahlFallAlle%22%0D%0A%7D%5D&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=json
output = data/~~~landkreisid~~~.json
EOF

# the curl command
curlcommand="timeout 300 curl --silent --connect-timeout 2 --max-time 5 -K $curlconfig"

# trying to fetch all landkreise, repeat missing landkreise N times at max
for i in $(seq 1 $retries); do
  find data/ -size -4k -delete
  ls data/ > "$filelist"
  echo "" > "$curlconfig"
  while read kreis; do
    [ $(grep -c "$kreis" "$filelist") -eq 0 ] && sed "s/~~~landkreisid~~~/$kreis/" "$curlconfigbase" >> "$curlconfig"
  done <<< "$(cut -d ';' -f 1 kreiseinwohner.csv)"
  [ $(stat --format=%s "$curlconfig") -eq 1 ] && break
  $curlcommand
done

cat << EOF > "$curlconfig"
url = https://services7.arcgis.com/mOBPykOjAyBO2ZKk/ArcGIS/rest/services/RKI_COVID19/FeatureServer/0/query?where=1%3D1&objectIds=&time=&resultType=none&outFields=Landkreis%2CIdLandkreis&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=true&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=pjson&token=
output = data/kreisname.json
EOF

# trying to fetch all landkreis names, repeat up to N times if necessary
# and do a backup, replace json with backup if nothing could be fetched
for i in $(seq 1 $retries); do
  $curlcommand
  [ $(stat --format=%s data/kreisname.json) -gt 16384 ] && cp -a data/kreisname.json data/kreisname.bak && break
done
[ -e data/kreisname.json ] || cp -a data/kreisname.bak data/kreisname.json

rm $curlconfigbase
rm $curlconfig
rm $filelist



