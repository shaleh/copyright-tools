#!/bin/sh

virtualenv test-env/
test-env/bin/pip install -r test-requirements.txt
virtualenv-3.4 py34-test-env
py34-test-env/bin/pip install -r test-requirements.txt
