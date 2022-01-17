from sys import path
from os.path import realpath
path.insert(0, realpath(f"{__file__}/../../"))

import unittest
from lib.general import Switch, default, Call

class MainTest(unittest.TestCase):
    def setUp(self):
        self.n = Switch({
            'this': Call(print, 'hello, world!'),
            'unthised': 'hello, world!',
            default: lambda: print('hello, world!')
        })
    def test_switch_default(self):
        self.n.do()
    
    def test_switch_remaining(self):
        self.n.do('this')
        self.n.do('unthised')
    
    @unittest.expectedFailure
    def test_switch_not_found(self):
        self.n.do('bar')

if __name__ == '__main__':
    unittest.main()
