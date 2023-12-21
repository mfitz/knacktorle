#!/bin/bash

pushd "${0%/*}" > /dev/null

python actorle_solver.py \
--movies-file data/title.basics.tsv.gz \
--performances-file data/title.principals.tsv.gz \
--actors-file data/name.basics.tsv.gz "$@"
