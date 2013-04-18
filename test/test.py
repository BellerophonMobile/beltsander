#!/usr/bin/env python3

import unittest

import beltsander

class Test(beltsander.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_0(self):
        ''''Should say "Hello World!"

        (this test should pass)
        '''

        cmd = self.execute('echo "Hello World"')
        self.assertEqual(cmd.retval, 0)
        self.assertIn('Hello', cmd.stdout)

    @unittest.expectedFailure
    def test_1(self):
        '''Should not say "Hello World!"

        (this test should fail, and therefore if it fails it passes)
        '''

        cmd = self.execute('echo "Hello World"')
        self.assertNotIn('Hello', cmd.stdout)

    def test_2(self):
        '''Should say "Hello World!"

        (this test should pass)
        '''

        cmd = self.execute('cat', stdin='Hello World!')
        self.assertIn('Hello', cmd.stdout)

    @unittest.expectedFailure
    def test_3(self):
        '''Should say "Hello World!"

        (this test should fail and therefore pass)
        '''

        cmd = self.execute('cat', stdin='Hello World!')
        self.assertIn('Mushi', cmd.stdout)
        self.assertNotIn('Hello', cmd.stdout)

if __name__ == '__main__':
    unittest.main()
