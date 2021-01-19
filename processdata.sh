#!/bin/bash

cd $(dirname $(readlink -f $0))

bwd=$(dirname $(readlink -f $0))
cd $bwd
[ ! -d 2020-rki-archive ] && git clone https://github.com/ard-data/2020-rki-archive
cd 2020-rki-archive
git pull &>/dev/null || echo "git pull failed. please check."
cd $bwd
currentarchive=$(find 2020-rki-archive/data/2_parsed/ -type f -size +5M | sort  | tail -n 1)
bzcat $currentarchive > current.json

python3 processdata.py > data.json
echo -n "labels = " > data.js
cat data.json | jq .labels -c >> data.js
echo -n "datasets = " >> data.js
cat data.json | jq .datasets -c >> data.js

cat tidy.index.html | sed "s/~~~LASTUPDATE~~~/$(basename $currentarchive)/" > index.html

which minify &>/dev/null && minify index.html > im.html && mv im.html index.html
