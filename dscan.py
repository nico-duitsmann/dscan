#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
dscan - Command line utility to search data for matching patterns
Licensed under the GNU General Public License Version 3
(c) Copyright 2018 Nico Duitsmann. All rights reserved.

Usage:
    dscan [options] <pattern> [<input_data>...]

Arguments:
    pattern                   The searched pattern.
    input_data                The input data can be a file, directory or url
    
Options:
    -r --regex                Use a regular expression as pattern
    -f --follow-sym           Follow sym links
    -i --ignore-case          Ignore case sensitive
    -p --passing              Passing errors
    -N --no-color             No colored ouput
    -V --verbose              Verbose print
    -h --help                 Show this help and exit
    -v --version              Show version and exit

dscan 0.1 - https://github.com/nico-duitsmann/dscan
Run dscan as superuser or admin on permission errors.
"""

__version__ = "dscan 0.1"
__author__  = "Nico Duitsmann"
__github__  = "https://github.com/nico-duitsmann/dscan"
__license__ = "GNU GPL v3"

import os
import re
import select
import sys
import time
from os import scandir

from docopt import docopt
from termcolor import colored

RED = "\033[1m\033[91m" if not sys.platform.startswith("win") else ""
END = "\033[0m"  if not sys.platform.startswith("win") else ""


class Core(object):
    """dscan core.
    :param args:
    :param pipe_stream:
    """
    def __init__(self, args, pipe_stream=None):
        self.piped_data = pipe_stream
        self.args = docopt(args, version=__version__)

        self.input_data = self.args["<input_data>"]
        self.pattern = self.args["<pattern>"]

        self.search_regex = self.args["--regex"]
        self.follow_symlinks = self.args["--follow-sym"]
        self.ignore_case = self.args["--ignore-case"]
        self.passing_errors = self.args["--passing"]
        self.no_color = self.args["--no-color"]
        self.verbose = self.args["--verbose"]
        
        self._num_files = 0

        self.dscan_init()

    def cput(self, message, color, no_color=False):
        """Custom output method for colored ouput.
        :param message:
        :param color:
        """
        if not no_color:
            return colored(str(message), color, attrs=['bold'])
        else:
            return str(message)

    def regex_search(self, pattern, file):
        """Perform regex matching pattern search.
        :param pattern:
        :param file:
        """
        try:
            for i, line in enumerate(open(file, errors="replace", encoding="utf-8")):
                for match in re.finditer(pattern, line):
                    print("\nFound '%s' in %s on line %s" % (
                        self.cput(match.groups(0), "red"), file, i + 1))
                    print("%s\n%d: %s"% (file, i + 1, self.cput(match.groups(0), "red")))
        except Exception as e:
            if not self.passing_errors:
                sys.exit(self.cput("ERR ", "red") + str(e))

    def file_search(self, pattern, file):
        """Scan file for matching patterns or regular expressions
        :param filename
        """
        if not self.search_regex:
            try:
                for num, line in enumerate(open(file, errors="replace", encoding="utf-8"), 1):
                    if self.ignore_case: line = line.lower()
                    if str(pattern) in line:
                        print("%s\n%d: %s"% (file, num, line.replace(pattern, RED + pattern + END)))
            except (IOError, OSError, PermissionError) as e:
                if not self.passing_errors:
                    sys.exit(self.cput("ERR ", "red") + str(e))
        else:
            self.regex_search(self.pattern, file)

    def scan_tree(self, path):
        """Recursively yield DirEntry objects for given directory.
        :param path:
        """
        for entry in scandir(path):
            if entry.is_dir(follow_symlinks=bool(self.follow_symlinks)):
                yield from self.scan_tree(entry.path)
            else:
                yield entry

    def dir_search(self, dir):
        """Scan directory for files
        :param dir:
        """
        for entry in self.scan_tree(dir):
            self._num_files += 1
            if self.verbose:
                print("Processing " + self.cput(entry.path, "red") + " "*int(len(entry.path)), end="\r", flush=True)
            if self.search_regex:
                pattern = re.compile(r'%s' % self.pattern)
                self.regex_search(pattern, entry.path)
            else:
                self.file_search(self.pattern, entry.path)

    def process_data(self, input_data):
        """data processing.
        :param input_data:
        """
        # check if input data is a dir
        if os.path.isdir(input_data): self.dir_search(input_data)
        # check if input data is a file
        if os.path.isfile(input_data): self.file_search(self.pattern, input_data)
        # data is piped
        if not os.path.isdir(input_data) and \
            not os.path.isfile(input_data):
                if self.ignore_case: input_data = input_data.lower()
                if self.pattern in input_data:
                    print("Found match: " +
                          input_data.replace(self.pattern,
                                             RED + self.pattern + END).replace("\n", ""))

    def dscan_init(self):
        """Initialize dscan.
        """
        start = time.time()
        # override input_data if core was initialized with piped data
        if self.piped_data is not None:
            self.process_data(self.piped_data)
        else:
            if len(self.input_data) < 1:
                self.process_data(os.getcwd())
            else:
                for data in self.input_data:
                    self.process_data(data)
        end = time.time()
        sys.exit("\nElapsed time: %s for %d files (~%dms per file)" % (str(end-start), self._num_files, self._num_files/(end-start)))


def main():
    """dscan main.
    """
    # check if stdin has some data
    if select.select([sys.stdin, ], [], [], 0.0)[0]:
        pipe_stream = ""
        for line in sys.stdin:
            pipe_stream += line
        Core(__doc__, pipe_stream=pipe_stream)
    else:
        Core(__doc__)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        sys.exit(e)
