#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

# This file is part of Addison Arches.
#
# Addison Arches is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Addison Arches is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Addison Arches.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import cmd
from collections import Counter
from collections import deque
from collections import namedtuple
import concurrent.futures
import datetime
from enum import Enum
import itertools
import sys

import unittest

__doc__ = """
Commodity items in their millions (eg: shells): named tuples
Combine commodities to make objects (eg: shells + string -> wampum): classes
Modify objects by mixing (eg: wampum + shape -> belt)
Innovate objects by subclassing (eg: belt + speech -> influence) Influence is a commodity!
Break down objects to commodities again.

"""

class Length(Enum):
    metre = 1

class Pellets(Enum):
    one = 1
    handful = 12
    pouch = 64
    bag = 4800
    sack = 144000
 
Glyph = namedtuple("Glyph", ["name"])
Shell = namedtuple("Shell", ["colour"])
String = namedtuple("String", ["length"])

class Promise:
    pass

class Makeable:

    @staticmethod
    def recipe():
        raise NotImplementedError

    @classmethod
    def requirements(class_):
        for k, v in class_.recipe().items():
            try:
                yield from k.requirements()
            except AttributeError:
                yield (k, getattr(v, "value", v))
        
    @classmethod
    def build(class_, bits:list):
        """Kwargs contain ingredients from recipe"""
        recipe = Counter(
            {k: getattr(v, "value", v) for k, v in class_.recipe().items()}
        )
        bits.subtract(recipe)
        return class_()

    def breakUp(self, bits=None):
        bits = {} if bits is None else bits
        bits.update(super().breakUp())
        return bits

Memory = deque

class Wampum(Makeable):

    @staticmethod
    def recipe():
        return {Shell: Pellets.pouch, String: Length.metre}

class Belt(Makeable, Memory):

    @staticmethod
    def recipe():
        return {Wampum: Length.metre, Glyph: 1}

class BeltTests(unittest.TestCase):

    def test_recipe(self):
        recipe = Counter(dict(Belt.recipe()))
        self.assertIn(Glyph, recipe)
        self.assertNotIn(Shell, recipe)
        self.assertNotIn(String, recipe)
        self.assertIn(Wampum, recipe)

    def test_requirements(self):
        req = Counter(dict(Belt.requirements()))
        self.assertIn(Glyph, req)
        self.assertIn(Shell, req)
        self.assertIn(String, req)
        self.assertNotIn(Wampum, req)

    def test_build(self):
        bits = {k: getattr(v, "value", v) for k, v in Belt.recipe().items()}
        belt = Belt.build(Counter(bits).elements())
        self.assertIsInstance(belt, Belt)
