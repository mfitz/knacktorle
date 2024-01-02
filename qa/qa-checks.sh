#!/usr/bin/env bash

pushd "${0%/*}"

./lint-check.sh && ./coverage/code-coverage.sh

return_code=$?

popd

exit ${return_code}