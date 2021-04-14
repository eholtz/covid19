#!/bin/bash

# ensure data dir is there and remove old files
mkdir -p data
find data/ -name "*.ndjson" -mmin +240 -delete
find data/ -name "*.json" -mmin +240 -delete
find data/ -name "*.txt" -mmin +240 -delete
find data/ -name "*.bak" -mmin +240 -delete

# clean up from previous versions
[ -d data-aligned ] && rm -rf data-aligned

# number of retries
retries=5

curlconfig=$(mktemp)

# base for generating the curl config file
cat << EOF > "$curlconfig"
url = https://storage.googleapis.com/brdata-public-data/rki-corona-archiv/2_parsed/index.txt
output = data/archives.txt
EOF

# the curl command
curlcommand="timeout 300 curl --silent --connect-timeout 2 --max-time 5 -K $curlconfig"

# fetch the last archive entry from ard data
for i in $(seq 1 $retries); do
  $curlcommand
    [ $(stat --format=%s data/archives.txt) -gt 1024 ] && break
done

lastarchive=$(tail -n 1 data/archives.txt)

cat << EOF > "$curlconfig"
url = https://storage.googleapis.com/brdata-public-data/rki-corona-archiv/2_parsed/$lastarchive
output = data/data-current.ndjson.xz
EOF

# fetch the last archive from ard data
for i in $(seq 1 $retries); do
  $curlcommand
  [ $(stat --format=%s data/data-current.ndjson.xz) -gt 16384 ] && break
done

unxz data/data-current.ndjson.xz

rm $curlconfig

