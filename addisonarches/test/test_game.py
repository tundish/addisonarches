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
import pickle


class GameTests(unittest.TestCase):

    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.assertTrue(os.path.isdir(self.root.name))

    def test_pickling_game(self):
        with self.root as root:
            path = os.path.join(root, "game.pkl")
            game = Game(businesses=addisonarches.scenario.businesses)
            with open(path, 'wb') as fObj:
                pickle.dump(game, fObj, 4)
                print(os.listdir(root))
        
    def test_pickling_businesses(self):
        with self.root as root:
            path = os.path.join(root, "businesses.pkl")
            with open(path, 'wb') as fObj:
                pickle.dump(addisonarches.scenario.businesses, fObj, 4)
                print(os.listdir(root))
        
    def tearDown(self):
        self.assertFalse(os.path.isdir(self.root.name))
        self.root = None

