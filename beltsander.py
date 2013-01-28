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


if len(sys.argv) <= 1:
    sys.exit('ERROR: Must provide test script filename.')

testScript = sys.argv[1]

if not os.path.isfile(testScript):
   sys.exit('ERROR: Test script ' + testScript + ' does not exist.')

try:
    tree = ET.parse(testScript)
    root = tree.getroot()
except ET.ParseError as e:
    sys.exit('ERROR: Parse error on script ' + testScript + ':\n' + str(e))

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

print('beltsander executing ' + testScript + ': ' + title + ' - ' + author)


someFailures = False
count = 0
for test in root.findall('test'):
    count += 1
    passed = True
    expected = True

    print('\n########################################################################')
    id = test.get('id')
        id = '<unknown>'
    print("Test " + str(count) + ":", id)
    if test_id is None:

    description = test.find('description')
    if description != None:
        description = description.text
        print("Description:", description)

    exp = test.get('expected')
    if exp == 'pass' or exp is None:
        expected = True # The default...
    elif exp == 'fail':
        expected = False
    else:
        sys.exit('Unknown expectation ' + exp)

    command = test.find('command')
    if command is None:
        sys.exit('ERROR: Test ' + id + ' [' + str(count) + '] has no command!')
    command = command.text

    print("Command:")
    print(" ", command)

    # Command is intentionally run without checking to see if there
    # actually are any accept/fail conditions, so you can cheat and
    # have a dummy test to do any setup or teardown.  - tjkopena

    p = Popen([command], shell=True, stdout=PIPE, stdin=PIPE)

    commandInput = test.find('input')
    if commandInput is not None:
        commandInput = commandInput.text
    else:
        commandInput = ''

    output = p.communicate(commandInput.encode())[0].decode("utf-8")
    print("Output:")
    print(output)

    # This commented-out code would be better, to print as the process
    # goes.  But closing stdin seems to terminate the process without
    # any output...  - tjkopena

#    commandInput = test.find('input')
#    if commandInput != None:
#        commandInput = commandInput.text
#        print("Input:")
#        print(commandInput)
#        p.stdin.write(commandInput.encode())
#        p.stdin.flush()
#        p.stdin.close()
#
#    output = ''
#    print("Output:")
#    while True:
#        line = p.stdout.readline()
#        if line == '' or p.poll() != None:
#            break
#        print(line.decode("utf-8"), end='')
#        output += line.decode("utf-8")

    print("Return code:", p.returncode)

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
                        print("FAILED: Return code " +
                              condition.text + " != " + str(p.returncode))
                        passed = False
            elif condition.tag == 'contains':
                if not condition.text in output:
                    print("FAILED: Output does not contain '" +
                          condition.text + "'")
                    passed = False
            else:
                sys.exit('Unknown accept condition ' + condition.tag)

    #-- Run through battery of failure conditions
    fail = test.find('fail')
    if fail is not None:
        for condition in fail:
            if condition.tag == 'returncode':
                if p.returncode == int(condition.text):
                        print("FAILED: Return code " +
                              condition.text + " == " + str(p.returncode))
                        passed = False
            elif condition.tag == 'contains':
                if condition.text in output:
                    print("FAILED: Output contains '" +
                          condition.text + "'")
                    passed = False
            else:
                sys.exit('Unknown accept condition ' + condition.tag)

    if passed == expected:
        print("Status: PASSED")
    else:
        print("Status: FAILED")
        someFailures = True


print('\n########################################################################')
if someFailures:
    print("Some tests failed.")
    sys.exit(-1)
else:
    print("All tests passed.")
    sys.exit(0)
