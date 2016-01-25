import unittest

from update_copyright_year import copyright_years, string_from_copyrights
from update_copyright_year import should_skip


class TestCopyrightYears(unittest.TestCase):

    def testYears(self):
        result = copyright_years("2015")
        self.assertEquals([(2015, 2015), ], result)

        result = copyright_years("2015,2017")
        self.assertEquals([(2015, 2015), (2017, 2017), ], result)

        result = copyright_years("2015-2017")
        self.assertEquals([(2015, 2017), ], result)

        result = copyright_years("2012 - 2015, 2017")
        self.assertEquals([(2012, 2015), (2017, 2017), ], result)

        result = copyright_years("2010-15")
        self.assertEquals([(2010, 2015), ], result)

        result = copyright_years("10-12")
        self.assertEquals([(2010, 2012), ], result)

        result = copyright_years("1994-1996,98")
        self.assertEquals([(1994, 1996), (1998, 1998)], result)

        result = copyright_years("2010-12,14")
        self.assertEquals([(2010, 2012), (2014, 2014), ], result)


class TestStringFromCopyrights(unittest.TestCase):

    def testStrings(self):
        self.assertEquals("2015", string_from_copyrights([(2015, 2015), ]))

        self.assertEquals("2015,2017", string_from_copyrights([(2015, 2015), (2017, 2017), ]))

        self.assertEquals("2015-2017", string_from_copyrights([(2015, 2017), ]))

        self.assertEquals("2012-2015,2017", string_from_copyrights([(2012, 2015), (2017, 2017), ]))


class TestShouldSkip(unittest.TestCase):

    def testYes(self):
        self.assertTrue(should_skip(["*"], "foo"))
        self.assertTrue(should_skip(["*.md"], "foo.md"))
        self.assertTrue(should_skip(["README"], "README"))
