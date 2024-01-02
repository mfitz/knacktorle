#!/bin/bash

pushd "${0%/*}"/../.. > /dev/null

python3 -m pytest -vv \
--cov=. \
--cov-report=html:reports/coverage \
--cov-report=xml:reports/coverage/coverage.xml \
--cov-config=qa/coverage/.coveragerc \
tests/
return_code=$?

popd > /dev/null

exit $return_code
