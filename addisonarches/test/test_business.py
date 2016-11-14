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

from addisonarches.business import Asset
from addisonarches.business import Business
from addisonarches.inventory import Volume
import addisonarches.scenario.common
from addisonarches.scenario.types import Commodity
from addisonarches.valuation import Valuation
from addisonarches.valuation import ValueBook

from tallywallet.common.finance import Note

from turberfield.utils.assembly import Assembly


class SerialisationTests(unittest.TestCase):

    def test_commodity_roundtrip(self):
        now = datetime.date(2015, 4, 1)
        commodity = Commodity("Bricks", "Reclaimed London clay bricks", Volume.load)
        text = Assembly.dumps(commodity)
        rv = Assembly.loads(text)
        self.assertEqual(commodity, rv)

    def test_roundtrip_volume(self):
        volume =  Volume.load
        text = Assembly.dumps(volume)
        rv = Assembly.loads(text)
        self.assertEqual(volume, rv)

class BusinessTests(unittest.TestCase):
    commodities = [
        Commodity("Desk", "Self-assembly beech effect office desk", Volume.box),
        Commodity("Desk", "Antique mahogany campaign desk", Volume.load),
        Commodity("Bricks", "Reclaimed London clay bricks", Volume.load),
        Commodity("Topsoil", "Finest growing medium from Norfolk", Volume.heap),
        Commodity("VCRs", "Betamax video cassette recorders", Volume.box),
        Commodity("PVRs", "Freeview HD recorders with dual HDMI", Volume.box),
    ]

    def setUp(self):
        then = datetime.date(2015, 4, 1)
        credit = (datetime.timedelta(days=30), Decimal("0.050"))
        self.business = harry = Business(
            addisonarches.scenario.common.characters[0],
            ValueBook(),
            addisonarches.scenario.common.locations[1:2],
        )
        self.assertIn(
            addisonarches.scenario.common.locations[1].name,
            harry.inventories
        )
        self.assertEqual(
            0, harry.inventories["Harry's House Clearances"].constraint
        )

        for commodity, offer, quantity in zip(
            BusinessTests.commodities[0:2],
            (Valuation(then, 40, "£"), Valuation(then, 600, "£")),
            (0, 1),
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

    def test_single_inventory_population(self):
        now = datetime.date(2015, 4, 1)
        commodity = BusinessTests.commodities[1]
        asset = Asset(commodity, 3, now)
        drop = self.business.store(asset)
        self.assertIn(("Harry's House Clearances", 3), drop)
        self.assertEqual(
            3,
            self.business.inventories["Harry's House Clearances"].contents[commodity]
        )

    def test_single_inventory_emptying(self):
        self.test_single_inventory_population()
        now = datetime.date(2015, 4, 1)
        commodity = BusinessTests.commodities[1]
        asset = Asset(commodity, 3, now)
        pick = self.business.retrieve(asset)
        self.assertIn(("Harry's House Clearances", 3), pick)
        self.assertEqual(
            0,
            self.business.inventories["Harry's House Clearances"].contents[commodity]
        )

    def test_single_inventory_overemptying(self):
        self.test_single_inventory_population()
        now = datetime.date(2015, 4, 1)
        commodity = BusinessTests.commodities[1]
        asset = Asset(commodity, 4, now)
        pick = self.business.retrieve(asset)
        self.assertIn(("Harry's House Clearances", 3), pick)
        self.assertEqual(
            0,
            self.business.inventories["Harry's House Clearances"].contents[commodity]
        )

    def test_single_inventory_picking(self):
        self.test_single_inventory_population()
        now = datetime.date(2015, 4, 1)
        commodity = BusinessTests.commodities[1]
        asset = Asset(commodity, 1, now)
        pick = self.business.retrieve(asset)
        self.assertIn(("Harry's House Clearances", 1), pick)
        self.assertEqual(
            2,
            self.business.inventories["Harry's House Clearances"].contents[commodity]
        )

    def test_store_integer_volume(self):
        self.test_single_inventory_population()
        now = datetime.date(2015, 4, 1)
        thing = Commodity(
            "thing", "one metre cubed ", 1)
        asset = Asset(thing, 1, now)
        drop = self.business.store(asset)
        self.assertIn(("Harry's House Clearances", 1), drop)
        self.assertEqual(
            1,
            self.business.inventories[
                "Harry's House Clearances"
            ].contents[thing]
        )
        pick = self.business.retrieve(asset)
        self.assertIn(("Harry's House Clearances", 1), pick)
        self.assertEqual(
            0,
            self.business.inventories[
                "Harry's House Clearances"
            ].contents[thing]
        )

    def test_store_zero_volume(self):
        self.test_single_inventory_population()
        now = datetime.date(2015, 4, 1)
        cloud = Commodity(
            "cloud", "nebulous and insubstantial", 0)
        asset = Asset(cloud, 1, now)
        drop = self.business.store(asset)
        self.assertIn(("Harry's House Clearances", 1), drop)
        self.assertEqual(
            1,
            self.business.inventories[
                "Harry's House Clearances"
            ].contents[cloud]
        )
        pick = self.business.retrieve(asset)
        self.assertIn(("Harry's House Clearances", 1), pick)
        self.assertEqual(
            0,
            self.business.inventories[
                "Harry's House Clearances"
            ].contents[cloud]
        )
