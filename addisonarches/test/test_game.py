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

import os.path
import tempfile
import unittest

from addisonarches.game import Game
import addisonarches.scenario

#prototyping
from collections import namedtuple
import pickle
import tempfile


Path = namedtuple("Path", ["root", "home", "slot", "file"])

def make_path(path:Path, prefix="tmp", suffix=""):
    if path.slot is None:
        dctry = os.path.join(path.root, path.home)
        try:
            os.mkdir(dctry)
        except FileExistsError:
            pass
        if path.file is not None:
            slot = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dctry)
            return path._replace(slot=slot)
        else:
            return path
    else:
        return None

class PathTests(unittest.TestCase):

    user = "someone@somewhere.net"

    def make_home(self):
        path = Path(self.root.name, PathTests.user, None, None)
        return make_path(path)

    def make_slot(self):
        path = Path(self.root.name, PathTests.user, None, "business.pkl")
        return make_path(path)

    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.assertTrue(os.path.isdir(self.root.name))

    def tearDown(self):
        if os.path.isdir(self.root.name):
            self.root.cleanup()
        self.assertFalse(os.path.isdir(self.root.name))
        self.root = None

    def test_make_home(self):
        path = self.make_home()
        self.assertTrue(path)
        self.assertTrue(path.root)
        self.assertTrue(path.home)
        self.assertFalse(path.slot)
        self.assertFalse(path.file)
        self.assertTrue(
            os.path.isdir(os.path.join(*(i for i in path if i is not None)))
        )
 
    def test_make_home_twice(self):
        first = self.make_home()
        path = self.make_home()
        self.assertEqual(first, path)
        self.assertTrue(path)
        self.assertTrue(path.root)
        self.assertTrue(path.home)
        self.assertFalse(path.slot)
        self.assertFalse(path.file)
        self.assertTrue(
            os.path.isdir(os.path.join(*(i for i in path if i is not None)))
        )
    
    def test_make_slot(self):
        path = self.make_slot()
        self.assertTrue(path)
        self.assertTrue(path.root)
        self.assertTrue(path.home)
        self.assertTrue(path.slot)
        self.assertTrue(path.file)
        self.assertTrue(
            os.path.isdir(os.path.join(*path[:-1]))
        )
         
    def test_make_slot_twice(self):
        first = self.make_slot()
        path = self.make_slot()
        self.assertNotEqual(first, path)
        self.assertTrue(path)
        self.assertTrue(path.root)
        self.assertTrue(path.home)
        self.assertTrue(path.slot)
        self.assertTrue(path.file)
        self.assertTrue(
            os.path.isdir(os.path.join(*path[:-1]))
        )
         
class GameTests(unittest.TestCase):

    user = "someone@somewhere.net"

    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.assertTrue(os.path.isdir(self.root.name))
        self.home = os.path.join(self.root.name, GameTests.user)
        os.mkdir(self.home)

    @unittest.skip("Can't pickle <class 'generator'>")
    def test_pickling_game(self):
        with self.root as root:
            path = os.path.join(root, "game.pkl")
            game = Game(businesses=addisonarches.scenario.businesses)
            with open(path, 'wb') as fObj:
                pickle.dump(game, fObj, 4)
        
    def test_pickling_businesses(self):
        with self.root as root:
            path = os.path.join(root, "businesses.pkl")
            with open(path, 'wb') as fObj:
                pickle.dump(addisonarches.scenario.businesses, fObj, 4)
        
    def tearDown(self):
        self.assertFalse(os.path.isdir(self.root.name))
        self.root = None

