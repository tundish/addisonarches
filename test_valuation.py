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

from collections import defaultdict
from collections import deque
from collections import namedtuple
import datetime
from decimal import Decimal
import functools
import random
import statistics
import unittest
import warnings

from tallywallet.common.finance import Note
from tallywallet.common.finance import value_series


Commodity = namedtuple("Commodity", ["label", "description"])
Asset = namedtuple(
    "Asset",
    ["commodity", "unit", "quantity", "acquired"]
)

Offer = namedtuple("Offer", ["ts", "value", "currency"])
Valuation = namedtuple("Valuation", ["ts", "value", "currency"])


class ValueBook(dict):
    """
    .. todo:: refactor methods to accept commodities

    """

    @staticmethod
    def approve(series, offer, **kwargs):
        sd = statistics.pstdev(i.value for i in series)
        estimate = ValueBook.estimate(series)
        return (offer.value > estimate.value
                or estimate.value - offer.value < sd / 2)

    @staticmethod
    def estimate(series):
        currencies = {i.currency for i in series}
        if len(currencies) > 1:
            warnings.warn("Mixed currencies ({})".format(currencies))
            return None
        else:
            return Valuation(
                None,
                statistics.median_high(i.value for i in series),
                currencies.pop()
            )

    def __setitem__(self, key, value):
        raise NotImplementedError

    def consider(self, commodity:Commodity, offer:Offer, constraint=1.0):
        estimate = self.estimate(self[commodity])
        if offer.value > estimate.value or random.random() <= constraint:
            return self.commit(commodity, offer)
        else:
            return estimate

    def commit(self, commodity:Commodity, obj:set([Note, Offer])):
        if isinstance(obj, Note):
            series = super().setdefault(
                commodity,
                deque([Valuation(*i, currency=obj.currency)
                       for i in value_series(**vars(obj))],
                      maxlen= obj.term // obj.period)
            )
        elif isinstance(obj, Offer):
            series = self[commodity]
            series.append(obj)
        else:
            raise NotImplementedError

        return self.estimate(series)

    def setdefault(self, key, default=None):
        raise NotImplementedError

    def update(self, other):
        raise NotImplementedError


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
            "VCRs", "Betamax video cassette recorders"
        )
        goods = Asset(commodity, int, 10, note.date)
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
            "VCRs", "Betamax video cassette recorders"
        )
        goods = Asset(commodity, int, 10, then)
        book = ValueBook()
        offer = Offer(then, 1800, "£")
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
            "VCRs", "Betamax video cassette recorders"
        )
        goods = Asset(commodity, int, 10, note.date)
        book = ValueBook()
        book.commit(commodity, note)
        offer = Offer(then, 1200, "$")
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
            "VCRs", "Betamax video cassette recorders"
        )
        goods = Asset(commodity, int, 10, note.date)
        book = ValueBook()
        book.commit(commodity, note)
        offer = Offer(then, 1200, "£")
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
            "VCRs", "Betamax video cassette recorders"
        )
        goods = Asset(commodity, int, 10, note.date)
        book = ValueBook()
        book.commit(commodity, note)

        n = 0
        now = then
        offer = Offer(now, 1200, "£")
        valuation = book.consider(commodity, offer)
        while not book.approve(book[commodity], offer):
            n += 1
            now += datetime.timedelta(days=1)
            offer = Offer(
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
            "VCRs", "Betamax video cassette recorders"
        )
        goods = Asset(commodity, int, 10, note.date)
        book = ValueBook()
        book.commit(commodity, note)

        n = 0
        now = then
        offer = Offer(now, 1200, "£")
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
            "VCRs", "Betamax video cassette recorders"
        )
        goods = Asset(commodity, int, 10, note.date)
        book = ValueBook()
        book.commit(commodity, note)

        offer = Offer(then, 1200, "£")
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
            "VCRs", "Betamax video cassette recorders"
        )
        goods = Asset(commodity, int, 10, note.date)
        book = ValueBook()
        book.commit(commodity, note)

        now = then
        offer = Offer(now, 1800, "£")
        valuation = book.commit(commodity, offer)
        self.assertTrue(book.approve(book[commodity], offer))
