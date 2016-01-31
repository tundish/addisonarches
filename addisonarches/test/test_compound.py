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

from collections import Counter
from collections import namedtuple
from enum import Enum
import itertools
import unittest

from turberfield.ipc.message import dumps
from turberfield.ipc.message import load
from turberfield.ipc.message import type_dict

from addisonarches.compound import Compound
from addisonarches.compound import Memory


class Length(Enum):
    metre = 1

class Pellets(Enum):
    one = 1
    handful = 16
    pouch = 64
    bag = 4800
    sack = 144000
 
Glyph = namedtuple("Glyph", ["name"])
Shell = namedtuple("Shell", ["colour"])
String = namedtuple("String", ["length"])


class Wampum(Compound):

    @staticmethod
    def recipe():
        return {Shell: Pellets.pouch, String: Length.metre}

class Belt(Compound, Memory):

    @staticmethod
    def recipe():
        return {Wampum: Length.metre, Glyph: 1}

class SerialisationTests(unittest.TestCase):

    def test_belt_roundtrip(self):
        inventory = Counter(
            itertools.chain((String(1), Glyph("snake")),
            itertools.repeat(Shell("white"), 64))
        )
        inventory[Wampum.build(inventory)] += 1
        belt = Belt.build(inventory, maxlen=3)
        text = "\n".join(dumps(belt))
        obj = next(load(text), None)
        self.assertEqual(belt, obj)

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

    def test_build_exact(self):
        inventory = Counter(itertools.chain(
            (String(1), ), itertools.repeat(Shell("white"), 64)
        ))
        w = Wampum.build(inventory)
        self.assertIsInstance(w, Wampum)
        self.assertFalse(sum(inventory.values()), inventory)

    def test_build_over(self):
        inventory = Counter(itertools.chain(
            (String(1), ), itertools.repeat(Shell("white"), 65)
        ))
        w = Wampum.build(inventory)
        self.assertIsInstance(w, Wampum)
        self.assertEqual(1, inventory[Shell("white")])
        self.assertEqual(1, sum(inventory.values()))

    def test_build_under(self):
        inventory = Counter(itertools.chain(
            (String(1), ), itertools.repeat(Shell("white"), 63)
        ))
        w = Wampum.build(inventory)
        self.assertIsNone(w)
        self.assertEqual(64, sum(inventory.values()))

    def test_belt_build(self):
        inventory = Counter(itertools.chain(
            (String(1), Glyph("snake")), itertools.repeat(Shell("white"), 64)
        ))
        inventory[Wampum.build(inventory)] += 1
        belt = Belt.build(inventory, maxlen=3)
        self.assertIsInstance(belt, Belt)
        self.assertTrue(hasattr(belt, "components"))
        self.assertTrue(hasattr(belt, "memory"))
        self.assertFalse(sum(inventory.values()), inventory)
        belt.memory.extend([None] * 4)
        self.assertEqual(3, len(belt.memory))

    def test_volume(self):
        inventory = Counter(itertools.chain(
            (String(1), ), itertools.repeat(Shell("white"), 64)
        ))
        w = Wampum.build(inventory)
        self.assertTrue(hasattr(w, "volume"))
        
