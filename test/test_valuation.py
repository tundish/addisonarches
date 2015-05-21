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

from tallywallet.common.finance import Note

from inventory import Asset
from scenario import Commodity
from scenario import Volume
from valuation import Bid
from valuation import ValueBook


class ValueBookTests(unittest.TestCase):

    def test_is_readonly(self):
        book = ValueBook()
        self.assertRaises(
            NotImplementedError, book.setdefault, "commodity"
        )
        self.assertRaises(
            NotImplementedError, book.update, {}
        )
        try:
            book["commodity"] = None
        except NotImplementedError:
            pass
        else:
            self.fail()

    def test_valuation_from_finance_note(self):
        then = datetime.date(2015, 4, 1)
        note = Note(
            date=then,
            principal=1500,
            currency="£",
            term=datetime.timedelta(days=30),
            interest=Decimal("0.050"),
            period=datetime.timedelta(days=5)
        )
        commodity = Commodity(
            "VCRs", "Betamax video cassette recorders", Volume.box
        )
        goods = Asset(commodity, 10, note.date)
        book = ValueBook()
        valuation = book.commit(commodity, note)
        self.assertEqual(
            Decimal("1823.26"), valuation.value.quantize(Decimal("0.01"))
        )
        self.assertEqual(1, len(book))
        self.assertEqual(
            note.term // note.period,
            len(book[commodity])
        )

    def test_valuation_from_offer(self):
        then = datetime.date(2015, 4, 1)
        commodity = Commodity(
            "VCRs", "Betamax video cassette recorders", Volume.box
        )
        goods = Asset(commodity, 10, then)
        book = ValueBook()
        offer = Bid(then, 1800, "£")
        self.assertRaises(KeyError, book.commit, commodity, offer)

    def test_mixed_currency(self):
        then = datetime.date(2015, 4, 1)
        note = Note(
            date=then,
            principal=1500,
            currency="£",
            term=datetime.timedelta(days=30),
            interest=Decimal("0.050"),
            period=datetime.timedelta(days=5)
        )
        commodity = Commodity(
            "VCRs", "Betamax video cassette recorders", Volume.box
        )
        goods = Asset(commodity, 10, note.date)
        book = ValueBook()
        book.commit(commodity, note)
        offer = Bid(then, 1200, "$")
        self.assertWarns(Warning, book.commit, commodity, offer)

    def test_offer_too_low(self):
        then = datetime.date(2015, 4, 1)
        note = Note(
            date=then,
            principal=1500,
            currency="£",
            term=datetime.timedelta(days=30),
            interest=Decimal("0.050"),
            period=datetime.timedelta(days=5)
        )
        commodity = Commodity(
            "VCRs", "Betamax video cassette recorders", Volume.box
        )
        goods = Asset(commodity, 10, note.date)
        book = ValueBook()
        book.commit(commodity, note)
        offer = Bid(then, 1200, "£")
        valuation = book.commit(commodity, offer)
        self.assertEqual(
            Decimal("1823.26"), valuation.value.quantize(Decimal("0.01"))
        )

    def test_simple_haggling(self):
        then = datetime.date(2015, 4, 1)
        note = Note(
            date=then,
            principal=1500,
            currency="£",
            term=datetime.timedelta(days=30),
            interest=Decimal("0.050"),
            period=datetime.timedelta(days=5)
        )
        commodity = Commodity(
            "VCRs", "Betamax video cassette recorders", Volume.box
        )
        goods = Asset(commodity, 10, note.date)
        book = ValueBook()
        book.commit(commodity, note)

        n = 0
        now = then
        offer = Bid(now, 1200, "£")
        valuation = book.consider(commodity, offer)
        while not book.approve(book[commodity], offer):
            n += 1
            now += datetime.timedelta(days=1)
            offer = Bid(
                now,
                offer.value + (valuation.value - offer.value) // 2,
                valuation.currency
            )
            valuation = book.consider(commodity, offer)

        self.assertEqual(3, n)

    def test_stubborn_haggling_under_constraint(self):
        then = datetime.date(2015, 4, 1)
        note = Note(
            date=then,
            principal=1500,
            currency="£",
            term=datetime.timedelta(days=30),
            interest=Decimal("0.050"),
            period=datetime.timedelta(days=5)
        )
        commodity = Commodity(
            "VCRs", "Betamax video cassette recorders", Volume.box
        )
        goods = Asset(commodity, 10, note.date)
        book = ValueBook()
        book.commit(commodity, note)

        n = 0
        now = then
        offer = Bid(now, 1200, "£")
        while not book.approve(book[commodity], offer):
            n += 1
            now += datetime.timedelta(days=1)
            valuation = book.consider(commodity, offer, constraint=1.0)

        self.assertEqual(4, n)
        self.assertEqual(1200, valuation.value)

    def test_stubborn_haggling_without_constraint(self):
        then = datetime.date(2015, 4, 1)
        note = Note(
            date=then,
            principal=1500,
            currency="£",
            term=datetime.timedelta(days=30),
            interest=Decimal("0.050"),
            period=datetime.timedelta(days=5)
        )
        commodity = Commodity(
            "VCRs", "Betamax video cassette recorders", Volume.box
        )
        goods = Asset(commodity, 10, note.date)
        book = ValueBook()
        book.commit(commodity, note)

        offer = Bid(then, 1200, "£")
        valuation = book.consider(commodity, offer, constraint=0)

        self.assertNotIn(1200, (i.value for i in book[commodity]))

    def test_quick_deal(self):
        then = datetime.date(2015, 4, 1)
        note = Note(
            date=then,
            principal=1500,
            currency="£",
            term=datetime.timedelta(days=30),
            interest=Decimal("0.050"),
            period=datetime.timedelta(days=5)
        )
        commodity = Commodity(
            "VCRs", "Betamax video cassette recorders", Volume.box
        )
        goods = Asset(commodity, 10, note.date)
        book = ValueBook()
        book.commit(commodity, note)

        now = then
        offer = Bid(now, 1800, "£")
        valuation = book.commit(commodity, offer)
        self.assertTrue(book.approve(book[commodity], offer))
