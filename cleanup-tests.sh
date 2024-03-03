#!/bin/sh

rm -rf test-env
find . -type d -name __pycache__ -exec rm -rf {} \;
