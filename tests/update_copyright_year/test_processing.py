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
        # import pdb; pdb.set_trace()

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

    def testProcessLineYearsInThePast(self):
        year = self.this_year - 3
        self.cf._year = year
        result = self.cf._process_line("# Copyright {} {}".format(self.this_year, self.copyright_name))
        self.assertEquals("# Copyright {},{} {}".format(year, self.this_year, self.copyright_name),
                          result)

    def testProcessLineOneYearInThePast(self):
        self.cf._year = self.last_year
        result = self.cf._process_line("# Copyright {} {}".format(self.this_year, self.copyright_name))
        self.assertEquals("# Copyright {}-{} {}".format(self.last_year, self.this_year, self.copyright_name),
                          result)

    def testProcessLineYearsInThePastComplex(self):
        self.cf._year = 2013
        result = self.cf._process_line("# Copyright 2012,2016 {}".format(self.copyright_name))
        self.assertEquals("# Copyright 2012-2013,2016 {}".format(self.copyright_name),
                          result)

        self.cf._year = 2002
        result = self.cf._process_line("# Copyright 2004,2007,2010-2015 {}".format(self.copyright_name))
        self.assertEquals("# Copyright 2002,2004,2007,2010-2015 {}".format(self.copyright_name),
                          result)

        self.cf._year = 2003
        result = self.cf._process_line("# Copyright 2004,2007,2010-2015 {}".format(self.copyright_name))
        self.assertEquals("# Copyright 2003-2004,2007,2010-2015 {}".format(self.copyright_name),
                          result)

        self.cf._year = 2005
        result = self.cf._process_line("# Copyright 2004,2007,2010-2015 {}".format(self.copyright_name))
        self.assertEquals("# Copyright 2004-2005,2007,2010-2015 {}".format(self.copyright_name),
                          result)

        self.cf._year = 2006
        result = self.cf._process_line("# Copyright 2004,2007,2010-2015 {}".format(self.copyright_name))
        self.assertEquals("# Copyright 2004,2006-2007,2010-2015 {}".format(self.copyright_name),
                          result)

        self.cf._year = 2008
        result = self.cf._process_line("# Copyright 2004,2007,2010-2015 {}".format(self.copyright_name))
        self.assertEquals("# Copyright 2004,2007-2008,2010-2015 {}".format(self.copyright_name),
                          result)

        self.cf._year = 2008
        result = self.cf._process_line("# Copyright 2004,2006,2010-2015 {}".format(self.copyright_name))
        self.assertEquals("# Copyright 2004,2006,2008,2010-2015 {}".format(self.copyright_name),
                          result)

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
