#!/bin/bash

set +x

export PYTHONPATH=`pwd`/tools

TEST_ENV=${TEST_ENV:-test-env}

${TEST_ENV}/bin/nosetests --with-coverage --cover-package=tools
