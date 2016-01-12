#!/bin/sh

rm -rf py34-test-env
rm -rf test-env
find . -type d -name __pycache__ -exec rm -rf {} \;
find . -type d -name '*.pyc' -exec rm -f {} \;
