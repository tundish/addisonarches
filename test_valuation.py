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
import unittest

from tallywallet.common.finance import Note
from tallywallet.common.finance import value_series


Commodity = namedtuple("Commodity", ["label", "description"])
Asset = namedtuple(
    "Asset",
    ["commodity", "unit", "quantity", "acquired"]
)

Offer = namedtuple("Offer", ["ts"])
Valuation = namedtuple("Valuation", ["ts", "value", "currency"])

class ValueBook(dict):

    def commit(self, asset:Asset, obj:set([Note, Offer])):
        if isinstance(obj, Note):
            series = super().setdefault(
                asset.commodity,
                deque([Valuation(*i, currency=obj.currency)
                       for i in value_series(**vars(obj))],
                      maxlen=obj.term // obj.period)
            )
            rv = series[0]
        else:
            raise NotImplementedError
        return rv

    def __setitem__(self, key, value):
        raise NotImplementedError

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
        valuation = book.commit(goods, note)
        self.assertEqual(1575, valuation.value)
        self.assertEqual(1, len(book))
        self.assertEqual(
            note.term // note.period,
            len(book[commodity])
        )
