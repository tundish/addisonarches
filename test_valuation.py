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
from tallywallet.common.finance import value_simple


Commodity = namedtuple("Commodity", ["label", "description"])
Asset = namedtuple(
    "Asset",
    ["commodity", "unit", "quantity", "acquired"]
)

Offer = namedtuple("Offer", ["ts"])
Valuation = namedtuple("Valuation", ["ts"])

class ValueBook(dict):

    def commit(self, asset:Asset, obj:[Note, Offer]):
        """
        Valuation remains constant during duration of note.
        Then each Offer or Valuation modulates the mean of
        the series.
        """
        if isinstance(obj, Note):
            self.series = deque(maxlen=8)  # TODO: calculate maxlen
        else:
            raise NotImplementedError


class ValuationAPITests(unittest.TestCase):

    def test_class(self):
        then = datetime.date(2015, 4, 1)
        note = Note(
            date=then,
            principal=1500,
            currency="£",
            term=datetime.timedelta(days=30),
            interest=Decimal("0.20"),
            period=datetime.timedelta(days=30)
        )
        goods = Commodity("VCRs", "Betamax video cassette recorders")
        book = ValueBook()
        val = book.commit(Asset(goods, int, 10, note.date), note)
        #val = book.commit(Asset(goods, int, 10, note.date), Offer(..))
        self.fail(book)
        self.fail(value_simple(note))
