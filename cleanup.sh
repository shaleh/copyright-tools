#!/bin/sh

rm -rf py34-test-env
rm -rf test-env
find . -name __pycaches__ -exec rm -rf {} \;
find . -name '*.pyc' -exec rm -f {} \;
