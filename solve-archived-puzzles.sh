#!/bin/bash

start=$(date +%s)

for puzzle in $(find clues-files -type f)
do
  bash solve-current-actorle-puzzle.sh --clues-file $puzzle | egrep -i 'dude|clues file at'
done

end=$(date +%s)
runtime=$((end-start))

printf "\nFinished in %s" $runtime
