#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from datetime import datetime
import re


def copyright_years(years):
    copyrights = []

    for group in [s.strip() for s in years.split(',')]:
        try:
            start, end = [s.strip() for s in group.split('-')]
        except ValueError:
            start = end = group

        if len(start) == 4:
            if len(end) == 2:
                end = start[0:2] + end
        else:
            if copyrights:
                century = str(copyrights[-1][1])[0:2]
            else:
                century = '20'

            start = century + start
            end = century + end

        copyrights.append((int(start), int(end)))

    return copyrights


def string_from_copyrights(copyrights):
    pieces = []
    for start, end in copyrights:
        if start == end:
            pieces.append(str(start))
        else:
            pieces.append("{}-{}".format(start, end))

    return ",".join(pieces)


class CopyrightedFile(object):
    def __init__(self, fp, pattern, year, verbose=False):
        self._fp = fp
        self._pattern = pattern
        self._year = year
        self._verbose = verbose
        self._needs_updating = False
        self._lines = []

    def _match_line(self, line):
        match = self._pattern.match(line)
        if not match:
            return None, []

        return match, copyright_years(match.group('years'))

    def _process_line(self, line):
        match, copyrights = self._match_line(line)
        if match is None:
            return None

        valid = any(start <= self._year <= end for start, end in copyrights)
        if not valid:
            # update the year trying to follow the existing pattern
            start, end = copyrights[-1]

            if (self._year - 1) == end:
                # change the end of the range. This prevents 2015,2016,2017
                # but allows 2014,2017
                copyrights[-1] = (start, self._year)
            elif self._year < start:
                count = 0

                # Start looking for a spot at the beginning of the list
                for start, end in copyrights:
                    if self._year < start:
                        # Update, place at beginning of range
                        if (self._year + 1) == start:
                            copyrights[count] = (self._year, end)
                        else:
                            # Insert new value separately
                            copyrights.insert(count, (self._year, self._year))
                        break
                    elif (end + 1) == self._year:
                        # Update, place at end of range
                        copyrights[count] = (start, self._year)
                        break

                    count += 1
            else:
                # add another entry
                copyrights.append((self._year, self._year))

            new_copyright_dates = string_from_copyrights(copyrights)

            return line[:match.start(1)] + new_copyright_dates + line[match.end(1):]

        return ""

    def process(self, filename):
        if self._verbose:
            print("Processing: {}".format(filename))

        self.lineno = 1

        # use a while loop and readline to enable calling .read() later.
        # When used in a for loop, a read-ahead buffer is used which would
        # break the call to read() later

        while True:
            if self.lineno > 10:
                if self._verbose:
                    print("No copyright match")
                break

            self.lineno += 1

            line = self._fp.readline()
            if not line:
                break  # EOF

            self._lines.append(line)
            result = self._process_line(line)
            if result is None:
                continue  # no match, keep looking
            elif not result:
                break  # found but already up to date
            else:
                self._lines[-1] = result
                self._needs_updating = True
                break

        if self._needs_updating:
            # only read the whole file if necessary
            self._lines = ''.join(self._lines)
            self._lines += self._fp.read()
        else:
            self._lines = []

        self._fp.close()

    def update(self, filename, dry_run=False):
        if self._needs_updating:
            print("Writing {}...".format(filename))
            if not dry_run:
                with open(filename, "w") as fp:
                    fp.write(self._lines)
        else:
            print("No-op")


class UpdateCopyright(object):
    """Process files to update their copyright dates"""

    _copyright_regex = r"""
        ^\s*
        [#;]+                # Must be in a comment
        \s*
        (?:\(c\)|©)?         # Optional copyright symbol
        \s*
        Copyright:?          # Word 'copyright' with optional colon
        \s+
        (?:\(c\)|©)?         # Other location for optional copyright symbol
        \s*
        # Supports 1995 or 1995-1996 or 1995,1997 or a combination
        (?P<years>(?:[0-9]+(?:\s*-\s*[0-9]+)?\s*,\s*)*(?:[0-9]+(?:\s*-\s*[0-9]+)?))
        \s+
        {COPYRIGHT_NAME}     # Copyright holder's name
        \s*$
    """  # noqa

    def __init__(self, copyright_name, year, dry_run=False, verbose=False):
        self._year = year

        self._dry_run = dry_run
        self._verbose = verbose
        self._pat = re.compile(self._copyright_regex.format(COPYRIGHT_NAME=re.escape(copyright_name)),
                               re.VERBOSE | re.IGNORECASE)

    def run(self, files):
        for filename in files:
            item = CopyrightedFile(open(filename), self._pat, self._year, verbose=self._verbose)
            item.process(filename)
            item.update(filename, dry_run=self._dry_run)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Copyright date update tool")
    parser.add_argument("--copyright-name", type=str, required=True)
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument("--year", type=int)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    if args.year is None:
        year = datetime.now().year
    else:
        year = args.year

    tool = UpdateCopyright(copyright_name=args.copyright_name, year=year,
                           dry_run=args.dry_run, verbose=args.verbose)
    tool.run(args.files)
