#!/bin/sh

if [ -d test-run ]; then
    rm -rf test-run
fi

mkdir test-run
cp pristine/* test-run/
../../tools/update_copyright_name.py --old-copyright="Foo Corp, Inc." --new-copyright="Bar Corp, Inc." test-run/*

if ! diff -r expected test-run
then
    echo "test run failed"
    exit 1
fi

rm -rf test-run
