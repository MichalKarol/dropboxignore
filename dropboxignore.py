#!/usr/bin/env python

# dropboxignore - python script for automated ignoring paths by Dropbox
# Copyright (c) 20019-2019 Michał Karol <michal.p.karol@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
dropboxignore

@author: Michał Karol
@license: MIT License
@contact: michal.p.karol@gmail.com
"""

from collections import defaultdict
from typing import List, Pattern, NamedTuple

import os
import os.path as p
import pyinotify
import re
import subprocess
import sys


class RETURN_CODES(object):
    WRONG_NUMBER_OF_ARGS = 1
    PATH_IS_NOT_DIRECTORY = 2
    DROPBOXIGNORE_DOES_NOT_EXISTS = 3
    CANNOT_READ_DROPBOXIGNORE = 4
    CANNOT_WATCH_PATH = 5
    PARSING_ERROR = 6
    SCANNING_ERROR = 7


class ParsingException(Exception):
    pass


class Tree(defaultdict):
    def __init__(self, ignored=False):
        super(Tree, self).__init__(Tree)
        self.ignored = ignored


class IgnoreTree(object):
    def __init__(self, dropbox_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dropbox_path = dropbox_path
        self.tree = Tree()

    def add_ignored(self, path):
        path_elements = path.split(p.sep)
        current_node = self.tree
        for path_element in path_elements:
            # Key exists
            if path_element in current_node:
                if current_node[path_element].ignored:
                    # Already ignored
                    return
            current_node = current_node[path_element]
        current_node.ignored = True
        subprocess.call(f'dropbox exclude add {self.dropbox_path}{p.sep}{path}', shell=True)


# Typedefing
Rules = NamedTuple('Rules', [('ignored', List[Pattern[str]]), ('excluded', List[Pattern[str]])])


def parse_dropboxignore(dropboxignore: List[str]) -> Rules:
    rules: Rules = Rules([], [])

    # Otherwise, Git treats the pattern as a shell glob: "*" matches anything except "/", "?" matches any one
    # character except "/" and "[]" matches one character in a selected range.
    def prepare_regex(split: str) -> str:
        split = re.sub(r'([\.\+])', r'\\\1', split)  # Escape
        split = re.sub(r'\[!(.*?)\]', r'[^\1]', split)  # Escape
        split = re.sub(r'([^\\\*]|^)\*([^\*]|$)', r'\1([^\/]*)\2', split)  # Single star
        split = re.sub(r'([^\\]|^)\?', r'\1([^\/])', split)  # Question mark
        split = re.sub(r'\*\*', r'(.*)', split)  # Double star
        return rf'{split}(\/|$)'

    for line in dropboxignore:
        line = line.lstrip()
        regex = []
        exclude = False

        # A blank line matches no files, so it can serve as a separator for readability.
        if not line:
            continue

        # A line starting with # serves as a comment. Put a backslash ("\") in front of the first
        #   hash for patterns that begin with a hash.
        if line.startswith('#'):
            continue

        if line.startswith('\\#'):
            line = f'#{line[2:]}'

        # Trailing spaces are ignored unless they are quoted with backslash ("\").
        line = re.sub(r'(\w[^\\])(\s+)', r'\1', line, flags=re.MULTILINE)

        # An optional prefix "!" which negates the pattern; any matching file excluded by a previous pattern will become
        # included again. It is not possible to re-include a file if a parent directory of that file is excluded. Git
        # doesn’t list excluded directories for performance reasons, so any patterns on contained files have no effect,
        # no matter where they are defined. Put a backslash ("\") in front of the first "!" for patterns that begin with
        # a literal "!", for example, "\!important!.txt".

        if line.startswith('!'):
            line = line[1:]
            exclude = True

        if line.startswith('\\!'):
            line = f'!{line[2:]}'

        if line.startswith('**/'):
            line = line[3:]

        if line.endswith('/**'):
            line = line[:-3]

        # Two consecutive asterisks ("**") in patterns matched against full pathname may have special meaning:
        # A leading "**" followed by a slash means match in all directories. For example, "**/foo" matches file
        # or directory "foo" anywhere, the same as pattern "foo". "**/foo/bar" matches file or directory "bar"
        # anywhere that is directly under directory "foo".
        # A trailing "/**" matches everything inside. For example, "abc/**" matches all files inside directory "abc",
        #  relative to the location of the .gitignore file, with infinite depth.
        # A slash followed by two consecutive asterisks then a slash matches zero or more directories. For example,
        #  "a/**/b" matches "a/b", "a/x/b", "a/x/y/b" and so on.
        # Other consecutive asterisks are considered regular asterisks and will match according to the previous rules.
        line = re.sub(r'\/\*\*\/', '**', line)

        if '/' in line and not line.endswith('/'):
            # A leading slash matches the beginning of the pathname. For example, "/*.c" matches "cat-file.c"
            # but not "mozilla-sha1/sha1.c".
            regex.append(r'^')
            regex.append(r'\/'.join([prepare_regex(split) for split in line[1:].split('/')]))
            regex.append(r'(.*)')
        else:
            # If the pattern does not contain a slash /, Git treats it as a shell glob pattern and checks for a match
            # against the pathname relative to the location of the .gitignore file (relative to the toplevel of the work
            # tree if not from a .gitignore file).
            regex.append(r'(^|(.*)\/)')
            regex.append(r'\/'.join([prepare_regex(split) for split in line.split('/')]))
            regex.append(r'(.*)')

        getattr(rules, 'ignored' if not exclude else 'excluded').append(re.compile(r''.join(regex)))

    return rules


def test_if_ignored(path, rules):
    for rule in rules.ignored:
        if rule.match(path):
            for erule in rules.excluded:
                if erule.match(path):
                    return False
            return True
    return False


def build_initial_tree(dropbox_path: str, rules: Rules) -> IgnoreTree:
    """Build initial ignore tree, therefore allowing for ignoring paths by not yet applied rules
       and reducing needed calls when eg. created file is already in ignored path

    :param dropbox_path: path synchronized by dropbox
    :type dropbox_path: str
    :param rules: list of rules
    :type rules: List[str]
    :return: tree of ignored paths
    :rtype: [type]
    """
    ignore_tree = IgnoreTree(dropbox_path)

    def iterate_over_path(path):
        for subpath_entry in os.scandir(path):
            subpath = subpath_entry.path
            if not subpath_entry.is_dir():
                continue

            subrelpath = p.relpath(p.normpath(subpath), dropbox_path)
            if test_if_ignored(subrelpath, rules):
                ignore_tree.add_ignored(subrelpath)
            else:
                iterate_over_path(subpath)

    iterate_over_path(dropbox_path)
    return ignore_tree


class EventHandler(pyinotify.ProcessEvent):
    """Class with implementation of method checking ignored paths"""

    def __init__(self, dropbox_path: str, rules: Rules, ignore_tree: IgnoreTree, pevent=None, **kargs):
        self.dropbox_path = dropbox_path
        self.rules = rules
        self.ignore_tree = ignore_tree
        return super().__init__(pevent=pevent, **kargs)

    def process_default(self, event: pyinotify.Event):
        """Event handler checking if event path is ignored and synced by Dropbox

        :param self: Object of event handler
        :type self: EventHandler
        :param event: Object of raised event
        :type event: pyinotify.Event
        """
        relative_path = p.relpath(p.normpath(event.pathname), self.dropbox_path)

        # Test if ignored
        if test_if_ignored(relative_path, self.rules):
            self.ignore_tree.add_ignored(relative_path)


def main() -> None:
    if len(sys.argv) != 2:
        print('Wrong number of arguments')
        sys.exit(RETURN_CODES.WRONG_NUMBER_OF_ARGS)
    dropbox_path = sys.argv[1]

    # Check if dropbox path is a directory
    if not p.isdir(dropbox_path):
        print('Dropbox path is not a directory.')
        sys.exit(RETURN_CODES.PATH_IS_NOT_DIRECTORY)

    # Check for .dropboxignore file
    dropbox_ignore_file = p.join(dropbox_path, '.dropboxignore')
    if not p.exists(dropbox_ignore_file):
        print('.dropboxignore does not exists')
        sys.exit(RETURN_CODES.DROPBOXIGNORE_DOES_NOT_EXISTS)

    try:
        opened_file = open(dropbox_ignore_file, 'r')
        lines = opened_file.readlines()
    except Exception as err:
        print(f'Cannot open .dropboxignore in path: {err}')
        sys.exit(RETURN_CODES.CANNOT_READ_DROPBOXIGNORE)

    # Parse rules
    try:
        rules = parse_dropboxignore(lines)
    except ParsingException as err:
        print(f'Parsing error of .dropboxignore: {err}')
        sys.exit(RETURN_CODES.PARSING_ERROR)

    # Initial scan of directory and building ignore tree
    try:
        pass
        ignore_tree = build_initial_tree(dropbox_path, rules)
    except Exception as err:
        print(f'Exception during scanning path: {err}')
        sys.exit(RETURN_CODES.SCANNING_ERROR)

    # Watch directory
    events = pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO | pyinotify.IN_MOVED_FROM
    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm, EventHandler(dropbox_path, rules, ignore_tree))
    wm.add_watch(dropbox_path, events, rec=True)

    try:
        print('Watching path')
        notifier.loop()
    except pyinotify.NotifierError as err:
        print(f'Cannot watch path: {err}')
        sys.exit(RETURN_CODES.CANNOT_WATCH_PATH)


if __name__ == "__main__":
    main()
