# -*- coding: utf-8 -*-

import six
import unittest

try:
    import mock
except ImportError:
    import unittest.mock as mock

from update_copyright_year import CopyrightedFile
from update_copyright_year import UpdateCopyright
from update_copyright_year import insert_year


def patch_open():
    if six.PY2:
        open_location = "__builtin__.open"
    else:
        open_location = "builtins.open"

    return mock.patch(open_location)


class TestInsertYear(unittest.TestCase):
    def testSingles(self):
        years = [(2010,2010),(2012,2012)]
        result = insert_year(2015, years)
        self.assertTrue(result)
        self.assertEquals([(2010,2010),(2012,2012),(2015,2015)], years)

        years = [(2014,2014)]
        result = insert_year(2016, years)
        self.assertTrue(result)
        self.assertEquals([(2014,2014),(2016,2016)], years)

        years = [(2014,2014)]
        result = insert_year(2012, years)
        self.assertTrue(result)
        self.assertEquals([(2012, 2012), (2014,2014)], years)

    def testWithinExisting(self):
        years = [(2007,2007),(2010,2015)]
        expected = years[:]
        result = insert_year(2014, years)
        self.assertFalse(result)
        self.assertEquals(expected, years)

        years = [(2010,2015)]
        expected = years[:]
        result = insert_year(2014, years)
        self.assertFalse(result)
        self.assertEquals(expected, years)

        years = [(2015,2015)]
        expected = years[:]
        result = insert_year(2015, years)
        self.assertFalse(result)
        self.assertEquals(expected, years)

    def testUpdateExisting(self):
        base_years = [(2006,2006),(2009,2011),(2014,2015)]

        years = base_years[:]
        result = insert_year(2007, years)
        self.assertTrue(result)
        self.assertEquals([(2006,2007),(2009,2011),(2014,2015)], years)

        years = base_years[:]
        result = insert_year(2008, years)
        self.assertTrue(result)
        self.assertEquals([(2006,2006),(2008,2011),(2014,2015)], years)

        years = base_years[:]
        result = insert_year(2012, years)
        self.assertTrue(result)
        self.assertEquals([(2006,2006),(2009,2012),(2014,2015)], years)

        years = base_years[:]
        result = insert_year(2013, years)
        self.assertTrue(result)
        self.assertEquals([(2006,2006),(2009,2011),(2013,2015)], years)

        years = base_years[:]
        result = insert_year(2016, years)
        self.assertTrue(result)
        self.assertEquals([(2006,2006),(2009,2011),(2014,2016)], years)


class TestCopyrightedFile(unittest.TestCase):

    def setUp(self):
        self.this_year = 2016
        self.last_year = self.this_year - 1
        self.copyright_name = "Foo Corp, Inc."
        self.u = UpdateCopyright(self.copyright_name, self.this_year)
        self.cf = CopyrightedFile(None, self.u._commented_pat, self.this_year)

    def testNoMatch(self):
        m, copyrights = self.cf._match_line("# Copyright 2014 Someone Else")
        self.assertIsNone(m)

    def testSimpleCases(self):
        m, copyrights = self.cf._match_line(" # Copyright: 2014 Foo Corp, Inc.")
        self.assertIsNotNone(m)
        self.assertEquals([(2014, 2014), ], copyrights)

        m, copyrights = self.cf._match_line(" # Copyright: (c) 2014 Foo Corp, Inc.")
        self.assertIsNotNone(m)
        self.assertEquals([(2014, 2014), ], copyrights)

        m, copyrights = self.cf._match_line(" # (c) Copyright: 2014 Foo Corp, Inc.")
        self.assertIsNotNone(m)
        self.assertEquals([(2014, 2014), ], copyrights)

        m, copyrights = self.cf._match_line(" # © Copyright: 2014 Foo Corp, Inc.")
        self.assertIsNotNone(m)
        self.assertEquals([(2014, 2014), ], copyrights)

    def testCommaLists(self):
        m, copyrights = self.cf._match_line("# Copyright © 2010,2012,2014 Foo Corp, Inc.")
        self.assertIsNotNone(m)
        self.assertEquals([(2010, 2010), (2012, 2012), (2014, 2014), ], copyrights)

        m, copyrights = self.cf._match_line(" # Copyright: 2014, 2016 Foo Corp, Inc.")
        self.assertIsNotNone(m)
        self.assertEquals([(2014, 2014), (2016, 2016), ], copyrights)

    def testComplexDates(self):
        m, copyrights = self.cf._match_line(" # Copyright: 2013,2015-2017 Foo Corp, Inc.")
        self.assertIsNotNone(m)
        self.assertEquals([(2013, 2013), (2015, 2017), ], copyrights)

        m, copyrights = self.cf._match_line(" # Copyright: 2010-2014, 2016 Foo Corp, Inc.")
        self.assertIsNotNone(m)
        self.assertEquals([(2010, 2014), (2016, 2016), ], copyrights)

        m, copyrights = self.cf._match_line(" # Copyright: 2005 - 2010, 2013, 2015 - 2017 Foo Corp, Inc.")
        self.assertIsNotNone(m)
        self.assertEquals([(2005, 2010), (2013, 2013), (2015, 2017), ], copyrights)

    def testProcessLineNoMatch(self):
        self.assertIsNone(self.cf._process_line("# Foo"))

    def testPrcoessLineThisYear(self):
        result = self.cf._process_line("# Copyright {} {}".format(self.this_year, self.copyright_name))
        self.assertIs("", result)

    def testProcessGood(self):
        initial = """
# Copyright {} {}

print "monkey"
""".format(self.last_year, self.copyright_name)

        expected = """
# Copyright {}-{} {}

print "monkey"
""".format(self.last_year, self.this_year, self.copyright_name)

        self.cf._fp = six.StringIO(initial)

        self.cf.process("dummy")
        self.assertTrue(self.cf._needs_updating)
        self.assertEquals(expected, self.cf._lines)

        # Ensure dry run works
        with patch_open() as fake_open:
            self.cf.update("dummy", dry_run=True)
            self.assertFalse(fake_open.called)

        with patch_open() as fake_open:
            self.cf.update("dummy")
            self.assertTrue(fake_open.called)

    def testProcessNoChange(self):
        initial = """
# Copyright {} {}

print "monkey"
""".format(self.this_year, self.copyright_name)

        self.cf._fp = six.StringIO(initial)

        self.cf.process("dummy")
        self.assertFalse(self.cf._needs_updating)
        self.assertEquals([], self.cf._lines)

    def testProcessNoMatch(self):
        initial = """
# BSD Copyright {} Some one

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
"""
        self.cf._fp = six.StringIO(initial.format(self.last_year))

        self.cf.process("dummy")
        self.assertFalse(self.cf._needs_updating)
        self.assertEquals([], self.cf._lines)

        with patch_open() as fake_open:
            self.cf.update("dummy")
            self.assertFalse(fake_open.called)

    def testUncommented(self):
        # note the pattern used
        cf2 = CopyrightedFile(None, self.u._pat, self.this_year)

        m, copyrights = cf2._match_line(" Copyright 2015 {}".format(self.copyright_name))
        self.assertIsNotNone(m)
        self.assertEquals([(2015, 2015)], copyrights)
