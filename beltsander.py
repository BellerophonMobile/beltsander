#!/usr/bin/env python3

########################################################################
# Copyright (c) 2013 Joe Kopena <tjkopena@gmail.com>,
#                    Tom Wambold <tom5760@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
########################################################################

import subprocess
import unittest

class Command:
    def __init__(self, stdout, stderr, rv):
        self.stdout = stdout
        self.stderr = stderr
        self.retval = rv

class TestCase(unittest.TestCase):
    def execute(self, cmd, stdin=None, timeout=None):
        # TODO: Maybe check/sanitize environment variables?
        p = subprocess.Popen([cmd], shell=True,
                universal_newlines=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, stdin=subprocess.PIPE)

        if isinstance(cmd, str):
            stdin = [stdin]

        stdout = []
        stderr = []

        for line in stdin:
            rv = p.communicate(line, timeout)
            stdout.append(rv[0])
            stderr.append(rv[1])

        stdout, stderr = ['\n'.join(x) for x in (stdout, stderr)]

        return Command(stdout, stderr, p.returncode)
