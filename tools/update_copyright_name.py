#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from fnmatch import fnmatch
import re


class CopyrightedFile(object):

    def __init__(self, fp, pattern, old, new, verbose=False):
        self._fp = fp
        self._pattern = pattern
        self._new_copyright = new
        self._old_copyright = old
        self._verbose = verbose
        self._needs_updating = False
        self._lines = []

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

            # Match with a pattern to be properly cautious. Once detected the text can be safely replaced.
            m = self._pattern.match(line)
            if m:
                new = line.replace(self._old_copyright, self._new_copyright)
                self._lines.append(new)
                self._needs_updating = True
                break
            else:
                self._lines.append(line)

        if self._needs_updating:
            # only read the whole file if necessary
            self._lines = ''.join(self._lines)
            self._lines += self._fp.read()
        else:
            self._lines = []

        self._fp.close()

    def update(self, filename, dry_run=False):
        if self._needs_updating:
            print("{} {}...".format("Dry run" if dry_run else "Writing", filename))
            if not dry_run:
                with open(filename, "w") as fp:
                    fp.write(self._lines)
        else:
            print("No-op")


def should_skip(glob_list, filename):
    return any(fnmatch(filename, glob) for glob in glob_list)


class UpdateCopyright(object):
    """Process files to remove 'company' from the copright"""

    _commented_copyright_regex = r"""
        ^
        \s*
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
        {OLD_COPYRIGHT_NAME} # Name to be replaced
        \s*$
    """  # noqa

    _copyright_regex = r"""
        ^
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
        {OLD_COPYRIGHT_NAME}     # Copyright holder's name
        \s*$
    """  # noqa

    def __init__(self, old_copyright_name, new_copyright_name):
        self._old_name = old_copyright_name
        self._new_name = new_copyright_name

        self._pat = re.compile(self._copyright_regex.format(OLD_COPYRIGHT_NAME=re.escape(old_copyright_name)),
                               re.VERBOSE | re.IGNORECASE)
        self._commented_pat = re.compile(self._commented_copyright_regex.format(OLD_COPYRIGHT_NAME=re.escape(old_copyright_name)),  # noqa
                                         re.VERBOSE | re.IGNORECASE)

    def run(self, files, skip_comment_check_for=[], dry_run=False, verbose=False):
        for filename in files:
            pat = None
            if should_skip(skip_comment_check_for, filename):
                pat = self._pat
            else:
                pat = self._commented_pat

            item = CopyrightedFile(open(filename), pat, self._old_name, self._new_name, verbose=verbose)
            item.process(filename)
            item.update(filename, dry_run=dry_run)


def main(args=None):
    import argparse
    import sys

    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Tool to remove 'company' from copyrights")
    parser.add_argument("--old-copyright")
    parser.add_argument("--new-copyright")
    parser.add_argument("--skip-comment-check-for", type=str, action="append", default=[],
                        help="Takes a standard shell glob such as '*.md'. Remember to use single quotes around the glob so the shell does not consume them. Can be repeated as needed.")  # noqa
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    tool = UpdateCopyright(args.old_copyright, args.new_copyright)
    tool.run(args.files, skip_comment_check_for=args.skip_comment_check_for,
             dry_run=args.dry_run, verbose=args.verbose)


if __name__ == '__main__':
    main()
