#!/bin/bash

pushd "${0%/*}/.." > /dev/null

time PYTHONPATH=$PYTHONPATH:. \
python tests/integration/accuracy-test.py \
--puzzle-directory clues-files \
--answers-file data/puzzle-actual-answers.csv \
--solver-script $PWD/solve-current-actorle-puzzle.sh \
"$@"

popd > /dev/null