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
import pickle
import tempfile
import unittest

from addisonarches.game import Game
from addisonarches.game import Persistent
import addisonarches.scenario


class PersistentTests(unittest.TestCase):

    user = "someone@somewhere.net"

    def make_home(self):
        path = Persistent.Path(self.root.name, PersistentTests.user, None, None)
        return Persistent.make_path(path)

    def make_slot(self):
        path = Persistent.Path(
            self.root.name, PersistentTests.user, None, "business.pkl")
        return Persistent.make_path(path)

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
        self.assertNotIn(path.root, path.slot)
        self.assertNotIn(path.root, path.file)
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
         
    def test_no_recent_slot(self):
        path = self.make_home()
        path = Persistent.recent_slot(path)
        self.assertIs(None, path.slot)
        path = path._replace(file="objects.pkl")
        path = Persistent.make_path(path)
         
    def test_recent_slot(self):
        path = self.make_slot()
        self.assertEqual(
            path.slot,
            Persistent.recent_slot(path).slot
        )
         
class GameTests(unittest.TestCase):

    user = "someone@somewhere.net"

    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.assertTrue(os.path.isdir(self.root.name))

    @unittest.skip("Can't pickle <class 'generator'>")
    def test_pickling_game(self):
        with self.root as root:
            path = os.path.join(root, "game.pkl")
            game = Game(businesses=addisonarches.scenario.businesses)
            with open(path, 'wb') as fObj:
                pickle.dump(game, fObj, 4)
        
    def test_pickling_businesses(self):
        options = Game.options(
            Game.Player(GameTests.user, "Player 1"),
            parent=self.root.name
        )
        game = Game(
            Game.Player(GameTests.user, "Player 1"),
            addisonarches.scenario.businesses,
            **options
        )
        game.load()
        game.declare({"businesses": True})
        #with self.root as root:
        #    path = os.path.join(root, "businesses.pkl")
        #    with open(path, 'wb') as fObj:
        #        pickle.dump(addisonarches.scenario.businesses, fObj, 4)
        
    def tearDown(self):
        if os.path.isdir(self.root.name):
            self.root.cleanup()
        self.assertFalse(os.path.isdir(self.root.name))
        self.root = None
