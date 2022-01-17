"""RPGStatus - Status Test"""

from io import StringIO
from sys import path
from os.path import realpath
path.insert(0, realpath(f"{__file__}/../../"))

from status import BaseCharacter, Attribute, CharAttribute, setDebug
import unittest
from pprint import pprint

# We don't really need other classes like Attribute, etc. -- because 'they' was handled by BaseCharacter.
# What i mean is Attribute checking, etc. The '_is_valid_*' function should do the tricks,
# Advance classes like Item, Magic, Skill, etc. will be added to test_status_advance.py
# This file should contain basic stuff.

# On Frozen* classes, they'll go into other class. They could be skipped in BaseCharacter so...
# I want them also be tested as well... or not?

class TestCharacter(unittest.TestCase):
    def setUp(self):
        setDebug(True)
        self.attribute = Attribute([10]*13)
        self.char_attribute = CharAttribute(1, 0, 0, 1, 1, 1, "Debug #0", "DebugRace", 0, {"Debug": "debug"}, -1)
        self.base_char_init = [1, 0, 0, 1, 1, 1, "NAME", "DebugRace", 0, {"Debug": "debug"}, -1]
        self.main = BaseCharacter(self.char_attribute, self.attribute)
        self.output = StringIO()

    # TODO: There should be a function that generates new characters with different attributes then dumped into JSON file, containing all the characters.
    # Nice, isn't it?

    @unittest.expectedFailure
    def test_invalid_attributes(self):
        f_attr = Attribute(['foo']*13)
        f_ch_attr = CharAttribute(-1, 0, 0, -1, -1, -1, 3, 0, 0, "", -2)
        instance = BaseCharacter(f_ch_attr, f_attr)
        del instance, f_attr, f_ch_attr
    
    def test_generate_new(self):
        self.output.write("Generating up-to 100 characters with unique 100 Attribute classes...\n")
        for i in range(0, 100):
            # Up to 100 Attribute instances are different, but only CharAttribute that's different (unless Name.)
            n_attr = Attribute([i]*13)
            n_attr1 = self.base_char_init.copy()
            n_attr1.remove("NAME")
            n_attr1.insert(6, f"Debug #{i}")
            a1 = CharAttribute(**n_attr1)
            obj = BaseCharacter(a1, n_attr)
            json_string = pprint(obj.dump_to_jsonable())
            self.output.write(f"{'='*30}\n\n{n_attr[6]}\n\n")
            pprint(json_string, self.output, 2, sort_dicts=False)
            self.output.write("\n\n{'='*30}\n\n")
    
