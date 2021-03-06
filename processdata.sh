#!/bin/bash

cd $(dirname $(readlink -f $0))

bwd=$(dirname $(readlink -f $0))
cd $bwd
./fetchdata.sh

python3 processdata.py > data.json
echo -n "labels = " > data.js
cat data.json | jq .labels -c >> data.js
echo -n "datasets = " >> data.js
cat data.json | jq .datasets -c >> data.js

cat tidy.index.html | sed "s/~~~LASTUPDATE~~~/$(date)/" > index.html


which minify &>/dev/null && minify index.html > im.html && mv im.html index.html
