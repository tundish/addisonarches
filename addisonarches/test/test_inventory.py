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

import datetime
from decimal import Decimal
import unittest

from addisonarches.inventory import Inventory
from addisonarches.inventory import Volume
from addisonarches.scenario import Commodity

from tallywallet.common.finance import Note


class InventoryTests(unittest.TestCase):

    def test_capacity_constraint(self):
        inv = Inventory(capacity=12 * Volume.cubic_metre.value)
        self.assertEqual(0, inv.constraint)

        inv.contents[
            Commodity("Topsoil", "Finest growing medium from Norfolk", Volume.heap)
        ] += 9
        self.assertEqual(0.75, inv.constraint)

        inv.contents[
            Commodity("Topsoil", "Finest growing medium from Norfolk", Volume.heap)
        ] -= 3
        self.assertEqual(0.5, inv.constraint)

        inv.contents[
            Commodity("Bricks", "Reclaimed London clay bricks", Volume.load)
        ] += 3
        self.assertEqual(1, inv.constraint)
