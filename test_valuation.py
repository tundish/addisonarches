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

from collections import deque
from collections import namedtuple
import datetime
from decimal import Decimal
import unittest

from tallywallet.common.finance import Note


Asset = namedtuple("Asset", ["quantity", "acquired"])
Valuation = namedtuple("Valuation", [])

class Valuation:

    def __init__(self, note):
        """
        Valuation remains constant during duration of note.
        Then each Offer or Valuation modulates the mean of
        the series.
        """
        self.note = note
        self.series = deque(maxlen=8)  # TODO: calculate maxlen


class ValuationAPITests(unittest.TestCase):

    def test_class(self):
        note = Note(
            date=datetime.date(1995, 5, 11),
            principal=1500,
            currency=None,
            term=datetime.timedelta(days=90),
            interest=Decimal("0.08"),
            period=datetime.timedelta(days=360)
        )
        self.fail(note)
