#!/bin/sh

mkdir test-run
cp pristine/* test-run/
../../tools/update_copyright_year.py --copyright-name="Foo Corp, Inc." --year=2016 test-run/*

if ! diff -r expected-2016 test-run
then
	echo "2016 test run failed"
	exit 1
fi

rm -rf test-run

mkdir test-run
cp pristine/* test-run/
../../tools/update_copyright_year.py --copyright-name="Foo Corp, Inc." --year=2017 test-run/*

if ! diff -r expected-2017 test-run
then
	echo "2017 test run failed"
	exit 1
fi

rm -rf test-run

mkdir test-run
cp pristine/* test-run/
../../tools/update_copyright_year.py --copyright-name="Foo Corp, Inc." --year=2014 test-run/*

if ! diff -r expected-2014 test-run
then
	echo "2014 test run failed"
	exit 1
fi
