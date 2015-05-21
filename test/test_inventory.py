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

from inventory import Asset
from inventory import Business
from inventory import Inventory
import scenario
from scenario import Commodity
from scenario import Volume
from valuation import Ask
from valuation import ValueBook

from tallywallet.common.finance import Note


class BuyerTests(unittest.TestCase):

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


class GameTests(unittest.TestCase):

    def test_game_setup(self):
        then = datetime.date(2015, 4, 1)
        credit = (datetime.timedelta(days=30), Decimal("0.050"))
        harry = Business(
            scenario.characters[0],
            ValueBook(),
            scenario.locations[1:2],
            scenario.commodities[0:2]
        )
        self.assertIn(scenario.locations[1].name, harry.locations)
        self.assertEqual(0, harry.locations["Harry's House Clearances"].constraint)

        for commodity, offer, quantity in zip(
            harry.commodities,
            (Ask(then, 40, "£"), Ask(then, 600, "£")),
            (8, 1),
        ):
            note = Note(
                date=offer.ts,
                principal=offer.value,
                currency=offer.currency,
                term=credit[0],
                interest=credit[1],
                period=datetime.timedelta(days=5)
            )
            harry.book.commit(commodity, note)

            # Decide whether to add supply
            asset = Asset(commodity, quantity, note.date)

            # TODO: harry.store(asset)
            harry.locations["Harry's House Clearances"].contents[asset.commodity] += asset.quantity

        print(harry.book)
