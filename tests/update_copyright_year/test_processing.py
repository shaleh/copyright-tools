# -*- coding: utf-8 -*-

import six
import unittest

try:
    import mock
except ImportError:
    import unittest.mock as mock

from update_copyright_year import CopyrightedFile, UpdateCopyright


def patch_open():
    if six.PY2:
        open_location = "__builtin__.open"
    else:
        open_location = "builtins.open"

    return mock.patch(open_location)


class TestUpdateCopyright(unittest.TestCase):
    def testRegex(self):
        u = UpdateCopyright("Foo Corp, Inc.")
        last_year = u._year - 1

        self.assertIsNotNone(u._pat.match(" # Copyright: 2014 Foo Corp, Inc."))
        self.assertIsNotNone(u._pat.match(" # (c) Copyright: 2014 Foo Corp, Inc."))
        self.assertIsNotNone(u._pat.match(" # Copyright (c) 2014 Foo Corp, Inc."))
        self.assertIsNotNone(u._pat.match(" # © Copyright: 2014 Foo Corp, Inc."))


class TestCopyrightedFile(unittest.TestCase):
    def setUp(self):
        self.this_year = 2016
        self.last_year = self.this_year - 1
        self.copyright_name = "Foo Corp, Inc."
        self.u = UpdateCopyright(self.copyright_name)
        self.cf = CopyrightedFile(None, self.u._pat, self.this_year)

    def testProcessLineNoMatch(self):
        self.assertIsNone(self.cf._process_line("# Foo"))

    def testPrcoessLineThisYear(self):
        result = self.cf._process_line("# Copyright {} {}".format(self.this_year, self.copyright_name))
        self.assertIs("", result)

    def testPrcoessLineThisYearComplex(self):
        result = self.cf._process_line("# Copyright 2010-2012,{} {}".format(self.this_year, self.copyright_name))
        self.assertIs("", result)
        result = self.cf._process_line("# Copyright 2010-{} {}".format(self.last_year - 2000, self.copyright_name))
        self.assertEquals("# Copyright 2010-{} {}".format(self.this_year, self.copyright_name),
                          result)

    def testPrcoessLineRegionWithThisYear(self):
        start = self.this_year - 2
        end = self.this_year + 2
        result = self.cf._process_line("# Copyright {}-{} {}".format(start, end, self.copyright_name))
        self.assertIs("", result)

    def testProcessLineLastYear(self):
        result = self.cf._process_line("# Copyright {} {}".format(self.last_year, self.copyright_name))
        self.assertEquals("# Copyright {}-{} {}".format(self.last_year, self.this_year, self.copyright_name),
                          result)

    def testProcessLineOlder(self):
        year = self.this_year - 3
        result = self.cf._process_line("# Copyright {} {}".format(year, self.copyright_name))
        self.assertEquals("# Copyright {},{} {}".format(year, self.this_year, self.copyright_name),
                          result)

    def testProcessGood(self):
        self.fake_fp = six.StringIO("""
# Copyright {} {}

print "monkey"
""".format(self.last_year, self.copyright_name))
        self.cf._fp = self.fake_fp
        self.cf.process("dummy")
        self.assertEquals(4, len(self.cf._lines))
        self.assertEquals("# Copyright 2015-{} {}\n".format(self.this_year, self.copyright_name),
                          self.cf._lines[1])
        self.assertTrue(self.cf._needs_updating)

        with patch_open() as fake_open:
            self.cf.update("dummy")
            self.assertTrue(fake_open.called)

        # Ensure dry run works
        with patch_open() as fake_open:
            self.cf.update("dummy", dry_run=True)
            self.assertFalse(fake_open.called)

    def testProcessNone(self):
        self.fake_fp = six.StringIO("""
# BSD Copyright 2015 Some one

1
2
3
4
5
6
7
8
9
10
""")
        self.cf._fp = self.fake_fp

        self.cf.process("dummy")
        # prove only read 10 lines
        self.assertEquals(10, len(self.cf._lines))
        self.assertFalse(self.cf._needs_updating)

        with patch_open() as fake_open:
            self.cf.update("dummy")
            self.assertFalse(fake_open.called)
