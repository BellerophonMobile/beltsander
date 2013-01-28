#!/usr/bin/env python3

########################################################################
# Copyright (c) 2013 Joe Kopena <tjkopena@gmail.com>
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

import sys
import os.path
import xml.etree.ElementTree as ET
from subprocess import Popen, PIPE, STDOUT

def error(*args, **kwargs):
    'Simpler print to stderr.'
    if 'file' not in kwargs:
        kwargs['file'] = sys.stderr
    print('ERROR:', *args, **kwargs)

def main(argv):
    if len(argv) == 0:
        error('Must provide test script filename.')
        return 1

    testScript = sys.argv[1]

    if not os.path.isfile(testScript):
        error('Test script {} does not exist.'.format(testScript))
        return 1

    try:
        tree = ET.parse(testScript)
        root = tree.getroot()
    except ET.ParseError as e:
        error('Parse error on script {}: {}'.format(testScript, e))
        return 1

    title = root.find('title')
    if title is None:
        title = '<unknown>'
    else:
        title = title.text

    author = root.find('author')
    if author is None:
        author = '<unknown>'
    else:
        author = author.text

    print('beltsander executing {}: {} - {}'.format(testScript, title, author))

    someFailures = False
    for count, test in enumerate(root.findall('test'), start=1):
        passed = True
        expected = True

        print('\n########################################################################')
        test_id = test.get('id')
        if test_id is None:
            test_id = '<unknown>'
        print('Test {}: {}'.format(count, test_id))

        description = test.find('description')
        if description != None:
            description = description.text
            print('Description:', description)

        exp = test.get('expected')
        if exp == 'pass' or exp is None:
            expected = True # The default...
        elif exp == 'fail':
            expected = False
        else:
            error('Unknown expectation', exp)
            return 1

        command = test.find('command')
        if command is None:
            error('ERROR: Test {} [{}] has no command!'.format(test_id, count))
            return 1
        command = command.text

        print('Commmand:\n ', command)

        # Command is intentionally run without checking to see if there
        # actually are any accept/fail conditions, so you can cheat and
        # have a dummy test to do any setup or teardown.  - tjkopena

        output=[]
        print('Output:')
        p = Popen([command], shell=True, stdout=PIPE)

        for line in p.stdout:
            line = str(line, 'utf-8')
            if line == '' or p.poll() is not None:
                break
            print(line, end='')
            output.append(line)

        output = ''.join(output)

        print('Return code:', p.returncode)

        # Eventually there should be a map from tags to condition
        # functions.  The acceptance and failure batteries will just run
        # through the child notes and apply the appropriate function,
        # negating the result for the failure battery.  For
        # now... Hardcode!  - tjkopena

        #-- Run through battery of acceptance conditions
        accept = test.find('accept')
        if accept is not None:
            for condition in accept:
                if condition.tag == 'returncode':
                    if p.returncode != int(condition.text):
                        print('FAILED: Return code {} != {}'.format(
                            condition.text, p.returncode))
                        passed = False
                elif condition.tag == 'contains':
                    if not condition.text in output:
                        print('FAILED: Output does not contain \"{}\"'.format(
                            condition.text))
                        passed = False
                else:
                    error('Unknown accept condition:', condition.tag)
                    return 1

        #-- Run through battery of failure conditions
        fail = test.find('fail')
        if fail is not None:
            for condition in fail:
                if condition.tag == 'returncode':
                    if p.returncode == int(condition.text):
                        print('FAILED: Return code {} == {}'.format(
                            condition.text, p.returncode))
                        passed = False
                elif condition.tag == 'contains':
                    if condition.text in output:
                        print('FAILED: Output contains \"{}\"'.format(
                            condition.text))
                        passed = False
                else:
                    error('Unknown accept condition:', condition.tag)
                    return 1

        if passed == expected:
            print('Status: PASSED')
        else:
            print('Status: FAILED')
            someFailures = True

    print('\n########################################################################')
    if someFailures:
        print('Some tests failed.')
        return 1
    else:
        print('All tests passed.')
        return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
