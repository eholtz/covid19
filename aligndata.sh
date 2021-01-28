#!/bin/bash

mkdir -p data-aligned

for file in $(find ./data -iname "*.json"); do
  cat $file | jq -c .features > data-aligned/$(basename $file)
done

